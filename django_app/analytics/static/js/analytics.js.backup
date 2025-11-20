// Fetch analytics data and populate charts
document.addEventListener("DOMContentLoaded", function () {
  fetchAnalyticsData();
});

let analyticsData = null;

function fetchAnalyticsData() {
  // Determine API host: in Docker compose use 'fastapi', in dev use 'localhost'
  const apiHost = window.location.hostname === "localhost" ? "localhost:8001" : "fastapi:8001";
  const apiUrl = `http://${apiHost}/api/analytics`;

  console.log("Fetching from:", apiUrl);

  fetch(apiUrl)
    .then((response) => {
      console.log("Response status:", response.status);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    })
    .then((data) => {
      analyticsData = data;
      console.log("API Response:", data);

      if (data.error) {
        console.error("API Error:", data.error);
        return;
      }

      // Update metrics from basic stats
      const basic = data.basic || {};
      console.log("Basic stats:", basic);

      const postsEl = document.getElementById("total_posts");
      const repliesEl = document.getElementById("total_replies");
      const likesEl = document.getElementById("total_likes");
      const retweetsEl = document.getElementById("total_retweets");

      if (postsEl) postsEl.textContent = basic.total_posts || 0;
      if (repliesEl) repliesEl.textContent = basic.total_replies || 0;
      if (likesEl) likesEl.textContent = basic.total_likes || 0;
      if (retweetsEl) retweetsEl.textContent = basic.total_retweets || 0;

      // Update delta indicators
      updateDeltaIndicators(basic);

      // Initialize charts with real data
      initializeCharts(data);

      // Render peak activity hours cards and clustering
      if (data.peak_activity_hours) {
        renderPeakActivityHours(data.peak_activity_hours);
      }

      // Fill classic table for engagement by type
      if (data.engagement_by_type) {
        const table = document.getElementById('engagementTable');
        if (table) {
          table.innerHTML = '';
          data.engagement_by_type.forEach(row => {
            const tr = document.createElement('tr');
            const td1 = document.createElement('td');
            td1.textContent = row.type;
            const td2 = document.createElement('td');
            td2.textContent = row.total;
            td2.style.textAlign = 'right';
            td2.style.fontWeight = '600'; // semi-bold
            tr.appendChild(td1);
            tr.appendChild(td2);
            table.appendChild(tr);
          });
        }
      }
    })
    .catch((error) => {
      console.error("Error fetching analytics data:", error);
      // Try with localhost as fallback
      if (!apiHost.includes("localhost")) {
        console.log("Retrying with localhost...");
        fetch("http://localhost:8001/api/analytics")
          .then((r) => r.json())
          .then((data) => {
            analyticsData = data;
            console.log("Fallback successful:", data);
            const basic = data.basic || {};
            if (document.getElementById("total_posts")) document.getElementById("total_posts").textContent = basic.total_posts || 0;
            if (document.getElementById("total_replies")) document.getElementById("total_replies").textContent = basic.total_replies || 0;
            if (document.getElementById("total_likes")) document.getElementById("total_likes").textContent = basic.total_likes || 0;
            if (document.getElementById("total_retweets")) document.getElementById("total_retweets").textContent = basic.total_retweets || 0;
            initializeCharts(data);
          })
          .catch((err) => console.error("Fallback failed:", err));
      }
    });
}

