// Sentiment Analysis JavaScript
document.addEventListener('DOMContentLoaded', function() {
    loadSentimentData();
});

async function loadSentimentData() {
    try {
        console.log('Fetching sentiment data from /api/sentiment/...');
        const response = await fetch('/api/sentiment/');
        console.log('Response received:', response.status);

        const data = await response.json();
        console.log('Data parsed:', data);

        if (data.error) {
            console.error('Error:', data.error);
            return;
        }

        console.log('Sentiment data loaded successfully:', data);

        // Update sentiment cards
        updateSentimentCards(data.sentiment_distribution, data.total_analyzed);

        // Create pie chart for sentiment by engagement
        const sentimentEngagement = data.sentiment_by_engagement || data.sentiment_by_retweet;
        createSentimentEngagementChart(sentimentEngagement);

        // Populate sentiment engagement table
        populateSentimentTable(sentimentEngagement);

        // Create word clouds with LDA topics if available - simple lightweight version
        const negativeTopics = data.topics?.negative || [];
        const positiveTopics = data.topics?.positive || [];
        const neutralTopics = data.topics?.neutral || [];

        createWordCloud('wordcloud-negative', data.wordcloud_data.negative, 'rgb(227, 93, 96)', negativeTopics);
        createWordCloud('wordcloud-positive', data.wordcloud_data.positive, 'rgb(87, 188, 189)', positiveTopics);
        createWordCloud('wordcloud-neutral', data.wordcloud_data.neutral, 'rgb(251, 175, 58)', neutralTopics);

    } catch (error) {
        console.error('Error loading sentiment data:', error);
    }
}

function updateSentimentCards(sentimentDist, total) {
    console.log('updateSentimentCards called with:', { sentimentDist, total });

    // Update total
    const totalEl = document.getElementById('total-analyzed');
    console.log('total-analyzed element:', totalEl);
    if (totalEl) {
        totalEl.textContent = total.toLocaleString();
        console.log('Updated total to:', total);
    }

    // Update each sentiment
    const sentiments = ['positive', 'neutral', 'negative'];
    sentiments.forEach(sentiment => {
        const data = sentimentDist[sentiment] || { count: 0, percentage: 0 };
        const countEl = document.getElementById(`${sentiment}-count`);
        const percentEl = document.getElementById(`${sentiment}-percentage`);

        console.log(`${sentiment}: count=${data.count}, percentage=${data.percentage}`, { countEl, percentEl });

        if (countEl) countEl.textContent = data.count.toLocaleString();
        if (percentEl) percentEl.textContent = `${data.percentage}%`;
    });
}

