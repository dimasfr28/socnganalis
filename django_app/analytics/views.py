from django.shortcuts import render
from django.http import JsonResponse
import pandas as pd
import json
import os
import re
from collections import Counter
import numpy as np

def home(request):
    """Home page - deskripsi aplikasi"""
    return render(request, 'home.html')

def descriptive_analytics(request):
    """Halaman Descriptive Analytics"""
    return render(request, 'descriptive_analytics.html')

def sentiment_analysis(request):
    """Halaman Sentiment Analysis"""
    return render(request, 'sentiment_analysis.html')

def topic_pillar(request):
    """Halaman Topic Pillar Analysis"""
    return render(request, 'topic_pillar.html')

def emotion_analysis(request):
    """Halaman Emotion Analysis"""
    return render(request, 'emotion_analysis.html')

def recommendations(request):
    """Halaman Recommendation System"""
    return render(request, 'recommendations.html')

def data_initialization(request):
    """Halaman Data Initialization"""
    return render(request, 'data_initialization.html')

def dataset_manager(request):
    """Halaman Dataset Manager"""
    return render(request, 'dataset_manager.html')

def preprocess_text(text):
    """Advanced preprocessing - following preprocessing.ipynb"""
    if pd.isna(text) or text == '':
        return ""

    text = str(text)

    # Emoji to sentiment conversion
    emoji_dict = {
        '😊': 'senang', '😢': 'sedih', '😡': 'marah', '😍': 'suka',
        '👍': 'bagus', '👎': 'jelek', '❤️': 'suka', '💔': 'kecewa',
        '😂': 'lucu', '😭': 'menangis', '🔥': 'bagus', '💯': 'bagus',
        '🙏': 'terima_kasih', '👌': 'oke', '⚡': 'cepat', '🐌': 'lambat'
    }

    for emoji, replacement in emoji_dict.items():
        text = text.replace(emoji, f' {replacement} ')

    # Remove URLs
    text = re.sub(r'http[s]?://\S+', '', text)
    text = re.sub(r'www\.\S+', '', text)

    # Remove mentions
    text = re.sub(r'@\w+', '', text)

    # Process hashtags
    text = re.sub(r'#(\w+)', lambda m: re.sub('([a-z])([A-Z])', r'\1 \2', m.group(1)).lower(), text)

    # Remove unknown emoji
    emoji_pattern = re.compile("["
                             u"\U0001F600-\U0001F64F"
                             u"\U0001F300-\U0001F5FF"
                             u"\U0001F680-\U0001F6FF"
                             u"\U0001F1E0-\U0001F1FF"
                             "]+", flags=re.UNICODE)
    text = emoji_pattern.sub(r' ', text)

    text = text.lower()
    text = re.sub(r'(.)\1{3,}', r'\1\1', text)
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()

    # Stopwords
    stopwords_id = {
        'yang', 'dan', 'di', 'dengan', 'untuk', 'pada', 'adalah',
        'ini', 'itu', 'dari', 'ke', 'tidak', 'atau', 'juga',
        'kak', 'ka', 'gan', 'min', 'admin', 'halo', 'hai',
        'mohon', 'tolong', 'ya', 'oke', 'dong', 'nya'
    }

    words = text.split()
    filtered_words = [word for word in words if word not in stopwords_id and len(word) > 2]
    return ' '.join(filtered_words)

def simple_sentiment_analysis(text):
    """Simple rule-based sentiment analysis"""
    # Kata-kata positif dan negatif dalam bahasa Indonesia
    positive_words = [
        'bagus', 'baik', 'senang', 'puas', 'cepat', 'lancar', 'mantap',
        'oke', 'terima kasih', 'thanks', 'good', 'fast', 'smooth', 'great',
        'sukses', 'mantul', 'keren', 'top', 'recommended', 'recommended'
    ]

    negative_words = [
        'lambat', 'lemot', 'jelek', 'buruk', 'kecewa', 'marah', 'kesal',
        'gangguan', 'error', 'rusak', 'masalah', 'complain', 'komplain',
        'bad', 'slow', 'worst', 'terrible', 'parah', 'payah', 'down',
        'los', 'mati', 'putus', 'lag', 'kaga', 'gak jalan', 'ga bisa'
    ]

    text_lower = text.lower()

    pos_count = sum(1 for word in positive_words if word in text_lower)
    neg_count = sum(1 for word in negative_words if word in text_lower)

    if neg_count > pos_count:
        return 'negative'
    elif pos_count > neg_count:
        return 'positive'
    else:
        return 'neutral'

def get_topic_pillar_data(request):
    """API endpoint untuk mendapatkan topic pillar data - Proxy to FastAPI"""
    try:
        import requests

        # Call FastAPI endpoint
        fastapi_url = "http://fastapi:8001/api/topic-pillars"
        response = requests.get(fastapi_url, timeout=60)  # Longer timeout for topic modeling

        if response.status_code == 200:
            return JsonResponse(response.json())
        else:
            return JsonResponse({'error': 'Failed to fetch data from FastAPI'}, status=500)

    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': f'Request failed: {str(e)}'}, status=500)


