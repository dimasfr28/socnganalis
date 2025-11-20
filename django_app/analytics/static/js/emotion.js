// Emotion Analysis JavaScript
document.addEventListener("DOMContentLoaded", function () {
  loadEmotionData();
});

// Emotion configurations
const emotionConfig = {
  joy: { icon: "😊", color: "rgb(251, 187, 36)", name: "Joy" },
  anger: { icon: "😡", color: "rgb(239, 68, 68)", name: "Anger" },
  sadness: { icon: "😢", color: "rgb(59, 130, 246)", name: "Sadness" },
  fear: { icon: "😨", color: "rgb(168, 85, 247)", name: "Fear" },
  surprise: { icon: "😲", color: "rgb(236, 72, 153)", name: "Surprise" },
  disgust: { icon: "🤢", color: "rgb(34, 197, 94)", name: "Disgust" },
  neutral: { icon: "😐", color: "rgb(107, 114, 128)", name: "Neutral" },
};

async function loadEmotionData() {
  try {
    console.log("Fetching emotion data from /api/emotion-analysis/...");
    const response = await fetch("http://localhost:8001/api/emotion-analysis");
    console.log("Response received:", response.status);

    const data = await response.json();
    console.log("Data parsed:", data);

    if (data.error) {
      console.error("Error:", data.error);
      showError("Failed to load emotion data: " + data.error);
      return;
    }

    console.log("Emotion data loaded successfully:", data);

    // Update emotion summary cards
    updateEmotionCards(data.emotion_distribution, data.total_analyzed);

    // Create emotion distribution chart (pie/donut)
    createEmotionDistributionChart(data.emotion_distribution);

    // Create emotion engagement chart (grouped bar)
    createEmotionEngagementChart(data.emotion_by_engagement);

    // Create word clouds for each emotion
    createAllWordClouds(data.wordcloud_data);
  } catch (error) {
    console.error("Error loading emotion data:", error);
    showError("Failed to load emotion data. Please try again later.");
  }
}

function updateEmotionCards(emotionDist, total) {
  console.log("updateEmotionCards called with:", { emotionDist, total });

  const container = document.getElementById("emotionCardsContainer");
  container.innerHTML = "";

  // Emotion order for display
  const emotionOrder = ["joy", "anger", "sadness", "fear", "surprise", "disgust", "neutral"];

  emotionOrder.forEach((emotion) => {
    const data = emotionDist[emotion] || { count: 0, percentage: 0 };
    const config = emotionConfig[emotion];

    const card = document.createElement("div");
    card.className = `emotion-card ${emotion}`;
    card.innerHTML = `
            <div class="emotion-icon">${config.icon}</div>
            <div class="emotion-name">${config.name}</div>
            <div class="emotion-count">${data.count.toLocaleString()}</div>
            <div class="emotion-percentage">${data.percentage}%</div>
        `;

    container.appendChild(card);
  });
}

