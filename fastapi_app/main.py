from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import re
from datetime import datetime
from collections import Counter
from typing import Dict, List, Any
from data_processor import DataProcessor, convert_types
from sentiment_processor import SentimentProcessor
from topic_pillar_processor import analyze_topic_pillars, get_post_detail
from recommendation_processor import RecommendationProcessor
import os
import shutil
from pathlib import Path

app = FastAPI(title="Social Media Analytics API")

# Initialize Sentiment Processor
MODEL_PATH = "/home/dimas/crawling_sosmed/assets/model/LinearSVM.pkl"
VECTORIZER_PATH = "/home/dimas/crawling_sosmed/assets/model/tfidf_vectorizer.pkl"
sentiment_processor = None

@app.on_event("startup")
def load_sentiment_processor():
    """Initialize SentimentProcessor at startup"""
    global sentiment_processor
    try:
        sentiment_processor = SentimentProcessor(
            model_path=MODEL_PATH,
            vectorizer_path=VECTORIZER_PATH
        )
        print("✓ SentimentProcessor initialized successfully")
    except Exception as e:
        print(f"✗ Error initializing SentimentProcessor: {e}")
        sentiment_processor = None

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_PATH = "/home/dimas/crawling_sosmed/tweets-data"

# Create datasets directory structure
DATASETS_PATH = f"{DATA_PATH}/datasets"
os.makedirs(DATASETS_PATH, exist_ok=True)
os.makedirs(f"{DATASETS_PATH}/default", exist_ok=True)

# Global variable to track active dataset
ACTIVE_DATASET = "default"

# create a shared data processor instance
dp = DataProcessor(DATA_PATH)

def get_active_dataset_path():
    """Get the file paths for the currently active dataset"""
    global ACTIVE_DATASET

    if ACTIVE_DATASET == "default":
        # Use base data from root DATA_PATH
        return {
            "tweet_file": f"{DATA_PATH}/tweet.xlsx",
            "replies_file": f"{DATA_PATH}/replies.csv",
            "dataset_name": "default"
        }
    else:
        # Use dataset from datasets folder
        dataset_path = f"{DATASETS_PATH}/{ACTIVE_DATASET}"
        return {
            "tweet_file": f"{dataset_path}/tweet.xlsx",
            "replies_file": f"{dataset_path}/replies.csv",
            "dataset_name": ACTIVE_DATASET
        }

@app.get("/")
def read_root():
    return {"message": "FastAPI Analytics API Ready"}

