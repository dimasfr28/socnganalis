"""
Sentiment Analysis Processor Module
Handles all sentiment analysis operations including preprocessing, model loading, and prediction
"""

import pandas as pd
import numpy as np
import re
import joblib
import os
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from typing import Dict, List, Any


class SentimentProcessor:
    """Class untuk menangani sentiment analysis dengan LinearSVM model"""

    def __init__(self, model_path: str, vectorizer_path: str = None):
        """
        Initialize SentimentProcessor

        Args:
            model_path: Path ke file model LinearSVM (.pkl)
            vectorizer_path: Path ke file TfidfVectorizer (.pkl), opsional
        """
        self.model_path = model_path
        self.vectorizer_path = vectorizer_path or model_path.replace('LinearSVM.pkl', 'tfidf_vectorizer.pkl')
        self.model = None
        self.vectorizer = None
        self.model_loaded = False

        # Load model saat inisialisasi
        self._load_model()

    def _create_new_vectorizer(self):
        """Create new TfidfVectorizer with specified parameters"""
        self.vectorizer = TfidfVectorizer(
            tokenizer=lambda s: s.split(),  # Tokenisasi berdasarkan spasi
            ngram_range=(1, 1),  # Hanya unigram
            min_df=1,  # Tidak ada kata yang dibuang
            max_df=0.95  # Kata dibuang jika kemunculannya lebih dari 95%
        )
        print(f"✓ Created new TfidfVectorizer (will be fitted on data)")
        print(f"  Note: For best results, use the vectorizer from training")
        self.model_loaded = False  # Vectorizer belum di-fit

    def _load_model(self):
        """Load LinearSVM model dan TfidfVectorizer"""
        try:
            # Load model
            if os.path.exists(self.model_path):
                self.model = joblib.load(self.model_path)
                print(f"✓ LinearSVM model loaded from {self.model_path}")
            else:
                print(f"✗ Model file not found: {self.model_path}")
                return

            # Load vectorizer jika sudah ada
            print(f"Checking vectorizer at: {self.vectorizer_path}")
            print(f"Vectorizer exists: {os.path.exists(self.vectorizer_path)}")

            if os.path.exists(self.vectorizer_path):
                try:
                    print(f"Attempting to load vectorizer...")
                    self.vectorizer = joblib.load(self.vectorizer_path)
                    print(f"✓ Fitted TfidfVectorizer loaded from {self.vectorizer_path}")
                    self.model_loaded = True
                except Exception as vec_err:
                    print(f"⚠ Error loading vectorizer: {vec_err}")
                    print(f"  Creating new vectorizer instead")
                    self._create_new_vectorizer()
            else:
                print(f"⚠ Vectorizer not found at {self.vectorizer_path}")
                self._create_new_vectorizer()

        except Exception as e:
            import traceback
            import sys
            print(f"✗ Error loading model: {repr(e)}")
            print(f"Error type: {type(e).__name__}")
            print(f"Error args: {e.args}")
            traceback.print_exc(file=sys.stdout)
            self.model = None
            self.vectorizer = None
            self.model_loaded = False

    def preprocess_text(self, text: str) -> str:
        """
        Advanced preprocessing untuk sentiment analysis
        Mengikuti preprocessing.ipynb

        Args:
            text: Raw text input

        Returns:
            Cleaned and preprocessed text
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
            'terima', 'kasih', 'ya', 'yah', 'iya', 'ok', 'oke', 'dong', 'nala', 'pau', 'vioni'
            'deh', 'nih', 'sih', 'loh', 'wkwk', 'hehe', 'hihi', 'nya', 'kok', 'indihome', 'kakak', 'jadi', 'atas'
            # Kata kotor untuk difilter
            'kontol', 'anjing', 'bangsat', 'bajingan', 'memek', 'pepek', 'kampret',
            'goblok', 'tolol', 'tai', 'brengsek', 'jancuk', 'keparat', 'sialan',
            'perek', 'sundal', 'lonte', 'pelacur', 'babi', 'ajg', 'anjng', 'anj'
        }

        words = text.split()
        filtered_words = [word for word in words if word not in stopwords_id and len(word) > 2]
        text = ' '.join(filtered_words)

        return text

    def predict_sentiment(self, text: str) -> str:
        """
        Predict sentiment untuk single text menggunakan LinearSVM model

        Args:
            text: Cleaned text

        Returns:
            Sentiment label: 'positive', 'negative', atau 'neutral'
        """
        if not self.model_loaded or self.model is None or self.vectorizer is None:
            return self._fallback_sentiment(text)

        try:
            if not text or len(text.strip()) == 0:
                return 'neutral'

            # Vectorize dan predict
            X = self.vectorizer.transform([text])
            prediction = self.model.predict(X)[0]
            return prediction

        except Exception as e:
            print(f"Error in model prediction: {e}")
            return self._fallback_sentiment(text)

    def _fallback_sentiment(self, text: str) -> str:
        """
        Fallback rule-based sentiment analysis
        Digunakan jika model tidak tersedia

        Args:
            text: Text to analyze

        Returns:
            Sentiment label
        """
        positive_words = [
            'bagus', 'baik', 'senang', 'puas', 'cepat', 'lancar', 'mantap',
            'oke', 'terima kasih', 'thanks', 'good', 'fast', 'smooth', 'great',
            'sukses', 'mantul', 'keren', 'top', 'recommended', 'hebat', 'memuaskan'
        ]

        negative_words = [
            'lambat', 'lemot', 'jelek', 'buruk', 'kecewa', 'marah', 'kesal',
            'gangguan', 'error', 'rusak', 'masalah', 'complain', 'komplain',
            'bad', 'slow', 'worst', 'terrible', 'parah', 'payah', 'down',
            'los', 'mati', 'putus', 'lag', 'kaga', 'gak jalan', 'ga bisa', 'kendala', 'keluhan',
            'mengecewakan', 'zonk', 'lelet', 'anjlok'
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

    def analyze_dataframe(self, df: pd.DataFrame, text_column: str = 'full_text') -> pd.DataFrame:
        """
        Analyze sentiment untuk seluruh DataFrame

        Args:
            df: DataFrame dengan kolom text
            text_column: Nama kolom yang berisi text

        Returns:
            DataFrame dengan kolom tambahan 'cleaned_text' dan 'sentiment'
        """
        # Preprocessing
        df['cleaned_text'] = df[text_column].apply(self.preprocess_text)

        # Remove empty texts
        df = df[df['cleaned_text'].str.len() > 0].copy()

        # Fit vectorizer jika belum fitted (untuk vectorizer baru)
        if not self.model_loaded and self.model is not None and self.vectorizer is not None:
            try:
                print(f"Fitting vectorizer on {len(df)} texts...")
                X = self.vectorizer.fit_transform(df['cleaned_text'].astype(str))

                # Save fitted vectorizer untuk reuse
                if not os.path.exists(self.vectorizer_path):
                    joblib.dump(self.vectorizer, self.vectorizer_path)
                    print(f"✓ Saved fitted vectorizer to {self.vectorizer_path}")

                # Predict menggunakan model
                predictions = self.model.predict(X)
                df['sentiment'] = predictions

                self.model_loaded = True
                print(f"✓ Sentiment prediction completed using LinearSVM model on {len(df)} texts")
                print(f"  Features generated: {X.shape[1]}")

            except Exception as e:
                print(f"✗ Error in model prediction: {e}")
                print(f"⚠ Using fallback rule-based sentiment analysis")
                df['sentiment'] = df['cleaned_text'].apply(self._fallback_sentiment)
        else:
            # Gunakan model yang sudah loaded
            if self.model_loaded:
                try:
                    X = self.vectorizer.transform(df['cleaned_text'].astype(str))
                    predictions = self.model.predict(X)
                    df['sentiment'] = predictions
                    print(f"✓ Sentiment prediction completed using LinearSVM model on {len(df)} texts")
                except Exception as e:
                    print(f"✗ Error in model prediction: {e}")
                    df['sentiment'] = df['cleaned_text'].apply(self._fallback_sentiment)
            else:
                df['sentiment'] = df['cleaned_text'].apply(self._fallback_sentiment)

        return df

    def extract_topics_lda(self, texts: List[str], n_topics: int = 5, n_words: int = 10) -> List[Dict]:
        """
        Extract topics menggunakan LDA (Latent Dirichlet Allocation)

        Args:
            texts: List of texts
            n_topics: Number of topics to extract
            n_words: Number of top words per topic

        Returns:
            List of topic dictionaries
        """
        try:
            # Filter empty texts
            texts = [t for t in texts if len(t.strip()) > 0]

            if len(texts) < 3:
                return []

            # Vectorize text
            vectorizer = CountVectorizer(max_features=100, stop_words='english', min_df=1)
            doc_term_matrix = vectorizer.fit_transform(texts)

            # Apply LDA
            lda = LatentDirichletAllocation(n_components=min(n_topics, len(texts)), random_state=42)
            lda.fit(doc_term_matrix)

            # Get feature names
            feature_names = vectorizer.get_feature_names_out()

            # Extract topics
            topics = []
            for topic_idx, topic in enumerate(lda.components_):
                top_words_idx = topic.argsort()[-n_words:][::-1]
                top_words = [feature_names[i] for i in top_words_idx]
                topics.append({
                    'topic_id': topic_idx,
                    'words': top_words,
                    'weights': [float(topic[i]) for i in top_words_idx]
                })

            return topics

        except Exception as e:
            print(f"LDA Error: {e}")
            return []

    def get_word_frequency(self, texts: pd.Series, n: int = 50) -> List[Dict[str, Any]]:
        """
        Get top N words dari texts

        Args:
            texts: Series of texts
            n: Number of top words to return

        Returns:
            List of dicts with 'text' and 'value' keys
        """
        all_words = ' '.join(texts).split()
        # Filter kata yang lebih dari 3 karakter
        all_words = [word for word in all_words if len(word) > 3]
        word_freq = Counter(all_words).most_common(n)
        return [{'text': word, 'value': count} for word, count in word_freq]

    def generate_sentiment_report(self, df: pd.DataFrame, tweets_df: pd.DataFrame = None) -> Dict[str, Any]:
        """
        Generate comprehensive sentiment analysis report

        Args:
            df: DataFrame dengan kolom 'sentiment', 'cleaned_text', 'favorite_count', 'retweet_count', 'conversation_id_str'
            tweets_df: Optional DataFrame dari tweet.xlsx untuk menghitung jumlah replies

        Returns:
            Dictionary dengan sentiment distribution, engagement stats, wordcloud data, dan topics

        NOTE:
        - Engagement = Likes (favorite_count) + Retweets (retweet_count) + Replies (count of rows with same conversation_id)
        - Retweets menggunakan kolom retweet_count dari data
        - Replies dihitung dari banyaknya baris dengan conversation_id yang sama
        """
        total = len(df)

        # 1. Sentiment Distribution
        sentiment_counts = df['sentiment'].value_counts().to_dict()
        sentiment_distribution = {
            sentiment: {
                'count': int(count),
                'percentage': round((count / total) * 100, 2)
            }
            for sentiment, count in sentiment_counts.items()
        }

        # 2. Calculate Engagement per sentiment
        # Engagement = Likes + Retweets + Replies count
        df['engagement'] = 0

        # Add likes (favorite_count)
        if 'favorite_count' in df.columns:
            df['engagement'] += df['favorite_count'].fillna(0)

        # Add retweets (retweet_count)
        if 'retweet_count' in df.columns:
            df['engagement'] += df['retweet_count'].fillna(0)

        # Add count of replies per conversation (banyaknya baris dengan conversation_id yang sama)
        if 'conversation_id_str' in df.columns:
            reply_counts = df.groupby('conversation_id_str').size()
            df['conversation_reply_count'] = df['conversation_id_str'].map(reply_counts)
            df['engagement'] += df['conversation_reply_count'].fillna(0)

        # Sum engagement by sentiment
        sentiment_by_engagement = df.groupby('sentiment')['engagement'].sum().to_dict()
        sentiment_by_engagement = {k: int(v) for k, v in sentiment_by_engagement.items()}

        # 3. Word frequency untuk word cloud per sentiment
        wordcloud_data = {}
        for sentiment in ['positive', 'negative', 'neutral']:
            sentiment_texts = df[df['sentiment'] == sentiment]['cleaned_text']
            if len(sentiment_texts) > 0:
                wordcloud_data[sentiment] = self.get_word_frequency(sentiment_texts, n=50)
            else:
                wordcloud_data[sentiment] = []

        # 4. LDA Topic Modeling per sentiment
        topics = {}
        for sentiment in ['positive', 'negative', 'neutral']:
            sentiment_texts = df[df['sentiment'] == sentiment]['cleaned_text'].tolist()
            if len(sentiment_texts) > 0:
                topics[sentiment] = self.extract_topics_lda(sentiment_texts, n_topics=3, n_words=10)
            else:
                topics[sentiment] = []

        # 5. Metadata
        sentiment_method = 'LinearSVM' if self.model_loaded else 'rule_based_fallback'

        report = {
            'sentiment_distribution': sentiment_distribution,
            'sentiment_by_engagement': sentiment_by_engagement,
            'sentiment_by_retweet': sentiment_by_engagement,  # Backward compatibility
            'wordcloud_data': wordcloud_data,
            'topics': topics,
            'total_analyzed': total,
            'metadata': {
                'data_source': 'processed_dataframe',
                'preprocessing_steps': [
                    'emoji_conversion', 'remove_urls', 'remove_mentions',
                    'hashtag_split', 'remove_emoji', 'lowercase',
                    'normalize_chars', 'remove_special_chars', 'stopwords_removal'
                ],
                'sentiment_method': sentiment_method,
                'sentiment_model': 'LinearSVM with TfidfVectorizer (tokenizer=split, ngram_range=(1,1), min_df=1, max_df=0.95)',
                'topic_modeling': 'LDA',
                'engagement_calculation': 'likes (favorite_count) + retweets (retweet_count) + replies (conversation_reply_count)'
            }
        }

        return report
