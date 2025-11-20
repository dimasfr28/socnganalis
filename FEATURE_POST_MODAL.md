# Feature: Post Detail Modal

## Overview
Fitur pop-up modal yang muncul ketika user mengklik salah satu post card di halaman Topic Pillar Analysis. Modal menampilkan informasi detail tambahan yang tidak ditampilkan di card.

## Fitur yang Ditambahkan

### 1. **Hashtag Extraction**
- Ekstraksi semua hashtag yang digunakan dalam post
- Ditampilkan sebagai tag dengan gradient warna (yellow-coral)
- Jika tidak ada hashtag, tampilkan pesan "No hashtags found"

### 2. **Reply Word Cloud**
- Word cloud dari kata-kata yang sering muncul di replies post tersebut
- Data diambil dari `IndiHome_all_replies.csv` dengan matching:
  - `tweet.xlsx id_str` == `IndiHome_all_replies.csv conversation_id_str`
- Preprocessing sama dengan sentiment analysis:
  - Emoji conversion
  - URL & mention removal
  - Stopwords filtering
  - Profanity filter
- Top 30 kata yang paling sering muncul
- Ukuran font dan opacity berdasarkan frekuensi kata
- Hover effect untuk interaktivitas

### 3. **Post Information**
- Caption lengkap
- Engagement metrics (Likes, Replies)
- Tweet Type
- Jumlah replies yang dianalisis

## Technical Implementation

### Backend Changes

#### 1. **FastAPI Processor** (`topic_pillar_processor.py`)

**New Functions:**
```python
def extract_hashtags(text)
    # Extract hashtags menggunakan regex r'#(\w+)'

def get_post_detail(tweet_file_path, permalink)
    # Main function untuk mendapatkan detail post
    # Returns: hashtags, wordcloud_data, reply_count, dll
```

**Proses:**
1. Load tweet.xlsx dan cari post by permalink
2. Extract hashtags dari caption
3. Extract id_str dari permalink URL
4. Load IndiHome_all_replies.csv
5. Filter replies where conversation_id_str == id_str
6. Combine semua reply texts
7. Preprocess combined text
8. Generate word frequency (Counter)
9. Return top 30 words

#### 2. **FastAPI Endpoint** (`main.py`)
```python
@app.get("/api/post-detail")
def get_post_detail_api(permalink: str)
    # GET endpoint dengan query parameter 'permalink'
```

#### 3. **Django View Proxy** (`views.py`)
```python
def get_post_detail(request)
    # Proxy to FastAPI
    # URL encode permalink parameter
```

#### 4. **Django URL** (`urls.py`)
```python
path('api/post-detail/', views.get_post_detail, name='api_post_detail')
```

### Frontend Changes

#### 1. **CSS Styles** (`style.css`)

**New Classes:**
- `.modal-overlay` - Overlay background dengan blur
- `.modal-container` - Container modal dengan border radius
- `.modal-header` - Header dengan close button
- `.modal-body` - Body content
- `.modal-loading` - Loading state dengan spinner
- `.modal-section` - Section untuk hashtags & wordcloud
- `.hashtag-tag` - Tag styling dengan gradient
- `.modal-wordcloud` - Word cloud container
- `.modal-wordcloud-word` - Individual word styling

**Animations:**
- `fadeIn` - Fade in overlay
- `slideUp` - Slide up modal container
- `spin` - Spinner rotation

**Enhancements:**
- Post cards now have `cursor: pointer`
- Hover effect: `transform: translateY(-5px)`

#### 2. **HTML Template** (`topic_pillar.html`)

**Modal Structure:**
```html
<div id="postModal" class="modal-overlay">
    <div class="modal-container">
        <div class="modal-header">
            <h3>Post Details</h3>
            <button class="modal-close" onclick="closePostModal()">×</button>
        </div>
        <div class="modal-body" id="modalBody">
            <!-- Dynamic content -->
        </div>
    </div>
</div>
```

#### 3. **JavaScript** (`topic_pillar.js`)

**New Functions:**

```javascript
function openPostModal(permalink)
    // Open modal with loading state
    // Fetch data from /api/post-detail/
    // Render modal content

function closePostModal()
    // Close modal by removing 'active' class

function renderPostDetails(data, container)
    // Render post info, hashtags, word cloud

// Event listeners:
- Click outside modal to close
- ESC key to close
- Click on post card to open modal
```

**Word Cloud Rendering:**
- Font size range: 14px - 32px
- Opacity range: 0.5 - 1.0
- Based on word frequency (linear scaling)

## User Interaction Flow

1. User mengklik salah satu post card
2. Modal muncul dengan loading spinner
3. JavaScript fetch data dari `/api/post-detail/?permalink=...`
4. Django proxy request ke FastAPI
5. FastAPI process data:
   - Extract hashtags
   - Load & filter replies
   - Generate word cloud data