function createEmotionDistributionChart(emotionDist) {
  const ctx = document.getElementById("emotionDistributionChart").getContext("2d");

  const emotions = Object.keys(emotionDist);
  const labels = emotions.map((e) => emotionConfig[e]?.name || e);
  const values = emotions.map((e) => emotionDist[e].count);
  const colors = emotions.map((e) => emotionConfig[e]?.color || "#718096");

  // Arrow plugin for emotion distribution
  const arrowPlugin = {
    id: "emotionArrowAll",
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

        // Calculate total and percentages to detect small slices
        const total = values.reduce((a, b) => a + b, 0);
        const percentages = values.map((v) => (v / total) * 100);

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

          // Adaptive curve distance based on slice size and position
          // Small slices (<5%) get more spread to avoid collision
          const isSmallSlice = percentages[i] < 5;
          const baseDistance = isSmallSlice ? 28 : 22;

          // Check if this slice is in a cluster of small slices
          const prevSmall = i > 0 && percentages[i - 1] < 5;
          const nextSmall = i < values.length - 1 && percentages[i + 1] < 5;
          const inCluster = isSmallSlice && (prevSmall || nextSmall);

          // Add variation based on index to separate adjacent small slices
          let spreadFactor = 0;
          if (isSmallSlice) {
            if (prevSmall || nextSmall) {
              // Spread out for clustered small slices (reduced from 12)
              spreadFactor = i % 2 === 0 ? 8 : -8;
            }
          }

          const curveDist = baseDistance + spreadFactor + 3 * Math.sin((i * Math.PI) / values.length);
          const ex = cx + Math.cos(mid) * (outerRadius + curveDist);
          const ey = cy + Math.sin(mid) * (outerRadius + curveDist);

          // Control point for curve - straighter for clustered small slices to avoid collision
          // If in cluster, use minimal curve; otherwise use normal curve
          let curveIntensity;
          if (inCluster) {
            // Very minimal curve for clustered small slices
            curveIntensity = 0.06;
          } else if (isSmallSlice) {
            // Moderate curve for isolated small slices
            curveIntensity = 0.15;
          } else {
            // Normal curve for large slices
            curveIntensity = 0.18;
          }

          const ctrlAngle = mid + (i % 2 === 0 ? curveIntensity : -curveIntensity);
          const ctrlRadius = outerRadius + curveDist * 0.5;
          const cx1 = cx + Math.cos(ctrlAngle) * ctrlRadius;
          const cy1 = cy + Math.sin(ctrlAngle) * ctrlRadius;

          // Get color for this emotion
          const arrowColor = colors[i];

          ctx.save();
          ctx.strokeStyle = arrowColor;
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
          ctx.fillStyle = arrowColor;
          ctx.fill();

          // Label (emotion name)
          const label = chart.data.labels && chart.data.labels[i] ? chart.data.labels[i] : "";
          ctx.font = "12px Montserrat, sans-serif";
          ctx.fillStyle = arrowColor;
          ctx.textAlign = "center";
          ctx.textBaseline = "middle";

          // Adjust label position for small slices to avoid overlap
          const labelDistance = isSmallSlice ? 16 : 14;
          const lx = ex + Math.cos(mid) * labelDistance;
          const ly = ey + Math.sin(mid) * (isSmallSlice ? 8 : 6);

          ctx.fillText(label, lx, ly);
          ctx.restore();
        }
      } catch (e) {
        console.error("Arrow plugin error", e);
      }
    },
  };

  new Chart(ctx, {
    type: "pie",
    data: {
      labels: labels,
      datasets: [
        {
          data: values,
          backgroundColor: colors,
          borderWidth: 3,
          borderColor: "#fff",
        },
      ],
    },
    plugins: [arrowPlugin],
    options: {
      responsive: true,
      maintainAspectRatio: true,
      layout: {
        padding: 35,
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
            label: function (context) {
              const label = context.label || "";
              const value = context.parsed || 0;
              const total = context.dataset.data.reduce((a, b) => a + b, 0);
              const percentage = ((value / total) * 100).toFixed(1);
              return `${label}: ${value.toLocaleString()} (${percentage}%)`;
            },
          },
        },
      },
    },
  });

  // Populate table
  populateEmotionDistributionTable(emotionDist);
}

function populateEmotionDistributionTable(emotionDist) {
  const table = document.getElementById("emotionDistributionTable");
  if (!table) return;

  table.innerHTML = "";

  // Emotion order for display
  const emotionOrder = ["joy", "anger", "sadness", "fear", "surprise", "disgust", "neutral"];

  emotionOrder.forEach((emotion) => {
    if (emotionDist[emotion]) {
      const data = emotionDist[emotion];
      const config = emotionConfig[emotion];

      const tr = document.createElement("tr");
      const td1 = document.createElement("td");
      td1.innerHTML = `${config.icon} ${config.name}`;

      const td2 = document.createElement("td");
      td2.textContent = data.count.toLocaleString();

      tr.appendChild(td1);
      tr.appendChild(td2);
      table.appendChild(tr);
    }
  });
}

