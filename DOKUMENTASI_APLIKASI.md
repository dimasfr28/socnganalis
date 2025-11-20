# Catatan Dokumentasi - Social Media Analytics Tool

## 📋 Overview Aplikasi
Aplikasi web analytics untuk menganalisis data media sosial IndiHome dari Twitter/X dengan 3 halaman utama analisis.

---

## 🏠 **1. Home Page** (`/`)
### Fitur:
- **Hero Banner**: Tampilan welcome dengan tagline dan deskripsi aplikasi
- **Feature Cards**: 3 kartu fitur utama (Descriptive Analytics, Sentiment Analysis, Topic Pillar)
- **Quick Stats Preview**: Preview statistik cepat
- **Call-to-Action Buttons**: Navigasi cepat ke halaman analisis
- **Responsive Design**: Layout yang responsif untuk berbagai ukuran layar

### Teknologi:
- Django Templates
- CSS Grid & Flexbox
- Custom CSS dengan color scheme (Yellow, Teal, Navy, Coral)

---

## 📊 **2. Descriptive Analytics** (`/analytics/`)
### Fitur:
- **Summary Cards**:
  - Total Tweets
  - Total Engagement
  - Average Engagement
  - Peak Hour Activity

- **Charts & Visualizations**:
  - **Engagement by Type**: Bar chart (Likes, Replies, Retweets per tweet type)
  - **Engagement Trend**: Line chart engagement over time
  - **Engagement by Day**: Bar chart engagement per hari
  - **Peak Hours**: Bar chart aktivitas per jam

- **Tweet Type Distribution**: Analisis distribusi tipe tweet (Original, Reply, Retweet)

### Data Source:
- `tweet.xlsx` (header row 4)

### API Endpoint:
- `/api/analytics/`

### Teknologi:
- Chart.js untuk visualisasi
- Pandas untuk data processing
- FastAPI backend

---

## 😊 **3. Sentiment Analysis** (`/sentiment/`)
### Fitur:
- **Sentiment Cards**:
  - Total Positive (hijau/teal)
  - Total Negative (merah/coral)
  - Total Neutral (kuning)
  - Persentase masing-masing sentiment

- **Sentiment Distribution Chart**:
  - Pie chart distribusi sentiment (Positive, Negative, Neutral)

- **Sentiment by Engagement Chart**:
  - Pie chart total engagement berdasarkan sentiment
  - Tooltips menampilkan breakdown (Likes, Replies, Retweets)

- **Engagement Table**:
  - Tabel total engagement per sentiment

- **Word Clouds per Sentiment**:
  - 3 word clouds (Negative, Positive, Neutral)
  - Ukuran kata berdasarkan frekuensi
  - Interactive hover effects
  - Menampilkan 25 kata teratas

- **LDA Topic Modeling**:
  - Top 3 topics per sentiment
  - 3 kata teratas per topic
  - Ditampilkan di atas setiap word cloud

### Data Processing:
- **Preprocessing**:
  - Emoji conversion ke text (😊 → 'senang', 😢 → 'sedih', dll)
  - Remove URLs, mentions, hashtags
  - Lowercase conversion
  - Stopwords removal (Indonesian + domain-specific)
  - Profanity filter
  - Repeated character normalization

- **Sentiment Classification**:
  - Model: LinearSVM (`LinearSVM.pkl`)
  - Vectorizer: TF-IDF (`tfidf_vectorizer.pkl`)
  - 3 kelas: Positive, Negative, Neutral

- **Topic Modeling**:
  - Algorithm: LDA (Latent Dirichlet Allocation)
  - 3 topics per sentiment group
  - TF-IDF Vectorization

### Data Source:
- `IndiHome_all_replies.csv`

### API Endpoint:
- `/api/sentiment/`

### Teknologi:
- Chart.js
- Scikit-learn (LinearSVM, TF-IDF, LDA)
- Custom lightweight word cloud (tanpa D3.js)

---

## 🎯 **4. Topic Pillar Analysis** (`/topic-pillar/`)
### Fitur:
- **Discovered Topics Grid**:
  - Kartu untuk setiap topic yang ditemukan
  - Menampilkan label dan 5 kata kunci teratas per topic

- **Engagement by Topic Chart**:
  - Bar chart total engagement per topic
  - Engagement = Likes + Replies + Retweets
  - Tooltips detail: breakdown likes, replies, retweets, jumlah posts
  - Sorted by engagement (descending)

- **Topic Filter Dropdown**:
  - Option "All Topics" untuk melihat semua posts
  - Option per topic untuk filter posts tertentu

- **Posts Grid dengan Pagination**:
  - Menampilkan 6 posts per halaman
  - Post cards berisi:
    - Tweet Type badge
    - Topic strength score (% match)
    - Topic label (jika All Topics)
    - Caption/Full Text (dengan word wrapping untuk text panjang)
    - Engagement stats: Likes ❤️, Replies 💬, Retweets 🔁, Total 📊
  - Previous/Next buttons
  - Page indicator (Page X of Y)
  - Reset ke page 1 saat filter berubah