6. Response dikirim kembali ke frontend
7. Modal render data:
   - Post caption & meta info
   - Hashtag tags
   - Word cloud visualization
8. User bisa:
   - Hover word cloud items (scale effect)
   - Klik close button (×)
   - Klik outside modal area
   - Tekan ESC key
9. Modal tertutup

## Data Flow

```
User Click Post Card
    ↓
JavaScript: openPostModal(permalink)
    ↓
Fetch: GET /api/post-detail/?permalink=...
    ↓
Django View: get_post_detail()
    ↓
Proxy to FastAPI: http://fastapi:8001/api/post-detail?permalink=...
    ↓
FastAPI: get_post_detail_api()
    ↓
Processor: get_post_detail(tweet_file_path, permalink)
    ↓
1. Load tweet.xlsx → find post
2. Extract hashtags from Caption
3. Extract id_str from Permalink
4. Load IndiHome_all_replies.csv
5. Filter: conversation_id_str == id_str
6. Combine reply texts → preprocess
7. Counter word frequency → top 30
    ↓
Return JSON:
{
    "permalink": "...",
    "caption": "...",
    "hashtags": ["tag1", "tag2", ...],
    "wordcloud_data": [
        {"text": "word", "value": count},
        ...
    ],
    "reply_count": 20,
    "likes": 100,
    "replies": 50,
    "tweet_type": "Original Tweet",
    "date": "..."
}
    ↓
JavaScript: renderPostDetails()
    ↓
Modal displays content
```

## API Endpoints

### `/api/post-detail/` (Django - Proxy)
- **Method**: GET
- **Query Params**:
  - `permalink` (required) - Full permalink URL
- **Response**: JSON with post details

### `/api/post-detail` (FastAPI - Backend)
- **Method**: GET
- **Query Params**:
  - `permalink` (required) - URL-encoded permalink
- **Response**:
```json
{
    "permalink": "string",
    "caption": "string",
    "hashtags": ["string"],
    "wordcloud_data": [
        {"text": "string", "value": int}
    ],
    "reply_count": int,
    "likes": int,
    "replies": int,
    "tweet_type": "string",
    "date": "string"
}
```

## Files Modified

### Backend:
1. `/home/dimas/crawling_sosmed/fastapi_app/topic_pillar_processor.py`
   - Added `extract_hashtags()`
   - Added `get_post_detail()`

2. `/home/dimas/crawling_sosmed/fastapi_app/main.py`
   - Import `get_post_detail`
   - Added endpoint `/api/post-detail`

3. `/home/dimas/crawling_sosmed/django_app/analytics/views.py`
   - Added `get_post_detail()` view

4. `/home/dimas/crawling_sosmed/django_app/analytics/urls.py`
   - Added route `api/post-detail/`

### Frontend:
5. `/home/dimas/crawling_sosmed/django_app/analytics/static/css/style.css`
   - Added modal styles (~235 lines)
   - Added animations
   - Enhanced post-card hover

6. `/home/dimas/crawling_sosmed/django_app/analytics/templates/topic_pillar.html`
   - Added modal HTML structure
   - Updated JS version to v1.3

7. `/home/dimas/crawling_sosmed/django_app/analytics/static/js/topic_pillar.js`
   - Added `openPostModal()`
   - Added `closePostModal()`
   - Added `renderPostDetails()`
   - Added click event listener on post cards
   - Added ESC key & outside click handlers

## Design Considerations

### Performance:
- Modal loads asynchronously (loading spinner)
- Word cloud limited to top 30 words
- Lightweight rendering (no D3.js)
- CSS animations (hardware accelerated)

### UX:
- Multiple ways to close modal (×, ESC, outside click)
- Loading feedback
- Error handling with user-friendly messages
- Hover effects for interactivity
- Responsive design

### Styling:
- Consistent with existing design system
- Gradient colors matching brand (yellow-coral)
- Smooth animations (0.3s ease)
- Backdrop blur effect
- Box shadows for depth

## Testing Checklist

- [x] API endpoint returns correct data
- [x] Hashtag extraction works
- [x] Word cloud data generated from replies
- [x] Modal opens on card click
- [x] Modal closes on × button
- [x] Modal closes on ESC key
- [x] Modal closes on outside click
- [ ] Test with post without hashtags
- [ ] Test with post without replies
- [ ] Test responsive design (mobile)
- [ ] Test loading states
- [ ] Test error states

## Future Enhancements

1. **Sentiment Analysis per Reply**
   - Show sentiment distribution in replies
   - Color-code word cloud by sentiment

2. **Time-based Analysis**
   - Show reply timeline
   - Peak reply hours

3. **User Mentions Analysis**
   - Most mentioned users in replies
   - User network graph

4. **Export Functionality**
   - Export word cloud as image
   - Export hashtags list

5. **Filtering**
   - Filter replies by date range
   - Filter by sentiment

## Version
- **Current Version**: 1.3
- **Date**: November 2025
- **Developer**: Dimas
