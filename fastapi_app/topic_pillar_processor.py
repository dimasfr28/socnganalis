"""
Topic Pillar Analysis Processor
Uses LDA (Latent Dirichlet Allocation) for topic modeling
"""

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.model_selection import GridSearchCV
import re
from collections import Counter
import pickle
import os


def preprocess_text(text):
    """
    Advanced preprocessing untuk topic modeling
    Mengikuti preprocessing dari sentiment_processor.py
    """
    if pd.isna(text) or text == '':
        return ""

    text = str(text)

    # 1. Emoji dictionary untuk konversi emoji ke sentiment
    emoji_dict = {
        '😊': 'senang', '😢': 'sedih', '😡': 'marah', '😍': 'suka',
        '👍': 'bagus', '👎': 'jelek', '❤️': 'suka', '💔': 'kecewa',
        '😂': 'lucu', '😭': 'menangis', '🔥': 'bagus', '💯': 'bagus',
        '😀': 'senang', '😃': 'senang', '😄': 'senang', '😁': 'senang',
        '🙏': 'terima_kasih', '👌': 'oke', '✅': 'benar', '❌': 'salah',
        '💸': 'mahal', '💰': 'murah', '📶': 'sinyal', '📡': 'internet',
        '🚫': 'tidak', '⚡': 'cepat', '🐌': 'lambat'
    }

    # Konversi emoji ke teks
    for emoji, replacement in emoji_dict.items():
        text = text.replace(emoji, f' {replacement} ')

    # 2. Remove URLs
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    text = re.sub(r'www\.(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)

    # 3. Remove mentions
    text = re.sub(r'@\w+', '', text)

    # 4. Process hashtags - split CamelCase
    def process_hashtag(match):
        hashtag = match.group(1)
        camel_split = re.sub('([a-z])([A-Z])', r'\1 \2', hashtag)
        return camel_split.lower()

    text = re.sub(r'#(\w+)', process_hashtag, text)

    # 5. Remove emoji yang tidak dikenal
    emoji_pattern = re.compile("["
                             u"\U0001F600-\U0001F64F"
                             u"\U0001F300-\U0001F5FF"
                             u"\U0001F680-\U0001F6FF"
                             u"\U0001F1E0-\U0001F1FF"
                             u"\U00002702-\U000027B0"
                             u"\U000024C2-\U0001F251"
                             "]+", flags=re.UNICODE)
    text = emoji_pattern.sub(r' ', text)

    # 6. Lowercase
    text = text.lower()

    # 7. Normalize repeated characters (lebih dari 3 kali jadi 2 kali)
    text = re.sub(r'(.)\1{3,}', r'\1\1', text)

    # 8. Remove special characters tapi keep spaces
    text = re.sub(r'[^\w\s]', ' ', text)

    # 9. Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    # 10. Stopwords removal (Indonesian + domain-specific)
    stopwords_id = {
        'yang', 'dan', 'di', 'dengan', 'untuk', 'pada', 'adalah',
        'ini', 'itu', 'dari', 'ke', 'tidak', 'atau', 'juga', 'akan',
        'telah', 'dapat', 'ada', 'dalam', 'saya', 'kamu', 'dia',
        'mereka', 'kami', 'sudah', 'belum', 'masih', 'sangat',
        'sekali', 'hanya', 'bisa', 'mau', 'ingin', 'perlu', 'harus',
        'kak', 'ka', 'gan', 'sis', 'bro', 'min', 'admin', 'cs', 'halo',
        'hai', 'selamat', 'pagi', 'siang', 'sore', 'malam', 'mohon',
        'tolong', 'cek', 'thanks', 'thx', 'makasih', 'terimakasih', 'makasi',
        'terima', 'kasih', 'ya', 'yah', 'iya', 'ok', 'oke', 'dong', 'nala',
        'deh', 'nih', 'sih', 'loh', 'wkwk', 'hehe', 'hihi', 'nya', 'kok', 'indihome', 'kakak', 'jadi', 'atas',
        # Kata kotor untuk difilter
        'kontol', 'anjing', 'bangsat', 'bajingan', 'memek', 'pepek', 'kampret',
        'goblok', 'tolol', 'tai', 'brengsek', 'jancuk', 'keparat', 'sialan',
        'perek', 'sundal', 'lonte', 'pelacur', 'babi', 'ajg', 'anjng', 'anj'
    }

    words = text.split()
    filtered_words = [word for word in words if word not in stopwords_id and len(word) > 2]
    text = ' '.join(filtered_words)

    return text


def find_optimal_k(texts, k_range=range(3, 11), max_iter=20):
    """
    Find optimal number of topics using GridSearchCV
    Returns best k value
    """
    vectorizer = TfidfVectorizer(
        max_features=1000,
        min_df=2,
        max_df=0.8
    )

    doc_term_matrix = vectorizer.fit_transform(texts)

    # Grid search parameters
    search_params = {'n_components': list(k_range)}

    lda = LatentDirichletAllocation(
        random_state=42,
        max_iter=max_iter,
        learning_method='online'
    )

    # Perform grid search
    model = GridSearchCV(lda, param_grid=search_params, cv=3, n_jobs=-1)
    model.fit(doc_term_matrix)

    best_k = model.best_params_['n_components']
    best_score = model.best_score_

    return best_k, best_score


def perform_topic_modeling(df, n_topics=None):
    """
    Perform LDA topic modeling on tweet data

    Returns:
        - topics: list of topic dictionaries with top words
        - topic_assignments: dominant topic for each tweet
        - topic_scores: strength scores for each topic per tweet
    """
    # Preprocess tweets (use Caption column from tweet.xlsx)
    df['cleaned_text'] = df['Caption'].apply(preprocess_text)

    # Remove empty texts
    df_clean = df[df['cleaned_text'].str.len() > 0].copy()

    # If n_topics not specified, find optimal k
    if n_topics is None:
        print("Finding optimal number of topics...")
        n_topics, best_score = find_optimal_k(df_clean['cleaned_text'].tolist())
        print(f"Optimal K: {n_topics}, Score: {best_score:.4f}")

    # Vectorize
    vectorizer = TfidfVectorizer(
        max_features=1000,
        min_df=2,
        max_df=0.8
    )

    doc_term_matrix = vectorizer.fit_transform(df_clean['cleaned_text'])

    # LDA Model
    lda_model = LatentDirichletAllocation(
        n_components=n_topics,
        random_state=42,
        max_iter=20,
        learning_method='online'
    )

    lda_output = lda_model.fit_transform(doc_term_matrix)

    # Get feature names
    feature_names = vectorizer.get_feature_names_out()

    # Extract topics
    topics = []
    for topic_idx, topic in enumerate(lda_model.components_):
        top_words_idx = topic.argsort()[-10:][::-1]
        top_words = [feature_names[i] for i in top_words_idx]
        topics.append({
            'topic_id': topic_idx,
            'words': top_words,
            'label': f"Topic {topic_idx + 1}"
        })

    # Get dominant topic for each document
    dominant_topics = lda_output.argmax(axis=1)
    topic_strengths = lda_output.max(axis=1)

    # Add to dataframe
    df_clean['dominant_topic'] = dominant_topics
    df_clean['topic_strength'] = topic_strengths

    return topics, df_clean, lda_output


def extract_id_from_permalink(permalink):
    """Extract tweet ID from Permalink URL"""
    try:
        if pd.isna(permalink) or permalink == '':
            return None
        # Permalink format: https://www.twitter.com/USER_ID/status/TWEET_ID
        match = re.search(r'/status/(\d+)', str(permalink))
        if match:
            return match.group(1)
        return None
    except:
        return None


def calculate_reply_count(df_replies, id_str):
    """
    Calculate reply count by matching tweet id_str with conversation_id_str in replies CSV
    tweet.xlsx id_str == replies.csv conversation_id_str

    NOTE: Ini menghitung REPLIES, bukan retweets
    """
    try:
        if pd.isna(id_str) or id_str is None:
            return 0
        # Convert to int for matching (conversation_id_str is int64 in CSV)
        id_int = int(id_str)
        # Count rows in replies where conversation_id_str matches this tweet's id_str
        return len(df_replies[df_replies['conversation_id_str'] == id_int])
    except:
        return 0


def analyze_topic_pillars(tweet_file_path):
    """
    Main function to analyze topic pillars
    """
    # Load tweet data
    df = pd.read_excel(tweet_file_path, header=4)

    # Extract id_str from Permalink
    df['id_str'] = df['Permalink'].apply(extract_id_from_permalink)

    # Load replies data for retweet counting
    # Get replies path from same directory as tweet file
    import os
    tweet_dir = os.path.dirname(tweet_file_path)
    replies_path = os.path.join(tweet_dir, 'replies.csv')

    try:
        df_replies = pd.read_csv(replies_path)
        print(f"Loaded {len(df_replies)} replies from {replies_path}")
    except Exception as e:
        print(f"Warning: Could not load replies file: {e}")
        df_replies = pd.DataFrame()  # Empty dataframe as fallback

    # Perform topic modeling
    topics, df_with_topics, topic_scores = perform_topic_modeling(df)

    # Calculate engagement by topic
    topic_engagement = []

    for topic_idx in range(len(topics)):
        # Get tweets for this topic
        topic_tweets = df_with_topics[df_with_topics['dominant_topic'] == topic_idx]

        # Calculate engagement
        total_likes = int(topic_tweets['Likes'].sum())
        total_retweets = int(topic_tweets['Retweets'].sum())  # From tweet.xlsx

        # Calculate replies using replies.csv
        # Match tweet.xlsx id_str with replies.csv conversation_id_str
        total_replies = 0
        for _, row in topic_tweets.iterrows():
            if 'id_str' in row:
                reply_count = calculate_reply_count(df_replies, row['id_str'])
                total_replies += reply_count

        total_engagement = total_likes + total_replies + total_retweets

        topic_engagement.append({
            'topic_id': topic_idx,
            'topic_label': topics[topic_idx]['label'],
            'total_likes': total_likes,
            'total_replies': total_replies,
            'total_retweets': total_retweets,
            'total_engagement': total_engagement,
            'tweet_count': len(topic_tweets)
        })

    # Get top posts for each topic
    topic_posts = {}

    for topic_idx in range(len(topics)):
        topic_tweets = df_with_topics[df_with_topics['dominant_topic'] == topic_idx]

        # Sort by topic strength
        topic_tweets_sorted = topic_tweets.sort_values('topic_strength', ascending=False)

        # Get top 10 posts
        top_posts = []
        for _, row in topic_tweets_sorted.head(10).iterrows():
            # Get id_str for reply counting
            id_str = row.get('id_str', None)
            reply_count = calculate_reply_count(df_replies, id_str)

            top_posts.append({
                'id_str': str(row.get('Permalink', '')),
                'full_text': str(row['Caption']),
                'likes': int(row['Likes']) if pd.notna(row.get('Likes')) else 0,
                'replies': reply_count,  # From CSV
                'retweets': int(row['Retweets']) if pd.notna(row.get('Retweets')) else 0,  # From tweet.xlsx
                'tweet_type': str(row.get('Tweet Type', 'Unknown')),
                'topic_strength': float(row['topic_strength']),
                'created_at': str(row.get('Date', ''))
            })

        topic_posts[topic_idx] = top_posts

    return {
        'topics': topics,
        'topic_engagement': topic_engagement,
        'topic_posts': topic_posts,
        'total_tweets_analyzed': len(df_with_topics),
        'n_topics': len(topics)
    }


def extract_hashtags(text):
    """Extract hashtags from text"""
    if pd.isna(text) or text == '':
        return []
    hashtags = re.findall(r'#(\w+)', str(text))
    return hashtags


def get_post_detail(tweet_file_path, permalink):
    """
    Get detailed information for a specific post
    Returns hashtags and word cloud data from replies
    """
    try:
        # Load tweet data
        df = pd.read_excel(tweet_file_path, header=4)

        # Find the post by permalink
        post = df[df['Permalink'] == permalink]

        if post.empty:
            return {'error': 'Post not found'}

        post_row = post.iloc[0]

        # Extract hashtags from caption
        hashtags = extract_hashtags(post_row['Caption'])

        # Extract id_str from permalink
        id_str = extract_id_from_permalink(permalink)

        # Load replies data from same directory as tweet file
        import os
        tweet_dir = os.path.dirname(tweet_file_path)
        replies_path = os.path.join(tweet_dir, 'replies.csv')

        try:
            df_replies = pd.read_csv(replies_path)

            # Get all replies for this post (where conversation_id_str == id_str)
            if id_str:
                id_int = int(id_str)
                post_replies = df_replies[df_replies['conversation_id_str'] == id_int]

                # Combine all reply texts
                all_reply_texts = ' '.join(post_replies['full_text'].dropna().astype(str).tolist())

                # Preprocess combined text
                cleaned_text = preprocess_text(all_reply_texts)

                # Generate word frequency
                if cleaned_text:
                    words = cleaned_text.split()
                    from collections import Counter
                    word_freq = Counter(words)

                    # Get top 30 words
                    wordcloud_data = [
                        {'text': word, 'value': count}
                        for word, count in word_freq.most_common(30)
                    ]
                else:
                    wordcloud_data = []

                reply_count = len(post_replies)
            else:
                wordcloud_data = []
                reply_count = 0

        except Exception as e:
            print(f"Error loading replies: {e}")
            wordcloud_data = []
            reply_count = 0

        return {
            'permalink': permalink,
            'caption': str(post_row['Caption']),
            'hashtags': hashtags,
            'wordcloud_data': wordcloud_data,
            'reply_count': reply_count,  # Count from CSV
            'likes': int(post_row['Likes']) if pd.notna(post_row.get('Likes')) else 0,
            'replies': reply_count,  # Replies from CSV
            'retweets': int(post_row['Retweets']) if pd.notna(post_row.get('Retweets')) else 0,  # From tweet.xlsx
            'tweet_type': str(post_row.get('Tweet Type', 'Unknown')),
            'date': str(post_row.get('Date', ''))
        }

    except Exception as e:
        return {'error': str(e)}
