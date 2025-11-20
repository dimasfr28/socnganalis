"""
Utility functions for data processing and analytics
"""
import pandas as pd
import numpy as np
from datetime import datetime
import re
from collections import Counter
from typing import List, Dict, Any
from sklearn.cluster import DBSCAN
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler


def convert_types(obj):
    """Convert numpy types to Python native types for JSON serialization"""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, dict):
        return {k: convert_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_types(item) for item in obj]
    return obj

class DataProcessor:
    """Data processing utilities for analytics"""
    
    def __init__(self, data_path: str = "/home/dimas/crawling_sosmed/tweets-data"):
        self.data_path = data_path
    
    def load_tweet_data(self) -> pd.DataFrame:
        """Load tweet data from Excel"""
        try:
            return pd.read_excel(f"{self.data_path}/tweet.xlsx", header=4)
        except Exception as e:
            print(f"Error loading tweet data: {e}")
            return pd.DataFrame()
    def load_replies_csv(self) -> pd.DataFrame:
        """Load replies data from CSV (replies.csv)"""
        try:
            return pd.read_csv(f"{self.data_path}/replies.csv")
        except Exception as e:
            print(f"Error loading replies CSV: {e}")
            return pd.DataFrame()
    
    def load_replies_data(self, filename: str) -> pd.DataFrame:
        """Load replies data from CSV"""
        try:
            return pd.read_csv(f"{self.data_path}/{filename}")
        except Exception as e:
            print(f"Error loading replies data: {e}")
            return pd.DataFrame()
    
    def count_replies_per_tweet(self) -> Dict[str, int]:
        """
        Count replies for each tweet by matching:
        tweet.xlsx id_str == replies.csv conversation_id_str
        """
        try:
            replies_df = self.load_replies_csv()
            if replies_df.empty:
                print("WARNING: replies_df is empty")
                return {}

            print(f"Replies CSV shape: {replies_df.shape}")
            print(f"Replies CSV columns: {replies_df.columns.tolist()}")

            # Group by conversation_id_str and count rows
            reply_counts = replies_df.groupby('conversation_id_str').size().to_dict()
            print(f"Reply counts calculated: {len(reply_counts)} unique conversations")
            return reply_counts
        except Exception as e:
            print(f"ERROR in count_replies_per_tweet: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
    def extract_hashtags(self, text: str) -> List[str]:
        """Extract hashtags from text"""
        if pd.isna(text):
            return []
        return re.findall(r'#\w+', str(text))
    
    def parse_twitter_date(self, date_str: str) -> datetime:
        """Parse Twitter date format: 'Sat Nov 15 23:59:58 +0000 2025'"""
        try:
            # Remove timezone info for parsing
            cleaned = date_str.replace('+0000', '').strip()
            return datetime.strptime(cleaned, "%a %b %d %H:%M:%S %Y")
        except:
            return None
    
    def parse_iso_date(self, date_str: str) -> datetime:
        """Parse ISO format date: '2025-11-15T19:51:55+07:00'"""
        try:
            return pd.to_datetime(date_str)
        except:
            return None
    
    def get_engagement_by_day(self) -> Dict[str, int]:
        """Calculate engagement by day of week"""
        df = self.load_tweet_data()
        if df.empty:
            return {}
        
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_engagement = {day: 0 for day in day_names}
        
        for date_str in df['Date']:
            try:
                dt = self.parse_iso_date(date_str)
                if dt:
                    day_name = day_names[dt.dayofweek]
                    engagement = df[df['Date'] == date_str][['Likes', 'Replies', 'Retweets']].sum().sum()
                    day_engagement[day_name] += int(engagement)
            except:
                pass
        
        return convert_types(day_engagement)
    
    def get_top_hashtags(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top hashtags from all captions"""
        df = self.load_tweet_data()
        if df.empty:
            return []
        
        hashtags = []
        for caption in df['Caption']:
            hashtags.extend(self.extract_hashtags(caption))
        
        hashtag_counts = Counter(hashtags)
        top_hashtags = hashtag_counts.most_common(limit)
        
        result = [{"hashtag": tag, "count": int(count)} for tag, count in top_hashtags]
        return convert_types(result)
    
    def get_tweet_id_from_permalink(self, permalink: str) -> str:
        """Extract tweet ID from permalink like 'https://x.com/IndiHome/status/1989677741894246514'"""
        try:
            if pd.isna(permalink):
                return None
            # Split by / and get last part (tweet ID)
            parts = str(permalink).split('/')
            if len(parts) > 0:
                return parts[-1]
        except:
            pass
        return None
    
    def get_engagement_by_type(self) -> List[Dict[str, Any]]:
        """
        Get engagement stats by post type
        - Retweets: from tweet.xlsx Retweets column
        - Replies: count from replies.csv where conversation_id_str == id_str
        - Likes: from tweet.xlsx Likes column
        """
        try:
            df = self.load_tweet_data()
            if df.empty:
                print("WARNING: tweet df is empty")
                return []

            print(f"Tweet DF shape: {df.shape}")
            print(f"Tweet DF columns: {df.columns.tolist()}")

            # Get reply counts per tweet (from CSV)
            reply_counts = self.count_replies_per_tweet()

            # Calculate likes and retweets per type (from tweet.xlsx)
            type_engagement = df.groupby('Type')[['Likes', 'Retweets']].sum().reset_index()

            # Calculate replies from CSV for each type
            type_replies = {}
            for idx, row in df.iterrows():
                tweet_type = row['Type']
                # Extract tweet ID from Permalink
                tweet_id = self.get_tweet_id_from_permalink(row.get('Permalink'))

                if not tweet_id:
                    continue

                # Get reply count from CSV
                reply_count = reply_counts.get(int(tweet_id), 0)

                if tweet_type not in type_replies:
                    type_replies[tweet_type] = 0
                type_replies[tweet_type] += reply_count

            print(f"Type replies (from CSV): {type_replies}")

            result = []
            for idx, row in type_engagement.iterrows():
                tweet_type = row['Type']
                likes = int(row['Likes'])
                retweets = int(row['Retweets'])
                replies = type_replies.get(tweet_type, 0)
                total = likes + replies + retweets

                result.append({
                    "type": str(tweet_type),
                    "likes": likes,
                    "replies": replies,
                    "retweets": retweets,
                    "total": total
                })

            return convert_types(result)
        except Exception as e:
            print(f"ERROR in get_engagement_by_type: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_basic_statistics(self) -> Dict[str, int]:
        """
        Get basic statistics
        - Retweets: from tweet.xlsx Retweets column
        - Replies: count from replies.csv where conversation_id_str == id_str
        - Likes: from tweet.xlsx Likes column
        """
        try:
            df = self.load_tweet_data()
            if df.empty:
                return {}

            # Get reply counts per tweet (from CSV)
            reply_counts = self.count_replies_per_tweet()

            # Calculate total replies from CSV
            total_replies_from_csv = 0
            for idx, row in df.iterrows():
                # Extract tweet ID from Permalink
                tweet_id = self.get_tweet_id_from_permalink(row.get('Permalink'))
                if tweet_id:
                    total_replies_from_csv += reply_counts.get(int(tweet_id), 0)

            result = {
                "total_posts": int(len(df)),
                "total_replies": total_replies_from_csv,
                "total_likes": int(df['Likes'].sum()),
                "total_retweets": int(df['Retweets'].sum()),
                "total_engagement": int(df['Likes'].sum()) + total_replies_from_csv + int(df['Retweets'].sum())
            }
            return convert_types(result)
        except Exception as e:
            print(f"ERROR in get_basic_statistics: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
    def get_statistics_with_delta(self) -> Dict[str, Any]:
        """
        Get basic statistics with delta (change from previous post/day)
        - Retweets: from tweet.xlsx Retweets column
        - Replies: count from replies.csv where conversation_id_str == id_str
        - Likes: from tweet.xlsx Likes column
        """
        try:
            df = self.load_tweet_data()
            if df.empty:
                return {}

            # Sort by date to calculate deltas
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'])
                df = df.sort_values('Date')

            # Get reply counts per tweet (from CSV)
            reply_counts = self.count_replies_per_tweet()

            # Calculate engagement for each row
            df['tweet_id'] = df['Permalink'].apply(self.get_tweet_id_from_permalink)
            df['reply_count_csv'] = df['tweet_id'].apply(lambda x: reply_counts.get(int(x), 0) if x else 0)
            df['total_engagement_row'] = df['Likes'] + df['reply_count_csv'] + df['Retweets']

            # Calculate totals
            total_posts = int(len(df))
            total_replies = int(df['reply_count_csv'].sum())
            total_likes = int(df['Likes'].sum())
            total_retweets = int(df['Retweets'].sum())
            total_engagement = total_likes + total_replies + total_retweets

            # Calculate deltas: compare last post with average of previous posts
            if total_posts >= 2:
                last_post = df.iloc[-1]
                previous_posts = df.iloc[:-1]

                delta_posts = 0  # Posts are discrete
                delta_replies = int(last_post['reply_count_csv'] - previous_posts['reply_count_csv'].mean())
                delta_likes = int(last_post['Likes'] - previous_posts['Likes'].mean())
                delta_retweets = int(last_post['Retweets'] - previous_posts['Retweets'].mean())
                delta_engagement = int(last_post['total_engagement_row'] - previous_posts['total_engagement_row'].mean())
            else:
                # If only one post, no comparison available
                delta_posts = 0
                delta_replies = 0
                delta_likes = 0
                delta_retweets = 0
                delta_engagement = 0

            result = {
                "total_posts": total_posts,
                "total_replies": total_replies,
                "total_likes": total_likes,
                "total_retweets": total_retweets,
                "total_engagement": total_engagement,
                "delta_posts": delta_posts,
                "delta_replies": delta_replies,
                "delta_likes": delta_likes,
                "delta_retweets": delta_retweets,
                "delta_engagement": delta_engagement
            }
            return convert_types(result)
        except Exception as e:
            print(f"ERROR in get_statistics_with_delta: {e}")
            import traceback
            traceback.print_exc()
            return {}

    def get_peak_activity_hours(self) -> Dict[str, Any]:
        """
        Analyze peak activity hours using DBSCAN clustering on replies data from CSV.
        Returns non-outlier clusters, peak hour ranges, and PCA visualization data.
        """
        try:
            # Load replies CSV
            df = self.load_replies_csv()
            if df.empty:
                print("WARNING: replies CSV is empty")
                return {}

            # Extract hour from created_at
            hours = []
            for date_str in df['created_at']:
                dt = self.parse_twitter_date(date_str)
                if dt:
                    hours.append(dt.hour)

            if len(hours) < 2:
                return {"error": "Not enough data for clustering"}

            # Prepare data for clustering
            # Create features: [hour, count at that hour]
            hour_counts = Counter(hours)

            # Create feature matrix: each row is [hour, normalized_count]
            X = np.array([[hour, count] for hour, count in hour_counts.items()])

            # Standardize features
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)

            # Apply DBSCAN clustering
            # eps and min_samples can be tuned based on data
            dbscan = DBSCAN(eps=0.5, min_samples=2)
            labels = dbscan.fit_predict(X_scaled)

            # Separate non-outliers (label != -1) from outliers (label == -1)
            non_outlier_mask = labels != -1
            non_outlier_hours = X[non_outlier_mask]
            non_outlier_labels = labels[non_outlier_mask]

            # Get peak hour ranges from non-outlier clusters
            peak_ranges = []
            unique_clusters = set(non_outlier_labels)

            for cluster_id in unique_clusters:
                cluster_mask = non_outlier_labels == cluster_id
                cluster_hours = non_outlier_hours[cluster_mask][:, 0]  # Get hour values

                min_hour = int(np.min(cluster_hours))
                max_hour = int(np.max(cluster_hours))
                avg_count = int(np.mean(cluster_hours))

                peak_ranges.append({
                    "cluster_id": int(cluster_id),
                    "start_hour": min_hour,
                    "end_hour": max_hour,
                    "range": f"{min_hour:02d}:00 - {max_hour:02d}:00",
                    "avg_activity": avg_count
                })

            # Sort by average activity
            peak_ranges.sort(key=lambda x: x['avg_activity'], reverse=True)

            # PCA for visualization (reduce to 2D if needed)
            pca = PCA(n_components=2)
            X_pca = pca.fit_transform(X_scaled)

            # Prepare scatter plot data
            scatter_data = {
                "points": [
                    {
                        "x": float(X_pca[i, 0]),
                        "y": float(X_pca[i, 1]),
                        "hour": int(X[i, 0]),
                        "count": int(X[i, 1]),
                        "cluster": int(labels[i]),
                        "is_outlier": bool(labels[i] == -1)
                    }
                    for i in range(len(X))
                ],
                "explained_variance": [float(v) for v in pca.explained_variance_ratio_]
            }

            result = {
                "peak_ranges": peak_ranges,
                "scatter_data": scatter_data,
                "total_hours_analyzed": len(hours),
                "unique_hours": len(hour_counts),
                "num_clusters": len(unique_clusters),
                "num_outliers": int(np.sum(labels == -1))
            }

            return convert_types(result)

        except Exception as e:
            print(f"ERROR in get_peak_activity_hours: {e}")
            import traceback
            traceback.print_exc()
            return {}