function initializeCharts(data) {
  data = data || {};
  console.log("initializeCharts called with:", data);

  // Engagement by Post Type Chart
  const engagementCtx = document.getElementById("engagementChart");
  if (engagementCtx && data.engagement_by_type) {
    console.log("Rendering engagement chart with:", data.engagement_by_type);
    const typeData = data.engagement_by_type;
    const labels = typeData.map((t) => t.type);
    const values = typeData.map((t) => t.total);
    // Neutral color palette - dominated by neutral yellow rgb(251, 175, 58)
    const colors = [
      "rgb(251, 175, 58)",   // Neutral yellow - primary
      "rgb(21, 19, 46)",     // Deep navy
      "rgb(87, 188, 189)",   // Teal
      "rgb(227, 93, 96)",    // Coral red
      "rgb(74, 110, 229)",   // Royal blue
      "rgb(251, 175, 58)",   // Repeat yellow for emphasis
      "rgb(87, 188, 189)"    // Repeat teal
    ];

    // Plugin: draw curved arrows + label for all categories (label only)
    const arrowColors = [
      'rgba(251,175,58,0.95)', // animated_gif - yellow
      'rgba(21,19,46,0.95)',   // link - navy
      'rgba(87,188,189,0.95)', // photo - teal
      'rgba(227,93,96,0.95)',  // status - coral
      'rgba(74,110,229,0.95)'  // video - blue
    ];
    const arrowPlugin = {
      id: 'engagementArrowAll',
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
            // End point (curved outward, less curve)
            const curveDist = 26 + 4 * Math.sin(i * Math.PI / values.length); // less curve
            const ex = cx + Math.cos(mid) * (outerRadius + curveDist);
            const ey = cy + Math.sin(mid) * (outerRadius + curveDist);
            // Control point for curve (gentler)
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
            // Label (only category name)
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
          // swallow drawing errors
          console.error('Arrow plugin error', e);
        }
      }
    };

    new Chart(engagementCtx, {
      type: "doughnut",
      data: {
        labels: labels,
        datasets: [
          {
            label: "Post Type Distribution",
            data: values,
            backgroundColor: colors.slice(0, labels.length),
            borderColor: "#fff",
            borderWidth: 3,
          },
        ],
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
            position: "top",
            labels: {
              padding: 0,
              font: {
                size: 0,
              },
            },
          },
          tooltip: {
            callbacks: {
              label: function(context) {
                return context.label + ': ' + context.parsed + ' engagements';
              }
            }
          }
        },
      },
    });
  } else {
    console.warn("Engagement chart not found or no data:", { engagementCtx, data: data.engagement_by_type });
  }

  // Peak Hours Chart
  const peakHoursCtx = document.getElementById("peakHoursChart");
  if (peakHoursCtx && data.peak_hours && !data.peak_hours.error) {
    console.log("Rendering peak hours chart with:", data.peak_hours);
    const peak = data.peak_hours;
    // Create hourly distribution from peak hours data
    const labels = Array.from({ length: 24 }, (_, i) => i.toString().padStart(2, "0") + ":00");
    const values = Array(24).fill(0);

    // Highlight peak hour range
    const minHour = peak.min_hour || 0;
    const maxHour = peak.max_hour || 23;
    for (let i = minHour; i <= maxHour && i < 24; i++) {
      values[i] = peak.count / Math.max(1, maxHour - minHour + 1);
    }

    new Chart(peakHoursCtx, {
      type: "bar",
      data: {
        labels: labels,
        datasets: [
          {
            label: "Activity Count",
            data: values,
            backgroundColor: "rgb(251, 175, 58)",  // Neutral yellow primary
            borderColor: "rgb(227, 93, 96)",       // Coral red accent
            borderWidth: 2,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
          legend: {
            display: true,
          },
        },
        scales: {
          y: {
            beginAtZero: true,
          },
        },
      },
    });
  } else {
    console.warn("Peak hours chart not found or no data:", { peakHoursCtx, data: data.peak_hours });
  }

  // Hashtags Chart
  const hashtagsCtx = document.getElementById("hashtagsChart");
  if (hashtagsCtx && data.hashtags) {
    console.log("Rendering hashtags chart with:", data.hashtags);
    const hashtagData = data.hashtags;
    const labels = hashtagData.map((h) => h.hashtag);
    const values = hashtagData.map((h) => h.count);

    // Gradient colors for hashtags
    const hashtagColors = values.map((value, index) => {
      const colors = [
        'rgba(251, 175, 58, 0.85)',  // Yellow
        'rgba(87, 188, 189, 0.85)',  // Teal
        'rgba(227, 93, 96, 0.85)',   // Coral
        'rgba(74, 110, 229, 0.85)',  // Blue
        'rgba(21, 19, 46, 0.85)',    // Navy
      ];
      return colors[index % colors.length];
    });

    new Chart(hashtagsCtx, {
      type: "bar",
      data: {
        labels: labels,
        datasets: [
          {
            label: "Hashtag Count",
            data: values,
            backgroundColor: hashtagColors,
            borderWidth: 0,
            borderRadius: 6,
            borderSkipped: false,
          },
        ],
      },
      options: {
        indexAxis: "y",
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
          legend: {
            display: false,
          },
          tooltip: {
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            titleFont: {
              family: 'Montserrat, sans-serif',
              size: 13
            },
            bodyFont: {
              family: 'Montserrat, sans-serif',
              size: 12
            },
            padding: 12,
            cornerRadius: 8,
            callbacks: {
              label: function(context) {
                return 'Count: ' + context.parsed.x;
              }
            }
          }
        },
        scales: {
          x: {
            beginAtZero: true,
            grid: {
              color: 'rgba(0, 0, 0, 0.05)',
              drawBorder: false,
            },
            ticks: {
              font: {
                family: 'Montserrat, sans-serif',
                size: 11
              }
            }
          },
          y: {
            grid: {
              display: false,
            },
            ticks: {
              font: {
                family: 'Montserrat, sans-serif',
                size: 11,
                weight: '500'
              }
            }
          }
        },
      },
    });
  } else {
    console.warn("Hashtags chart not found or no data:", { hashtagsCtx, data: data.hashtags });
  }

  // Day Engagement Chart
  const dayEngagementCtx = document.getElementById("dayEngagementChart");
  if (dayEngagementCtx && data.engagement_by_day) {
    console.log("Rendering day engagement chart with:", data.engagement_by_day);
    const dayData = data.engagement_by_day;
    const labels = dayData.map((d) => d.day);
    const values = dayData.map((d) => d.engagement);

    // Gradient colors for each day
    const dayColors = [
      'rgba(251, 175, 58, 0.8)',   // Monday - Yellow
      'rgba(87, 188, 189, 0.8)',   // Tuesday - Teal
      'rgba(227, 93, 96, 0.8)',    // Wednesday - Coral
      'rgba(74, 110, 229, 0.8)',   // Thursday - Blue
      'rgba(251, 175, 58, 0.8)',   // Friday - Yellow
      'rgba(87, 188, 189, 0.6)',   // Saturday - Teal lighter
      'rgba(227, 93, 96, 0.6)',    // Sunday - Coral lighter
    ];

    new Chart(dayEngagementCtx, {
      type: "bar",
      data: {
        labels: labels,
        datasets: [
          {
            label: "Total Engagement",
            data: values,
            backgroundColor: dayColors,
            borderWidth: 0,
            borderRadius: 8,
            borderSkipped: false,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
          legend: {
            display: false,
          },
          tooltip: {
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            titleFont: {
              family: 'Montserrat, sans-serif',
              size: 13
            },
            bodyFont: {
              family: 'Montserrat, sans-serif',
              size: 12
            },
            padding: 12,
            cornerRadius: 8,
            callbacks: {
              label: function(context) {
                return 'Engagement: ' + context.parsed.y;
              }
            }
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            grid: {
              color: 'rgba(0, 0, 0, 0.05)',
              drawBorder: false,
            },
            ticks: {
              font: {
                family: 'Montserrat, sans-serif',
                size: 11
              }
            }
          },
          x: {
            grid: {
              display: false,
            },
            ticks: {
              font: {
                family: 'Montserrat, sans-serif',
                size: 11
              }
            }
          }
        },
      },
    });
  } else {
    console.warn("Day engagement chart not found or no data:", { dayEngagementCtx, data: data.engagement_by_day });
  }
}