@app.get("/api/basic-stats")
def get_basic_stats():
    """Get basic statistics from tweet data"""
    try:
        dataset_paths = get_active_dataset_path()
        df_tweets = pd.read_excel(dataset_paths['tweet_file'], header=4)

        stats = {
            "total_posts": int(len(df_tweets)),
            "total_replies": int(df_tweets['Replies'].sum()),
            "total_likes": int(df_tweets['Likes'].sum()),
            "total_retweets": int(df_tweets['Retweets'].sum()),
            "total_mentions": int(df_tweets['Replies'].sum() + df_tweets['Likes'].sum() + df_tweets['Retweets'].sum()),
            "active_dataset": dataset_paths['dataset_name']
        }
        return convert_types(stats)
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/engagement-by-type")
def get_engagement_by_type():
    """Get engagement distribution by post type"""
    try:
        dataset_paths = get_active_dataset_path()
        df_tweets = pd.read_excel(dataset_paths['tweet_file'], header=4)
        
        # Calculate engagement per post type
        type_engagement = df_tweets.groupby('Type')[['Likes', 'Replies', 'Retweets']].sum().reset_index()
        type_engagement['Total'] = type_engagement['Likes'] + type_engagement['Replies'] + type_engagement['Retweets']
        
        result = []
        for idx, row in type_engagement.iterrows():
            result.append({
                "type": row['Type'],
                "likes": int(row['Likes']),
                "replies": int(row['Replies']),
                "retweets": int(row['Retweets']),
                "total": int(row['Total'])
            })
        return convert_types(result)
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/peak-hours")
def get_peak_hours():
    """Get peak activity hours using DBSCAN clustering"""
    try:
        import os
        
        replies_files = [f for f in os.listdir(DATA_PATH) if f.endswith('_replies.csv')]
        
        if not replies_files:
            return {"error": "No replies data found"}
        
        all_hours = []
        for file in replies_files:
            try:
                df_replies = pd.read_csv(f"{DATA_PATH}/{file}")
                if 'created_at' in df_replies.columns:
                    # Parse hours from created_at
                    for date_str in df_replies['created_at']:
                        try:
                            # Example: "Sat Nov 15 23:59:58 +0000 2025"
                            dt = datetime.strptime(date_str.replace('+0000', '').strip(), "%a %b %d %H:%M:%S %Y")
                            all_hours.append(dt.hour)
                        except:
                            pass
            except:
                pass
        
        if not all_hours:
            return {"error": "No time data available"}
        
        # Prepare data for DBSCAN
        X = np.array(all_hours).reshape(-1, 1)
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Apply DBSCAN
        dbscan = DBSCAN(eps=0.5, min_samples=5)
        labels = dbscan.fit_predict(X_scaled)
        
        # Find non-outlier hours
        non_outliers = X[labels != -1]
        
        if len(non_outliers) > 0:
            peak_hours = {
                "min_hour": int(np.min(non_outliers)),
                "max_hour": int(np.max(non_outliers)),
                "mean_hour": float(np.mean(non_outliers)),
                "count": int(len(non_outliers))
            }
        else:
            peak_hours = {"error": "Could not identify peak hours"}
        
        return convert_types(peak_hours)
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/hashtags")
def get_popular_hashtags():
    """Extract and return most popular hashtags"""
    try:
        df_tweets = pd.read_excel(f"{DATA_PATH}/tweet.xlsx", header=4)
        
        hashtags = []
        for caption in df_tweets['Caption']:
            if pd.notna(caption):
                # Extract hashtags
                found_tags = re.findall(r'#\w+', str(caption))
                hashtags.extend(found_tags)
        
        # Count and get top 10
        hashtag_counts = Counter(hashtags)
        top_hashtags = hashtag_counts.most_common(10)
        
        result = [{"hashtag": tag, "count": int(count)} for tag, count in top_hashtags]
        return convert_types(result)
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/engagement-by-day")
def get_engagement_by_day():
    """Get engagement by day of week"""
    try:
        df_tweets = pd.read_excel(f"{DATA_PATH}/tweet.xlsx", header=4)
        
        # Parse dates and calculate engagement
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_engagement = {day: 0 for day in day_names}
        
        for date_str in df_tweets['Date']:
            try:
                dt = pd.to_datetime(date_str)
                day_name = day_names[dt.dayofweek]
                day_engagement[day_name] += 1
            except:
                pass
        
        result = [{"day": day, "engagement": engagement} for day, engagement in day_engagement.items()]
        return convert_types(result)
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/clustering-pca")
def get_clustering_pca():
    """Get PCA clustering visualization data"""
    try:
        import os
        
        replies_files = [f for f in os.listdir(DATA_PATH) if f.endswith('_replies.csv')]
        
        if not replies_files:
            return {"error": "No replies data found"}
        
        all_data = []
        for file in replies_files:
            try:
                df = pd.read_csv(f"{DATA_PATH}/{file}")
                if len(df) > 0:
                    # Calculate engagement metrics per record
                    for idx, row in df.iterrows():
                        if 'created_at' in df.columns:
                            try:
                                dt = datetime.strptime(row['created_at'].replace('+0000', '').strip(), "%a %b %d %H:%M:%S %Y")
                                hour = dt.hour
                                all_data.append([hour, idx])
                            except:
                                pass
            except:
                pass
        
        if len(all_data) < 2:
            return {"error": "Insufficient data for PCA"}
        
        X = np.array(all_data)
        
        # Apply DBSCAN first
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        dbscan = DBSCAN(eps=0.5, min_samples=3)
        clusters = dbscan.fit_predict(X_scaled)
        
        # Apply PCA
        pca = PCA(n_components=2)
        X_pca = pca.fit_transform(X_scaled)
        
        result = {
            "points": [
                {"x": float(x), "y": float(y), "cluster": int(c)}
                for x, y, c in zip(X_pca[:, 0], X_pca[:, 1], clusters)
            ],
            "explained_variance": [float(v) for v in pca.explained_variance_ratio_],
            "n_clusters": len(set(clusters)) - (1 if -1 in clusters else 0)
        }
        return convert_types(result)
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/peak-activity-hours")
def get_peak_activity_hours_detailed():
    """Get detailed peak activity hours analysis with DBSCAN clustering and PCA visualization"""
    try:
        result = dp.get_peak_activity_hours()
        return result
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/sentiment-analysis")
def get_sentiment_analysis():
    """Comprehensive sentiment analysis dengan LinearSVM model dan LDA topic modeling"""
    global sentiment_processor

    try:
        # Check if sentiment processor is initialized
        if sentiment_processor is None:
            return {"error": "SentimentProcessor not initialized"}

        # Load replies data
        df = pd.read_csv(f"{DATA_PATH}/replies.csv")

        # Analyze sentiment using SentimentProcessor
        df = sentiment_processor.analyze_dataframe(df, text_column='full_text')

        # Generate comprehensive report
        report = sentiment_processor.generate_sentiment_report(df)

        # Update metadata dengan data source
        report['metadata']['data_source'] = 'replies.csv'

        return convert_types(report)

    except Exception as e:
        return {"error": str(e)}


