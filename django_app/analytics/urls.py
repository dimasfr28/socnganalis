from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('', views.home, name='home'),
    path('analytics/', views.descriptive_analytics, name='descriptive_analytics'),
    path('sentiment/', views.sentiment_analysis, name='sentiment_analysis'),
    path('topic-pillar/', views.topic_pillar, name='topic_pillar'),
    path('emotion/', views.emotion_analysis, name='emotion_analysis'),
    path('recommendations/', views.recommendations, name='recommendations'),
    path('data-init/', views.data_initialization, name='data_initialization'),
    path('dataset-manager/', views.dataset_manager, name='dataset_manager'),
    path('api/analytics/', views.get_analytics_data, name='api_analytics'),
    path('api/sentiment/', views.get_sentiment_data, name='api_sentiment'),
    path('api/topic-pillars/', views.get_topic_pillar_data, name='api_topic_pillars'),
    path('api/post-detail/', views.get_post_detail, name='api_post_detail'),
    path('api/recommendations/', views.get_recommendations_data, name='api_recommendations'),
]