function updateDeltaIndicators(basic) {
  // Update delta indicators with color and arrow
  const metrics = [
    { id: 'delta_posts', delta: basic.delta_posts },
    { id: 'delta_replies', delta: basic.delta_replies },
    { id: 'delta_likes', delta: basic.delta_likes },
    { id: 'delta_retweets', delta: basic.delta_retweets },
  ];

  metrics.forEach(metric => {
    const element = document.getElementById(metric.id);
    if (element) {
      const value = metric.delta || 0;
      const arrow = value > 0 ? '▲' : value < 0 ? '▼' : '●';
      const color = value > 0 ? '#48bb78' : value < 0 ? '#f56565' : '#94a3b8';
      const bgColor = value > 0 ? 'rgba(72, 187, 120, 0.15)' : value < 0 ? 'rgba(245, 101, 101, 0.15)' : 'rgba(148, 163, 184, 0.1)';

      element.textContent = `${arrow} ${Math.abs(value)}`;
      element.style.color = color;
      element.style.backgroundColor = bgColor;
    }
  });
}

function renderPeakActivityHours(peakData) {
  console.log("Rendering peak activity hours:", peakData);

  // Render peak hour range cards
  const container = document.getElementById('peakRangesContainer');
  if (container && peakData.peak_ranges) {
    container.innerHTML = '';

    // Icons for each rank
    const icons = ['🥇', '🥈', '🥉', '🏅', '⭐'];

    peakData.peak_ranges.forEach((range, index) => {
      const card = document.createElement('div');
      card.className = 'peak-range-card';

      const icon = icons[index] || '📊';
      const rankLabel = index === 0 ? 'Most Active' : index === 1 ? '2nd Most Active' : index === 2 ? '3rd Most Active' : `Rank #${index + 1}`;

      card.innerHTML = `
        <div class="range-label">${icon} ${rankLabel}</div>
        <div class="range-time">${range.range}</div>
        <div class="range-info">Cluster ${range.cluster_id} • Activity Level: ${range.avg_activity}</div>
      `;

      container.appendChild(card);
    });
  }

  // Render PCA scatter plot
  const scatterCtx = document.getElementById('clusteringScatterChart');
  if (scatterCtx && peakData.scatter_data) {
    const scatterData = peakData.scatter_data;

    // Separate outliers and non-outliers
    const outliers = scatterData.points.filter(p => p.is_outlier);
    const nonOutliers = scatterData.points.filter(p => !p.is_outlier);

    // Group non-outliers by cluster
    const clusters = {};
    nonOutliers.forEach(p => {
      if (!clusters[p.cluster]) {
        clusters[p.cluster] = [];
      }
      clusters[p.cluster].push(p);
    });

    // Create datasets for each cluster - using consistent color palette
    const datasets = [];
    const clusterColors = [
      'rgb(251, 175, 58)',   // Neutral yellow - primary
      'rgb(87, 188, 189)',   // Teal
      'rgb(227, 93, 96)',    // Coral red
      'rgb(74, 110, 229)',   // Royal blue
      'rgb(21, 19, 46)',     // Deep navy
    ];

    Object.keys(clusters).forEach((clusterId, index) => {
      const clusterPoints = clusters[clusterId];
      datasets.push({
        label: `Cluster ${clusterId}`,
        data: clusterPoints.map(p => ({ x: p.x, y: p.y })),
        backgroundColor: clusterColors[index % clusterColors.length],
        borderColor: '#fff',
        borderWidth: 2,
        pointRadius: 7,
        pointHoverRadius: 9,
      });
    });

    // Add outliers dataset
    if (outliers.length > 0) {
      datasets.push({
        label: 'Outliers',
        data: outliers.map(p => ({ x: p.x, y: p.y })),
        backgroundColor: 'rgba(150, 150, 150, 0.4)',
        borderColor: 'rgb(150, 150, 150)',
        borderWidth: 1,
        pointRadius: 5,
        pointHoverRadius: 7,
        pointStyle: 'crossRot',
      });
    }

    new Chart(scatterCtx, {
      type: 'scatter',
      data: {
        datasets: datasets
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
          legend: {
            display: true,
            position: 'bottom',
            labels: {
              font: {
                size: 11,
                family: 'Montserrat, sans-serif'
              },
              padding: 10,
              usePointStyle: true,
            }
          },
          tooltip: {
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            titleFont: {
              family: 'Montserrat, sans-serif'
            },
            bodyFont: {
              family: 'Montserrat, sans-serif'
            },
            callbacks: {
              label: function(context) {
                const point = scatterData.points[context.dataIndex];
                return `Hour: ${point.hour}:00, Count: ${point.count}`;
              }
            }
          },
          title: {
            display: true,
            text: `Variance Explained: PC1=${(scatterData.explained_variance[0] * 100).toFixed(1)}%, PC2=${(scatterData.explained_variance[1] * 100).toFixed(1)}%`,
            font: {
              size: 10,
              family: 'Montserrat, sans-serif',
              weight: '400'
            },
            color: '#666',
            padding: {
              bottom: 10
            }
          }
        },
        scales: {
          x: {
            title: {
              display: true,
              text: 'Principal Component 1',
              font: {
                family: 'Montserrat, sans-serif',
                size: 11
              }
            },
            grid: {
              color: 'rgba(0, 0, 0, 0.05)'
            }
          },
          y: {
            title: {
              display: true,
              text: 'Principal Component 2',
              font: {
                family: 'Montserrat, sans-serif',
                size: 11
              }
            },
            grid: {
              color: 'rgba(0, 0, 0, 0.05)'
            }
          }
        }
      }
    });
  }
}