@app.get("/api/emotion-analysis")
def get_emotion_analysis():
    """Comprehensive emotion analysis dengan rule-based lexicon approach"""
    try:
        from emotion_processor import EmotionProcessor

        # Initialize emotion processor
        emotion_processor = EmotionProcessor()

        # Load replies data
        df = pd.read_csv(f"{DATA_PATH}/replies.csv")

        # Analyze emotion
        df = emotion_processor.analyze_dataframe(df, text_column='full_text')

        # Generate comprehensive report
        report = emotion_processor.generate_emotion_report(df)

        # Update metadata
        report['metadata']['data_source'] = 'replies.csv'

        return convert_types(report)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

@app.get("/api/analytics")
def get_analytics():
    """Combined analytics payload for frontend consumption (processed in Python)."""
    try:
        basic = dp.get_statistics_with_delta()
        by_type = dp.get_engagement_by_type()
        hashtags = dp.get_top_hashtags()
        by_day = dp.get_engagement_by_day()

        # peak hours and clustering use replies CSVs and are already implemented
        peak = get_peak_hours()

        # Get detailed peak activity hours with clustering
        peak_activity = dp.get_peak_activity_hours()

        payload = {
            "basic": basic,
            "engagement_by_type": by_type,
            "hashtags": hashtags,
            # convert day dict to list for stable ordering in frontend
            "engagement_by_day": [
                {"day": k, "engagement": v} for k, v in by_day.items()
            ],
            "peak_hours": peak,
            "peak_activity_hours": peak_activity,
        }

        return convert_types(payload)
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/topic-pillars")
def get_topic_pillars():
    """Topic Pillar Analysis dengan LDA topic modeling"""
    try:
        # Path to tweet.xlsx
        tweet_file = f"{DATA_PATH}/tweet.xlsx"

        # Perform topic pillar analysis
        result = analyze_topic_pillars(tweet_file)

        return convert_types(result)

    except Exception as e:
        return {"error": str(e)}


@app.get("/api/post-detail")
def get_post_detail_api(permalink: str):
    """Get detailed information for a specific post including hashtags and reply word cloud"""
    try:
        # Path to tweet.xlsx
        tweet_file = f"{DATA_PATH}/tweet.xlsx"

        # Get post detail
        result = get_post_detail(tweet_file, permalink)

        return convert_types(result)

    except Exception as e:
        return {"error": str(e)}


@app.get("/api/data-status")
def get_data_status():
    """Check status data dan kesiapan platform"""
    try:
        # Check default (base) data
        tweet_exists = os.path.exists(f"{DATA_PATH}/tweet.xlsx")
        replies_exists = os.path.exists(f"{DATA_PATH}/replies.csv")

        # Get file stats for base data
        file_stats = {}
        if tweet_exists:
            try:
                df_tweets = pd.read_excel(f"{DATA_PATH}/tweet.xlsx", header=4)
                file_stats['total_tweets'] = len(df_tweets)
            except Exception:
                file_stats['total_tweets'] = None

        if replies_exists:
            try:
                df_replies = pd.read_csv(f"{DATA_PATH}/replies.csv")
                file_stats['total_replies'] = len(df_replies)
            except Exception:
                file_stats['total_replies'] = None

        # Get all available datasets
        datasets_list = []
        try:
            list_result = list_datasets()
            if list_result.get('success'):
                datasets_list = list_result.get('datasets', [])
        except:
            pass

        return convert_types({
            'data_ready': tweet_exists and replies_exists,
            'tweet_xlsx_exists': tweet_exists,
            'replies_csv_exists': replies_exists,
            'file_stats': file_stats,
            'active_dataset': ACTIVE_DATASET,
            'total_datasets': len(datasets_list),
            'datasets': datasets_list,
            'data_path': DATA_PATH
        })
    except Exception as e:
        return {"error": str(e)}