def get_post_detail(request):
    """API endpoint untuk mendapatkan detail post - Proxy to FastAPI"""
    try:
        import requests
        from urllib.parse import quote

        # Get permalink from query params
        permalink = request.GET.get('permalink', '')

        if not permalink:
            return JsonResponse({'error': 'Permalink parameter is required'}, status=400)

        # URL encode the permalink
        encoded_permalink = quote(permalink, safe='')

        # Call FastAPI endpoint
        fastapi_url = f"http://fastapi:8001/api/post-detail?permalink={encoded_permalink}"
        response = requests.get(fastapi_url, timeout=30)

        if response.status_code == 200:
            return JsonResponse(response.json())
        else:
            return JsonResponse({'error': 'Failed to fetch data from FastAPI'}, status=500)

    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': f'Request failed: {str(e)}'}, status=500)


def get_sentiment_data(request):
    """API endpoint untuk mendapatkan data sentiment analysis - Proxy to FastAPI"""
    try:
        import requests

        # Call FastAPI endpoint
        fastapi_url = "http://fastapi:8001/api/sentiment-analysis"
        response = requests.get(fastapi_url, timeout=30)

        if response.status_code == 200:
            return JsonResponse(response.json())
        else:
            return JsonResponse({'error': 'Failed to fetch data from FastAPI'}, status=500)

    except requests.exceptions.RequestException as e:
        # Fallback to local processing if FastAPI is unavailable
        try:
            # Load replies data
            replies_path = '/home/dimas/crawling_sosmed/tweets-data/replies.csv'
            df = pd.read_csv(replies_path)

            # Preprocessing
            df['cleaned_text'] = df['full_text'].apply(preprocess_text)

            # Sentiment analysis
            df['sentiment'] = df['cleaned_text'].apply(simple_sentiment_analysis)

            # Hitung dominasi sentimen
            sentiment_counts = df['sentiment'].value_counts().to_dict()

            # Total untuk persentase
            total = len(df)
            sentiment_distribution = {
                sentiment: {
                    'count': int(count),
                    'percentage': round((count / total) * 100, 2)
                }
                for sentiment, count in sentiment_counts.items()
            }

            # Sentimen berdasarkan retweet
            sentiment_by_retweet = df.groupby('sentiment')['retweet_count'].sum().to_dict()
            sentiment_by_retweet = {k: int(v) for k, v in sentiment_by_retweet.items()}

            # Word frequency untuk word cloud (top 50 words per sentiment)
            def get_top_words(sentiment, n=50):
                texts = df[df['sentiment'] == sentiment]['cleaned_text']
                all_words = ' '.join(texts).split()
                # Filter kata yang lebih dari 3 karakter
                all_words = [word for word in all_words if len(word) > 3]
                word_freq = Counter(all_words).most_common(n)
                return [{'text': word, 'value': count} for word, count in word_freq]

            wordcloud_data = {
                'positive': get_top_words('positive'),
                'negative': get_top_words('negative'),
                'neutral': get_top_words('neutral')
            }

            response_data = {
                'sentiment_distribution': sentiment_distribution,
                'sentiment_by_retweet': sentiment_by_retweet,
                'wordcloud_data': wordcloud_data,
                'total_analyzed': total,
                'topics': {
                    'negative': [],
                    'positive': [],
                    'neutral': []
                },
                'metadata': {
                    'data_source': 'replies.csv',
                    'preprocessing_steps': ['lowercase', 'remove_urls', 'remove_mentions', 'remove_special_chars'],
                    'sentiment_method': 'rule_based_fallback',
                    'topic_modeling': 'unavailable'
                }
            }

            return JsonResponse(response_data)

        except Exception as inner_e:
            return JsonResponse({'error': str(inner_e)}, status=400)

def get_analytics_data(request):
    """API endpoint untuk mendapatkan data analytics"""
    try:
        # Load tweet data
        tweet_data_path = '/home/dimas/crawling_sosmed/tweets-data/tweet.xlsx'
        df_tweets = pd.read_excel(tweet_data_path, header=4)

        # Hitung statistik dasar
        stats = {
            'total_posts': len(df_tweets),
            'total_replies': int(df_tweets['Replies'].sum()),
            'total_likes': int(df_tweets['Likes'].sum()),
            'total_retweets': int(df_tweets['Retweets'].sum()),
        }

        return JsonResponse(stats)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


def get_recommendations_data(request):
    """API endpoint untuk mendapatkan recommendation data - Proxy to FastAPI"""
    try:
        import requests

        # Call FastAPI endpoint
        fastapi_url = "http://fastapi:8001/api/recommendations"
        response = requests.get(fastapi_url, timeout=60)  # Longer timeout for comprehensive analysis

        if response.status_code == 200:
            return JsonResponse(response.json())
        else:
            return JsonResponse({'error': 'Failed to fetch data from FastAPI'}, status=500)

    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': f'Request failed: {str(e)}'}, status=500)