### Data Processing:
- **Topic Modeling**:
  - Algorithm: LDA (Latent Dirichlet Allocation)
  - Optimal K determination: GridSearchCV (range 3-11 topics)
  - Cross-validation: 3-fold CV
  - Learning method: Online learning

- **Preprocessing** (sama dengan Sentiment):
  - Emoji conversion
  - URL & mention removal
  - Hashtag CamelCase splitting
  - Stopwords & profanity filter

- **Topic Assignment**:
  - Setiap post mendapat dominant topic
  - Topic strength score (0-1)
  - Sorted by topic strength

- **Retweet Calculation** (UPDATED):
  - Matching `tweet.xlsx id_str` dengan `IndiHome_all_replies.csv conversation_id_str`
  - ID extraction dari Permalink URL: `/status/(\d+)`
  - Count jumlah rows di replies CSV yang match

### Data Source:
- `tweet.xlsx` (header row 4) - data posts utama
- `IndiHome_all_replies.csv` - untuk menghitung retweets

### API Endpoint:
- `/api/topic-pillars/`

### Teknologi:
- Chart.js
- Scikit-learn (LDA, TF-IDF, GridSearchCV)
- Client-side pagination
- CSS word-wrap untuk long text

---

## 🎨 **Design System**
### Color Palette:
- **Primary Yellow**: `rgb(251, 175, 58)` - Accent, hover effects
- **Teal**: `rgb(87, 188, 189)` - Positive sentiment, secondary accent
- **Navy**: `rgb(26, 32, 44)` - Text primary, dark backgrounds
- **Coral Red**: `rgb(227, 93, 96)` - Negative sentiment, alerts
- **Royal Blue**: `rgb(74, 85, 162)` - Charts, links
- **Light Gray**: `rgb(247, 250, 252)` - Backgrounds
- **Medium Gray**: `rgb(226, 232, 240)` - Borders, dividers
- **Dark Gray**: `rgb(45, 55, 72)` - Text secondary

### Typography:
- Font Family: 'Inter', 'Segoe UI', system fonts
- Headings: Bold weights
- Body: Regular (400), Medium (500), Semibold (600)

---

## 🔧 **Technical Stack**
### Backend:
- **FastAPI**: REST API server (port 8001)
- **Django**: Web framework & templates (port 8000)
- **Pandas**: Data processing
- **Scikit-learn**: ML models (LinearSVM, LDA, TF-IDF)
- **Python 3.x**

### Frontend:
- **HTML5 + Django Templates**
- **CSS3** (Custom, no frameworks)
- **Vanilla JavaScript** (ES6+)
- **Chart.js**: Visualisasi charts

### Deployment:
- **Docker Compose**: Multi-container orchestration
- **Nginx** (optional): Reverse proxy
- Volumes: `/home/dimas/crawling_sosmed/tweets-data`

---

## 📁 **File Structure**
```
crawling_sosmed/
├── django_app/
│   └── analytics/
│       ├── templates/
│       │   ├── base.html
│       │   ├── home.html
│       │   ├── descriptive_analytics.html
│       │   ├── sentiment_analysis.html
│       │   └── topic_pillar.html
│       ├── static/
│       │   ├── css/style.css
│       │   ├── js/
│       │   │   ├── analytics.js
│       │   │   ├── sentiment.js
│       │   │   └── topic_pillar.js
│       │   └── images/logo.png
│       ├── views.py
│       └── urls.py
├── fastapi_app/
│   ├── main.py
│   ├── data_processor.py
│   ├── sentiment_processor.py
│   └── topic_pillar_processor.py
├── tweets-data/
│   ├── tweet.xlsx
│   └── IndiHome_all_replies.csv
└── assets/model/
    ├── LinearSVM.pkl
    └── tfidf_vectorizer.pkl
```

---

## 🚀 **URLs & Navigation**
- Home: `http://localhost:8000/`
- Descriptive: `http://localhost:8000/analytics/`
- Sentiment: `http://localhost:8000/sentiment/`
- Topic Pillar: `http://localhost:8000/topic-pillar/`
- API Analytics: `http://localhost:8001/api/analytics`
- API Sentiment: `http://localhost:8001/api/sentiment`
- API Topic Pillars: `http://localhost:8001/api/topic-pillars`

---

## 📝 **Change Log**

### Version 1.2 (November 2025)
- ✅ Implemented Topic Pillar Analysis dengan LDA
- ✅ Added pagination untuk post cards (6 posts/page)
- ✅ Updated retweet calculation menggunakan IndiHome_all_replies.csv
- ✅ Added word wrapping untuk long captions
- ✅ Optimized word cloud performance (lightweight version)

### Version 1.1
- ✅ Implemented Sentiment Analysis dengan LinearSVM
- ✅ Added LDA topic modeling per sentiment
- ✅ Created custom word clouds

### Version 1.0
- ✅ Initial release
- ✅ Descriptive Analytics
- ✅ Home page dengan hero banner

---

**Last Updated**: November 2025
**Version**: 1.2
**Developer**: Dimas