function createSentimentEngagementChart(sentimentEngagement) {
    const ctx = document.getElementById('sentimentEngagementChart').getContext('2d');

    const labels = Object.keys(sentimentEngagement).map(s =>
        s.charAt(0).toUpperCase() + s.slice(1)
    );
    const values = Object.values(sentimentEngagement);

    // Consistent color palette matching Post Type by Engagement
    const sentimentColorMap = {
        'Negative': 'rgb(227, 93, 96)',    // Coral red
        'Neutral': 'rgb(251, 175, 58)',    // Neutral yellow - primary
        'Positive': 'rgb(87, 188, 189)'    // Teal
    };

    const backgroundColors = labels.map(label => sentimentColorMap[label] || '#718096');

    // Plugin: draw curved arrows + label for all sentiments
    const arrowColors = [
        'rgba(227, 93, 96, 0.95)',   // Negative - coral red
        'rgba(251, 175, 58, 0.95)',  // Neutral - yellow
        'rgba(87, 188, 189, 0.95)'   // Positive - teal
    ];

    const arrowPlugin = {
        id: 'sentimentArrowAll',
        afterDraw: (chart) => {
            try {
                if (!chart || !chart.ctx) return;
                const ctx = chart.ctx;
                const dataset = chart.data.datasets && chart.data.datasets[0];
                if (!dataset) return;
                const values = dataset.data || [];
                if (!values.length) return;
                const meta = chart.getDatasetMeta(0);
                if (!meta || !meta.data) return;
                const chartArea = chart.chartArea;
                const cx = (chartArea.left + chartArea.right) / 2;
                const cy = (chartArea.top + chartArea.bottom) / 2;

                for (let i = 0; i < values.length; i++) {
                    const arc = meta.data[i];
                    if (!arc) continue;
                    const start = arc.startAngle;
                    const end = arc.endAngle;
                    const mid = (start + end) / 2;
                    const outerRadius = arc.outerRadius || Math.min((chartArea.right - chartArea.left) / 2, (chartArea.bottom - chartArea.top) / 2);

                    // Start point (on arc)
                    const sx = cx + Math.cos(mid) * outerRadius;
                    const sy = cy + Math.sin(mid) * outerRadius;

                    // End point (curved outward)
                    const curveDist = 26 + 4 * Math.sin(i * Math.PI / values.length);
                    const ex = cx + Math.cos(mid) * (outerRadius + curveDist);
                    const ey = cy + Math.sin(mid) * (outerRadius + curveDist);

                    // Control point for curve
                    const ctrlAngle = mid + (i % 2 === 0 ? 0.22 : -0.22);
                    const ctrlRadius = outerRadius + curveDist * 0.45;
                    const cx1 = cx + Math.cos(ctrlAngle) * ctrlRadius;
                    const cy1 = cy + Math.sin(ctrlAngle) * ctrlRadius;

                    ctx.save();
                    ctx.strokeStyle = arrowColors[i % arrowColors.length];
                    ctx.lineWidth = 2.1;
                    ctx.beginPath();
                    ctx.moveTo(sx, sy);
                    ctx.quadraticCurveTo(cx1, cy1, ex, ey);
                    ctx.stroke();

                    // Arrow head
                    const angle = Math.atan2(ey - cy1, ex - cx1);
                    const headlen = 7;
                    ctx.beginPath();
                    ctx.moveTo(ex, ey);
                    ctx.lineTo(ex - headlen * Math.cos(angle - Math.PI / 6), ey - headlen * Math.sin(angle - Math.PI / 6));
                    ctx.lineTo(ex - headlen * Math.cos(angle + Math.PI / 6), ey - headlen * Math.sin(angle + Math.PI / 6));
                    ctx.closePath();
                    ctx.fillStyle = arrowColors[i % arrowColors.length];
                    ctx.fill();

                    // Label (sentiment name)
                    const label = (chart.data.labels && chart.data.labels[i]) ? chart.data.labels[i] : '';
                    ctx.font = '12px Montserrat, sans-serif';
                    ctx.fillStyle = arrowColors[i % arrowColors.length];
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    const lx = ex + Math.cos(mid) * 18;
                    const ly = ey + Math.sin(mid) * 7;
                    ctx.fillText(label, lx, ly);
                    ctx.restore();
                }
            } catch (e) {
                console.error('Arrow plugin error', e);
            }
        }
    };

    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: backgroundColors,
                borderWidth: 3,
                borderColor: '#fff'
            }]
        },
        plugins: [arrowPlugin],
        options: {
            responsive: true,
            maintainAspectRatio: true,
            layout: {
                padding: 50
            },
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        padding: 0,
                        font: {
                            size: 0
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return `${label}: ${value.toLocaleString()} engagement (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

function populateSentimentTable(sentimentEngagement) {
    const table = document.getElementById('sentimentEngagementTable');
    if (!table) return;

    table.innerHTML = '';

    // Define order: Negative, Neutral, Positive
    const order = ['negative', 'neutral', 'positive'];
    const labels = {
        'negative': 'Negative',
        'neutral': 'Neutral',
        'positive': 'Positive'
    };

    order.forEach(sentiment => {
        if (sentimentEngagement.hasOwnProperty(sentiment)) {
            const tr = document.createElement('tr');
            const td1 = document.createElement('td');
            td1.textContent = labels[sentiment];
            const td2 = document.createElement('td');
            td2.textContent = sentimentEngagement[sentiment].toLocaleString();
            tr.appendChild(td1);
            tr.appendChild(td2);
            table.appendChild(tr);
        }
    });
}

function createWordCloud(containerId, wordData, color, topics = []) {
    const container = document.getElementById(containerId);

    if (!wordData || wordData.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #718096;">No data available</p>';
        return;
    }

    // Clear previous content
    container.innerHTML = '';

    // Add topics info if available (limit to 2 topics, 3 words each)
    if (topics && topics.length > 0) {
        const topicsDiv = document.createElement('div');
        topicsDiv.style.cssText = 'margin-bottom: 1rem; padding: 0.75rem; background: rgba(0,0,0,0.03); border-radius: 8px; font-size: 0.8rem;';

        let topicsHTML = '<strong>Top Topics:</strong><br>';
        const limitedTopics = topics.slice(0, 3); // Show 3 topics
        limitedTopics.forEach((topic, idx) => {
            const topWords = topic.words.slice(0, 3).join(', '); // 3 words per topic
            topicsHTML += `<div style="margin-top: 0.4rem;"><em>Topic ${idx + 1}:</em> ${topWords}</div>`;
        });

        topicsDiv.innerHTML = topicsHTML;
        container.appendChild(topicsDiv);
    }

    // Create simple word cloud div - lightweight version without D3 cloud layout
    const cloudDiv = document.createElement('div');
    cloudDiv.className = 'wordcloud-canvas';
    cloudDiv.style.cssText = `
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        justify-content: center;
        align-items: flex-start;
        padding: 1.5rem;
        min-height: 200px;
        overflow: visible;
    `;

    // Take top 25 words to show more content
    const topWords = wordData.slice(0, 25);

    // Calculate font sizes
    const maxValue = Math.max(...topWords.map(d => d.value));
    const minValue = Math.min(...topWords.map(d => d.value));

    topWords.forEach(word => {
        const span = document.createElement('span');

        // Simple linear scaling for font size (smaller range: 12px to 24px)
        const fontSize = minValue === maxValue
            ? 14
            : 12 + ((word.value - minValue) / (maxValue - minValue)) * 12;

        // Simple opacity scaling
        const opacity = 0.6 + ((word.value - minValue) / (maxValue - minValue)) * 0.4;

        span.textContent = word.text;
        span.style.cssText = `
            font-size: ${fontSize}px;
            font-weight: 600;
            color: ${color};
            opacity: ${opacity};
            transition: all 0.2s ease;
            cursor: pointer;
            white-space: nowrap;
        `;

        span.addEventListener('mouseenter', function() {
            this.style.opacity = '1';
            this.style.transform = 'scale(1.1)';
        });

        span.addEventListener('mouseleave', function() {
            this.style.opacity = opacity;
            this.style.transform = 'scale(1)';
        });

        cloudDiv.appendChild(span);
    });

    container.appendChild(cloudDiv);
}
