"""
Recommendation System Processor
Generates automated insights and actionable recommendations based on:
- Sentiment analysis
- Emotion analysis
- Topic pillars
- Engagement patterns
- Peak hour activity
- Word clouds
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any
from collections import Counter
import re


class RecommendationProcessor:
    """Class untuk menghasilkan rekomendasi berdasarkan analisis data"""

    def __init__(self):
        """Initialize RecommendationProcessor"""
        self.priority_levels = {
            'critical': {'color': '#ef4444', 'icon': '🔴', 'weight': 1},
            'high': {'color': '#f59e0b', 'icon': '🟠', 'weight': 2},
            'medium': {'color': '#3b82f6', 'icon': '🔵', 'weight': 3},
            'low': {'color': '#10b981', 'icon': '🟢', 'weight': 4}
        }

    def generate_recommendations(
        self,
        sentiment_data: Dict[str, Any],
        emotion_data: Dict[str, Any],
        topic_data: Dict[str, Any],
        engagement_data: Dict[str, Any],
        peak_hours_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate comprehensive recommendations based on all analytics

        Returns:
            Dictionary containing:
            - insights: Key findings from data
            - recommendations: Actionable recommendations
            - priority_actions: Top priority actions
            - performance_score: Overall performance metrics
        """
        recommendations = []

        # 1. Sentiment-based recommendations
        recommendations.extend(self._analyze_sentiment(sentiment_data))

        # 2. Emotion-based recommendations
        recommendations.extend(self._analyze_emotions(emotion_data))

        # 3. Topic-based recommendations
        recommendations.extend(self._analyze_topics(topic_data))

        # 4. Engagement-based recommendations
        recommendations.extend(self._analyze_engagement(engagement_data))

        # 5. Timing-based recommendations
        recommendations.extend(self._analyze_timing(peak_hours_data))

        # Sort by priority
        recommendations.sort(key=lambda x: self.priority_levels[x['priority']]['weight'])

        # Generate insights summary
        insights = self._generate_insights(
            sentiment_data, emotion_data, topic_data, engagement_data, peak_hours_data
        )

        # Calculate performance score
        performance_score = self._calculate_performance_score(
            sentiment_data, emotion_data, engagement_data
        )

        # Get priority actions (top 5 critical/high priority)
        priority_actions = [
            r for r in recommendations
            if r['priority'] in ['critical', 'high']
        ][:5]

        return {
            'insights': insights,
            'recommendations': recommendations,
            'priority_actions': priority_actions,
            'performance_score': performance_score,
            'total_recommendations': len(recommendations)
        }

    def _analyze_sentiment(self, sentiment_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze sentiment distribution and generate recommendations"""
        recommendations = []

        if not sentiment_data or 'sentiment_distribution' not in sentiment_data:
            return recommendations

        dist = sentiment_data['sentiment_distribution']

        # Calculate sentiment percentages
        negative_pct = dist.get('negative', {}).get('percentage', 0)
        positive_pct = dist.get('positive', {}).get('percentage', 0)
        neutral_pct = dist.get('neutral', {}).get('percentage', 0)

        # High negative sentiment
        if negative_pct > 40:
            recommendations.append({
                'category': 'Sentiment',
                'priority': 'critical',
                'title': 'High Negative Sentiment Detected',
                'description': f'{negative_pct}% of interactions are negative. Immediate action required.',
                'actionable_steps': [
                    'Analyze negative sentiment word clouds to identify key issues',
                    'Prioritize response to complaints and concerns',
                    'Create targeted campaigns to address common pain points',
                    'Set up automated alerts for negative sentiment spikes'
                ],
                'impact': 'High - Customer satisfaction at risk',
                'effort': 'High'
            })
        elif negative_pct > 25:
            recommendations.append({
                'category': 'Sentiment',
                'priority': 'high',
                'title': 'Moderate Negative Sentiment',
                'description': f'{negative_pct}% of interactions are negative. Monitor closely.',
                'actionable_steps': [
                    'Review common negative topics and address systematically',
                    'Improve response time for customer complaints',
                    'Launch customer satisfaction improvement initiatives'
                ],
                'impact': 'Medium - Potential reputation impact',
                'effort': 'Medium'
            })

        # Low positive sentiment
        if positive_pct < 30:
            recommendations.append({
                'category': 'Sentiment',
                'priority': 'high',
                'title': 'Low Positive Sentiment',
                'description': f'Only {positive_pct}% of interactions are positive. Room for improvement.',
                'actionable_steps': [
                    'Identify and replicate positive interaction patterns',
                    'Encourage positive user testimonials and reviews',
                    'Launch engagement campaigns to boost positive sentiment',
                    'Highlight success stories and positive experiences'
                ],
                'impact': 'Medium - Growth opportunity',
                'effort': 'Medium'
            })

        # High neutral sentiment
        if neutral_pct > 50:
            recommendations.append({
                'category': 'Sentiment',
                'priority': 'medium',
                'title': 'High Neutral Sentiment',
                'description': f'{neutral_pct}% of interactions are neutral. Opportunity to increase engagement.',
                'actionable_steps': [
                    'Create more engaging content to evoke emotional responses',
                    'Use storytelling to connect with audience emotionally',
                    'Implement interactive campaigns and polls',
                    'Personalize communications to increase relevance'
                ],
                'impact': 'Low - Engagement optimization',
                'effort': 'Low'
            })

        return recommendations

    def _analyze_emotions(self, emotion_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze emotion distribution and generate recommendations"""
        recommendations = []

        if not emotion_data or 'emotion_distribution' not in emotion_data:
            return recommendations

        dist = emotion_data['emotion_distribution']

        # Calculate emotion percentages
        anger_pct = dist.get('anger', {}).get('percentage', 0)
        sadness_pct = dist.get('sadness', {}).get('percentage', 0)
        fear_pct = dist.get('fear', {}).get('percentage', 0)
        joy_pct = dist.get('joy', {}).get('percentage', 0)
        disgust_pct = dist.get('disgust', {}).get('percentage', 0)

        # High anger
        if anger_pct > 15:
            recommendations.append({
                'category': 'Emotion',
                'priority': 'critical',
                'title': 'High Anger Levels Detected',
                'description': f'{anger_pct}% of interactions show anger. Critical customer dissatisfaction.',
                'actionable_steps': [
                    'Review anger-related word clouds for specific complaints',
                    'Implement immediate resolution protocols for angry customers',
                    'Train support team in de-escalation techniques',
                    'Address root causes identified in anger-related topics'
                ],
                'impact': 'Critical - Brand reputation at risk',
                'effort': 'High'
            })

        # High fear/anxiety
        if fear_pct > 5:
            recommendations.append({
                'category': 'Emotion',
                'priority': 'high',
                'title': 'Customer Anxiety Detected',
                'description': f'{fear_pct}% of interactions show fear/anxiety. Address concerns promptly.',
                'actionable_steps': [
                    'Identify sources of customer anxiety in word clouds',
                    'Provide clear, transparent communication about services',
                    'Offer reassurance and guarantees where appropriate',
                    'Create FAQ and knowledge base for common concerns'
                ],
                'impact': 'High - Trust and confidence at stake',
                'effort': 'Medium'
            })

        # High sadness/disappointment
        if sadness_pct > 10:
            recommendations.append({
                'category': 'Emotion',
                'priority': 'high',
                'title': 'High Disappointment Levels',
                'description': f'{sadness_pct}% of interactions show sadness/disappointment.',
                'actionable_steps': [
                    'Analyze disappointment triggers from word clouds',
                    'Set realistic expectations in marketing materials',
                    'Improve product/service quality in identified areas',
                    'Implement customer success programs'
                ],
                'impact': 'High - Customer retention at risk',
                'effort': 'High'
            })

        # Low joy
        if joy_pct < 25:
            recommendations.append({
                'category': 'Emotion',
                'priority': 'medium',
                'title': 'Low Joy/Satisfaction Levels',
                'description': f'Only {joy_pct}% of interactions show joy. Increase positive experiences.',
                'actionable_steps': [
                    'Study joy-related word clouds for success patterns',
                    'Replicate conditions that generate positive emotions',
                    'Celebrate customer wins and milestones',
                    'Create moments of delight in customer journey'
                ],
                'impact': 'Medium - Customer loyalty opportunity',
                'effort': 'Medium'
            })

        # High disgust
        if disgust_pct > 5:
            recommendations.append({
                'category': 'Emotion',
                'priority': 'critical',
                'title': 'Disgust/Strong Negative Reactions',
                'description': f'{disgust_pct}% of interactions show disgust. Severe quality issues.',
                'actionable_steps': [
                    'Immediately investigate disgust-related complaints',
                    'Conduct quality audit of products/services',
                    'Implement stringent quality control measures',
                    'Issue public statement if widespread issue identified'
                ],
                'impact': 'Critical - Severe reputation damage',
                'effort': 'High'
            })

        return recommendations

    def _analyze_topics(self, topic_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze topic pillars and generate recommendations"""
        recommendations = []

        if not topic_data or 'topic_engagement' not in topic_data:
            return recommendations

        topic_engagement = topic_data['topic_engagement']

        # Sort topics by engagement
        sorted_topics = sorted(
            topic_engagement,
            key=lambda x: x['total_engagement'],
            reverse=True
        )

        if len(sorted_topics) > 0:
            # High engagement topics
            top_topic = sorted_topics[0]
            recommendations.append({
                'category': 'Topics',
                'priority': 'medium',
                'title': f'Top Performing Topic: {top_topic["topic_label"]}',
                'description': f'This topic has {top_topic["total_engagement"]:,} total engagement.',
                'actionable_steps': [
                    'Create more content related to this topic',
                    'Analyze what makes this topic resonate with audience',
                    'Expand on sub-topics within this category',
                    'Use similar messaging and tone in other topics'
                ],
                'impact': 'Medium - Content strategy optimization',
                'effort': 'Low'
            })

            # Low engagement topics
            if len(sorted_topics) > 2:
                low_topic = sorted_topics[-1]
                recommendations.append({
                    'category': 'Topics',
                    'priority': 'low',
                    'title': f'Low Engagement Topic: {low_topic["topic_label"]}',
                    'description': f'This topic has only {low_topic["total_engagement"]:,} engagement.',
                    'actionable_steps': [
                        'Reevaluate relevance of this topic to audience',
                        'Consider discontinuing or restructuring this topic',
                        'Test different angles or approaches for this topic',
                        'Merge with higher-performing related topics'
                    ],
                    'impact': 'Low - Resource optimization',
                    'effort': 'Low'
                })

        return recommendations

    def _analyze_engagement(self, engagement_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze engagement patterns and generate recommendations"""
        recommendations = []

        if not engagement_data:
            return recommendations

        # Analyze engagement by type
        if 'engagement_by_type' in engagement_data:
            eng_types = engagement_data['engagement_by_type']

            # Calculate average engagement
            total_eng = sum(e['total'] for e in eng_types)
            avg_eng = total_eng / len(eng_types) if eng_types else 0

            for eng_type in eng_types:
                if eng_type['total'] < avg_eng * 0.5:
                    recommendations.append({
                        'category': 'Engagement',
                        'priority': 'medium',
                        'title': f'Low Engagement for {eng_type["type"]}',
                        'description': f'{eng_type["type"]} has below-average engagement.',
                        'actionable_steps': [
                            f'Review and optimize {eng_type["type"]} content strategy',
                            'Test different formats and messaging',
                            'Increase posting frequency for high-performing formats',
                            'A/B test different approaches'
                        ],
                        'impact': 'Medium - Engagement optimization',
                        'effort': 'Medium'
                    })

        # Overall engagement analysis
        if 'total_engagement' in engagement_data:
            total_engagement = engagement_data['total_engagement']
            total_posts = engagement_data.get('total_posts', 1)
            avg_engagement_per_post = total_engagement / total_posts if total_posts > 0 else 0

            if avg_engagement_per_post < 100:
                recommendations.append({
                    'category': 'Engagement',
                    'priority': 'high',
                    'title': 'Low Overall Engagement Rate',
                    'description': f'Average engagement per post is {avg_engagement_per_post:.0f}.',
                    'actionable_steps': [
                        'Review and revamp content strategy',
                        'Increase use of visual content (images, videos)',
                        'Post during peak engagement hours',
                        'Use trending hashtags and topics',
                        'Engage with audience through polls and questions'
                    ],
                    'impact': 'High - Visibility and reach',
                    'effort': 'Medium'
                })

        return recommendations

    def _analyze_timing(self, peak_hours_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze peak hours and generate timing recommendations"""
        recommendations = []

        if not peak_hours_data or 'peak_hours' not in peak_hours_data:
            return recommendations

        peak_hours = peak_hours_data['peak_hours']

        if peak_hours:
            peak_hours_str = ', '.join([f"{h}:00" for h in peak_hours[:3]])

            recommendations.append({
                'category': 'Timing',
                'priority': 'medium',
                'title': 'Optimize Posting Schedule',
                'description': f'Peak activity hours are: {peak_hours_str}',
                'actionable_steps': [
                    f'Schedule important posts during peak hours: {peak_hours_str}',
                    'Use social media scheduling tools for optimal timing',
                    'Test posting at different times within peak windows',
                    'Monitor engagement rates by posting time',
                    'Adjust content calendar based on peak activity patterns'
                ],
                'impact': 'Medium - Visibility and engagement',
                'effort': 'Low'
            })

        return recommendations

    def _generate_insights(
        self,
        sentiment_data: Dict[str, Any],
        emotion_data: Dict[str, Any],
        topic_data: Dict[str, Any],
        engagement_data: Dict[str, Any],
        peak_hours_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate key insights from all data"""
        insights = []

        # Sentiment insights
        if sentiment_data and 'sentiment_distribution' in sentiment_data:
            dist = sentiment_data['sentiment_distribution']
            dominant_sentiment = max(dist.items(), key=lambda x: x[1].get('percentage', 0))

            insights.append({
                'category': 'Sentiment',
                'icon': '📊',
                'title': 'Dominant Sentiment',
                'value': dominant_sentiment[0].capitalize(),
                'percentage': dominant_sentiment[1].get('percentage', 0),
                'description': f'{dominant_sentiment[1].get("percentage", 0)}% of interactions'
            })

        # Emotion insights
        if emotion_data and 'emotion_distribution' in emotion_data:
            dist = emotion_data['emotion_distribution']
            dominant_emotion = max(dist.items(), key=lambda x: x[1].get('percentage', 0))

            emotion_icons = {
                'joy': '😊', 'anger': '😡', 'sadness': '😢',
                'fear': '😨', 'surprise': '😲', 'disgust': '🤢', 'neutral': '😐'
            }

            insights.append({
                'category': 'Emotion',
                'icon': emotion_icons.get(dominant_emotion[0], '😐'),
                'title': 'Dominant Emotion',
                'value': dominant_emotion[0].capitalize(),
                'percentage': dominant_emotion[1].get('percentage', 0),
                'description': f'{dominant_emotion[1].get("percentage", 0)}% of interactions'
            })

        # Engagement insights
        if engagement_data:
            total_engagement = engagement_data.get('total_engagement', 0)
            total_posts = engagement_data.get('total_posts', 1)
            avg_engagement = total_engagement / total_posts if total_posts > 0 else 0

            insights.append({
                'category': 'Engagement',
                'icon': '🔥',
                'title': 'Average Engagement',
                'value': f'{avg_engagement:.0f}',
                'description': f'per post ({total_engagement:,} total)'
            })

        # Topic insights
        if topic_data and 'topic_engagement' in topic_data:
            topic_engagement = topic_data['topic_engagement']
            if topic_engagement:
                top_topic = max(topic_engagement, key=lambda x: x['total_engagement'])

                insights.append({
                    'category': 'Topics',
                    'icon': '🎯',
                    'title': 'Top Topic',
                    'value': top_topic['topic_label'],
                    'description': f'{top_topic["total_engagement"]:,} total engagement'
                })

        # Timing insights
        if peak_hours_data and 'peak_hours' in peak_hours_data:
            peak_hours = peak_hours_data['peak_hours']
            if peak_hours:
                peak_hours_str = f"{peak_hours[0]}:00-{peak_hours[-1]}:00"

                insights.append({
                    'category': 'Timing',
                    'icon': '⏰',
                    'title': 'Peak Hours',
                    'value': peak_hours_str,
                    'description': 'Highest activity window'
                })

        return insights

    def _calculate_performance_score(
        self,
        sentiment_data: Dict[str, Any],
        emotion_data: Dict[str, Any],
        engagement_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate overall performance score (0-100)"""

        scores = {
            'sentiment_score': 0,
            'emotion_score': 0,
            'engagement_score': 0,
            'overall_score': 0
        }

        # Sentiment score (0-100)
        if sentiment_data and 'sentiment_distribution' in sentiment_data:
            dist = sentiment_data['sentiment_distribution']
            positive_pct = dist.get('positive', {}).get('percentage', 0)
            negative_pct = dist.get('negative', {}).get('percentage', 0)

            # Score = positive% - negative% + 50 (normalized to 0-100)
            sentiment_score = min(100, max(0, positive_pct - negative_pct + 50))
            scores['sentiment_score'] = round(sentiment_score, 1)

        # Emotion score (0-100)
        if emotion_data and 'emotion_distribution' in emotion_data:
            dist = emotion_data['emotion_distribution']
            joy_pct = dist.get('joy', {}).get('percentage', 0)
            anger_pct = dist.get('anger', {}).get('percentage', 0)
            sadness_pct = dist.get('sadness', {}).get('percentage', 0)
            disgust_pct = dist.get('disgust', {}).get('percentage', 0)

            # Score = joy% - (anger% + sadness% + disgust%) + 50
            emotion_score = min(100, max(0, joy_pct - (anger_pct + sadness_pct + disgust_pct) + 50))
            scores['emotion_score'] = round(emotion_score, 1)

        # Engagement score (0-100) - relative to benchmarks
        if engagement_data:
            total_posts = engagement_data.get('total_posts', 1)
            total_engagement = engagement_data.get('total_engagement', 0)
            avg_engagement = total_engagement / total_posts if total_posts > 0 else 0

            # Benchmark: 0-50 = poor, 50-100 = fair, 100-200 = good, 200+ = excellent
            # Normalize to 0-100 scale
            if avg_engagement >= 200:
                engagement_score = 100
            elif avg_engagement >= 100:
                engagement_score = 75
            elif avg_engagement >= 50:
                engagement_score = 50
            else:
                engagement_score = (avg_engagement / 50) * 50

            scores['engagement_score'] = round(engagement_score, 1)

        # Overall score (weighted average)
        overall_score = (
            scores['sentiment_score'] * 0.35 +
            scores['emotion_score'] * 0.35 +
            scores['engagement_score'] * 0.30
        )
        scores['overall_score'] = round(overall_score, 1)

        # Add rating
        if overall_score >= 80:
            scores['rating'] = 'Excellent'
            scores['rating_icon'] = '🌟'
            scores['rating_color'] = '#10b981'
        elif overall_score >= 60:
            scores['rating'] = 'Good'
            scores['rating_icon'] = '👍'
            scores['rating_color'] = '#3b82f6'
        elif overall_score >= 40:
            scores['rating'] = 'Fair'
            scores['rating_icon'] = '⚠️'
            scores['rating_color'] = '#f59e0b'
        else:
            scores['rating'] = 'Poor'
            scores['rating_icon'] = '❌'
            scores['rating_color'] = '#ef4444'

        return scores