@app.post("/api/upload-dataset")
async def upload_dataset(
    dataset_name: str = Form(...),
    tweet_file: UploadFile = File(...),
    replies_file: UploadFile = File(...)
):
    """
    Upload new dataset (tweet.xlsx and replies.csv)
    Creates a new dataset without overwriting the base data

    Args:
        dataset_name: Name for the new dataset (e.g., "dataset_1", "campaign_2024", etc.)
        tweet_file: Excel file with tweets
        replies_file: CSV file with replies
    """
    try:
        # Validate dataset name (alphanumeric and underscore only)
        if not re.match(r'^[a-zA-Z0-9_]+$', dataset_name):
            raise HTTPException(status_code=400, detail="Dataset name must contain only letters, numbers, and underscores")

        # Prevent overwriting default dataset
        if dataset_name.lower() == "default":
            raise HTTPException(status_code=400, detail="Cannot use 'default' as dataset name. This is reserved for base data.")

        # Create dataset directory
        dataset_dir = f"{DATASETS_PATH}/{dataset_name}"
        os.makedirs(dataset_dir, exist_ok=True)

        # Validate tweet file
        if not tweet_file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="Tweet file must be Excel format (.xlsx or .xls)")

        # Validate replies file
        if not replies_file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Replies file must be CSV format (.csv)")

        # Upload tweet file
        tweet_path = f"{dataset_dir}/tweet.xlsx"
        with open(tweet_path, "wb") as buffer:
            shutil.copyfileobj(tweet_file.file, buffer)

        # Validate tweet file can be read
        df_tweets = pd.read_excel(tweet_path, header=4)

        # Upload replies file
        replies_path = f"{dataset_dir}/replies.csv"
        with open(replies_path, "wb") as buffer:
            shutil.copyfileobj(replies_file.file, buffer)

        # Validate replies file can be read
        df_replies = pd.read_csv(replies_path)

        return {
            "success": True,
            "message": f"Dataset '{dataset_name}' created successfully",
            "dataset_name": dataset_name,
            "total_tweets": len(df_tweets),
            "total_replies": len(df_replies),
            "note": "Base data (default) remains unchanged. Switch to this dataset to analyze it."
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/select-dataset/{dataset_name}")
def select_dataset(dataset_name: str):
    """
    Select which dataset to use for analysis

    Args:
        dataset_name: Name of dataset to activate ("default" for base data, or any uploaded dataset name)
    """
    global ACTIVE_DATASET

    try:
        if dataset_name == "default":
            # Check if default dataset exists
            if not os.path.exists(f"{DATA_PATH}/tweet.xlsx") or not os.path.exists(f"{DATA_PATH}/replies.csv"):
                raise HTTPException(status_code=404, detail="Default dataset not found")

            ACTIVE_DATASET = "default"

            # Get stats
            df_tweets = pd.read_excel(f"{DATA_PATH}/tweet.xlsx", header=4)
            df_replies = pd.read_csv(f"{DATA_PATH}/replies.csv")

            return {
                "success": True,
                "message": "Switched to default (base) dataset",
                "active_dataset": "default",
                "total_tweets": len(df_tweets),
                "total_replies": len(df_replies)
            }
        else:
            # Check if dataset exists
            dataset_dir = f"{DATASETS_PATH}/{dataset_name}"
            if not os.path.exists(dataset_dir):
                raise HTTPException(status_code=404, detail=f"Dataset '{dataset_name}' not found")

            tweet_file = f"{dataset_dir}/tweet.xlsx"
            replies_file = f"{dataset_dir}/replies.csv"

            if not os.path.exists(tweet_file) or not os.path.exists(replies_file):
                raise HTTPException(status_code=404, detail=f"Dataset '{dataset_name}' is incomplete (missing files)")

            ACTIVE_DATASET = dataset_name

            # Get stats
            df_tweets = pd.read_excel(tweet_file, header=4)
            df_replies = pd.read_csv(replies_file)

            return {
                "success": True,
                "message": f"Switched to dataset '{dataset_name}'",
                "active_dataset": dataset_name,
                "total_tweets": len(df_tweets),
                "total_replies": len(df_replies)
            }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/list-datasets")
def list_datasets():
    """
    List all available datasets (default + uploaded datasets)
    """
    try:
        datasets = []

        # Add default dataset if exists
        if os.path.exists(f"{DATA_PATH}/tweet.xlsx") and os.path.exists(f"{DATA_PATH}/replies.csv"):
            df_tweets = pd.read_excel(f"{DATA_PATH}/tweet.xlsx", header=4)
            df_replies = pd.read_csv(f"{DATA_PATH}/replies.csv")

            datasets.append({
                "name": "default",
                "display_name": "Default (Base Data)",
                "total_tweets": len(df_tweets),
                "total_replies": len(df_replies),
                "is_active": ACTIVE_DATASET == "default"
            })

        # Add uploaded datasets
        if os.path.exists(DATASETS_PATH):
            for dataset_name in os.listdir(DATASETS_PATH):
                dataset_dir = f"{DATASETS_PATH}/{dataset_name}"
                if os.path.isdir(dataset_dir) and dataset_name != "default":
                    tweet_file = f"{dataset_dir}/tweet.xlsx"
                    replies_file = f"{dataset_dir}/replies.csv"

                    if os.path.exists(tweet_file) and os.path.exists(replies_file):
                        try:
                            df_tweets = pd.read_excel(tweet_file, header=4)
                            df_replies = pd.read_csv(replies_file)

                            # Get creation time
                            created_at = datetime.fromtimestamp(os.path.getctime(dataset_dir)).isoformat()

                            datasets.append({
                                "name": dataset_name,
                                "display_name": dataset_name.replace("_", " ").title(),
                                "total_tweets": len(df_tweets),
                                "total_replies": len(df_replies),
                                "created_at": created_at,
                                "is_active": ACTIVE_DATASET == dataset_name
                            })
                        except Exception as e:
                            print(f"Error reading dataset {dataset_name}: {e}")
                            continue

        return {
            "success": True,
            "active_dataset": ACTIVE_DATASET,
            "total_datasets": len(datasets),
            "datasets": datasets
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/delete-dataset/{dataset_name}")
def delete_dataset(dataset_name: str):
    """
    Delete an uploaded dataset
    Cannot delete the default dataset
    """
    global ACTIVE_DATASET

    try:
        if dataset_name == "default":
            raise HTTPException(status_code=400, detail="Cannot delete default dataset")

        dataset_dir = f"{DATASETS_PATH}/{dataset_name}"
        if not os.path.exists(dataset_dir):
            raise HTTPException(status_code=404, detail=f"Dataset '{dataset_name}' not found")

        # If deleting active dataset, switch to default
        if ACTIVE_DATASET == dataset_name:
            ACTIVE_DATASET = "default"

        # Delete dataset directory
        shutil.rmtree(dataset_dir)

        return {
            "success": True,
            "message": f"Dataset '{dataset_name}' deleted successfully",
            "active_dataset": ACTIVE_DATASET
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/recommendations")
def get_recommendations():
    """
    Generate automated insights and actionable recommendations based on:
    - Sentiment analysis
    - Emotion analysis
    - Topic pillars
    - Engagement patterns
    - Peak hour activity
    """
    try:
        from emotion_processor import EmotionProcessor

        # Initialize processors
        emotion_processor = EmotionProcessor()
        recommendation_processor = RecommendationProcessor()

        # Load data from active dataset
        dataset_paths = get_active_dataset_path()
        df_replies = pd.read_csv(dataset_paths['replies_file'])
        tweet_file = dataset_paths['tweet_file']

        # Get sentiment analysis data
        if sentiment_processor is not None:
            df_sentiment = sentiment_processor.analyze_dataframe(df_replies, text_column='full_text')
            sentiment_data = sentiment_processor.generate_sentiment_report(df_sentiment)
        else:
            sentiment_data = {}

        # Get emotion analysis data
        df_emotion = emotion_processor.analyze_dataframe(df_replies, text_column='full_text')
        emotion_data = emotion_processor.generate_emotion_report(df_emotion)

        # Get topic pillar data
        topic_data = analyze_topic_pillars(tweet_file)

        # Get engagement data
        engagement_data = dp.get_statistics_with_delta()

        # Get peak hours data
        peak_hours_data = dp.get_peak_activity_hours()

        # Generate recommendations
        result = recommendation_processor.generate_recommendations(
            sentiment_data=sentiment_data,
            emotion_data=emotion_data,
            topic_data=topic_data,
            engagement_data=engagement_data,
            peak_hours_data=peak_hours_data
        )

        # Add metadata
        result['metadata'] = {
            'data_source': 'replies.csv + tweet.xlsx',
            'generated_at': datetime.now().isoformat(),
            'analysis_types': ['sentiment', 'emotion', 'topics', 'engagement', 'timing']
        }

        return convert_types(result)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