function createEmotionEngagementChart(emotionEngagement) {
  const ctx = document.getElementById("emotionEngagementChart").getContext("2d");

  // Sort emotions by engagement (descending)
  const sortedEmotions = Object.entries(emotionEngagement)
    .sort((a, b) => b[1] - a[1])
    .map(([emotion, _]) => emotion);

  const labels = sortedEmotions.map((e) => emotionConfig[e]?.name || e);
  const values = sortedEmotions.map((e) => emotionEngagement[e]);
  const colors = sortedEmotions.map((e) => emotionConfig[e]?.color || "#718096");

  new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Total Engagement",
          data: values,
          backgroundColor: colors,
          borderRadius: 8,
          borderSkipped: false,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            font: {
              family: "Montserrat",
            },
          },
          grid: {
            color: "rgba(0, 0, 0, 0.05)",
          },
        },
        x: {
          ticks: {
            font: {
              family: "Montserrat",
            },
          },
          grid: {
            display: false,
          },
        },
      },
      plugins: {
        legend: {
          display: false,
        },
        tooltip: {
          callbacks: {
            label: function (context) {
              return `Engagement: ${context.parsed.y.toLocaleString()}`;
            },
          },
        },
      },
    },
  });
}

function createAllWordClouds(wordcloudData) {
  const emotions = ["joy", "anger", "sadness", "fear", "surprise", "disgust"];

  emotions.forEach((emotion) => {
    const containerId = `wordcloud-${emotion}`;
    const words = wordcloudData[emotion] || [];
    const color = emotionConfig[emotion].color;

    createWordCloud(containerId, words, color);
  });
}

function createWordCloud(containerId, wordData, color) {
  const container = document.getElementById(containerId);

  if (!wordData || wordData.length === 0) {
    container.innerHTML = '<p style="text-align: center; color: #718096; font-size: 0.9rem;">No data available</p>';
    return;
  }

  // Clear previous content
  container.innerHTML = "";

  // Take top 25 words for better variety
  const topWords = wordData.slice(0, 25);
  const maxValue = Math.max(...topWords.map((d) => d.value));
  const minValue = Math.min(...topWords.map((d) => d.value));

  topWords.forEach((word, index) => {
    const span = document.createElement("span");

    // Font size range: 10px to 30px
    const fontSize = minValue === maxValue ? 16 : 10 + ((word.value - minValue) / (maxValue - minValue)) * 20;

    // Opacity range: 0.7 to 1.0
    const opacity = 0.7 + ((word.value - minValue) / (maxValue - minValue)) * 0.3;

    // Rotate some words for variety
    const rotation = index % 4 === 0 ? -12 : index % 4 === 1 ? 12 : index % 4 === 2 ? -6 : 0;

    // Font weight varies with size
    const fontWeight = fontSize > 20 ? 700 : 600;

    span.textContent = word.text;
    span.style.cssText = `
            font-size: ${fontSize}px;
            font-weight: ${fontWeight};
            color: ${color};
            opacity: ${opacity};
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            cursor: pointer;
            white-space: nowrap;
            transform: rotate(${rotation}deg);
            text-shadow: 0 2px 4px rgba(0,0,0,0.1);
            line-height: 1.4;
            display: inline-block;
        `;

    span.setAttribute("data-opacity", opacity);
    span.setAttribute("data-rotation", rotation);
    span.setAttribute("title", `${word.text}: ${word.value} occurrences`);

    span.addEventListener("mouseenter", function () {
      this.style.opacity = "1";
      this.style.transform = "rotate(0deg) scale(1.15)";
      this.style.textShadow = "0 4px 12px rgba(0,0,0,0.2)";
    });

    span.addEventListener("mouseleave", function () {
      const originalOpacity = this.getAttribute("data-opacity");
      const originalRotation = this.getAttribute("data-rotation");
      this.style.opacity = originalOpacity;
      this.style.transform = `rotate(${originalRotation}deg) scale(1)`;
      this.style.textShadow = "0 2px 4px rgba(0,0,0,0.1)";
    });

    container.appendChild(span);
  });
}

function showError(message) {
  const container = document.getElementById("emotionCardsContainer");
  container.innerHTML = `
        <div style="grid-column: 1 / -1; text-align: center; padding: 2rem;">
            <p style="color: #ef4444; font-size: 1rem; margin-bottom: 0.5rem;">⚠️ Error</p>
            <p style="color: #718096; font-size: 0.9rem;">${message}</p>
        </div>
    `;
}
