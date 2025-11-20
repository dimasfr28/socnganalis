// Recommendations JavaScript
document.addEventListener("DOMContentLoaded", function () {
  loadRecommendations();
});

let allRecommendations = [];

async function loadRecommendations() {
  try {
    console.log("Fetching recommendations from /api/recommendations/...");
    const response = await fetch("http://localhost:8001/api/recommendations");
    console.log("Response received:", response.status);

    const data = await response.json();
    console.log("Data parsed:", data);

    if (data.error) {
      console.error("Error:", data.error);
      showError("Failed to load recommendations: " + data.error);
      return;
    }

    console.log("Recommendations loaded successfully:", data);

    // Store all recommendations for filtering
    allRecommendations = data.recommendations || [];

    // Update insights
    updateInsights(data.insights);

    // Update performance score
    updatePerformanceScore(data.performance_score);

    // Update priority actions
    updatePriorityActions(data.priority_actions);

    // Update all recommendations
    updateRecommendations(allRecommendations);

    // Show sections
    document.getElementById("performanceContainer").style.display = "block";
    document.getElementById("priorityActionsContainer").style.display = "block";
    document.getElementById("recommendationsContainer").style.display = "block";

    // Setup filter buttons
    setupFilters();
  } catch (error) {
    console.error("Error loading recommendations:", error);
    showError("Failed to load recommendations. Please try again later.");
  }
}

function updateInsights(insights) {
  console.log("updateInsights called with:", insights);

  const container = document.getElementById("insightsContainer");
  container.innerHTML = "";

  if (!insights || insights.length === 0) {
    container.innerHTML = '<p style="text-align: center; color: #718096;">No insights available</p>';
    return;
  }

  insights.forEach((insight) => {
    const card = document.createElement("div");
    card.className = "insight-card";

    card.innerHTML = `
            <div class="insight-icon">${insight.icon || "📊"}</div>
            <div class="insight-title">${insight.title || insight.category}</div>
            <div class="insight-value">${insight.value}</div>
            ${insight.percentage ? `<div class="insight-description">${insight.percentage}%</div>` : ""}
            <div class="insight-description">${insight.description}</div>
        `;

    container.appendChild(card);
  });
}

function updatePerformanceScore(performanceScore) {
  console.log("updatePerformanceScore called with:", performanceScore);

  if (!performanceScore) return;

  // Update score values
  document.getElementById("performanceScoreValue").textContent = performanceScore.overall_score || "--";
  document.getElementById("performanceScoreRating").textContent = performanceScore.rating || "--";
  document.getElementById("performanceScoreRating").style.color = performanceScore.rating_color || "#1a202c";

  document.getElementById("sentimentScore").textContent = performanceScore.sentiment_score || "--";
  document.getElementById("emotionScore").textContent = performanceScore.emotion_score || "--";
  document.getElementById("engagementScore").textContent = performanceScore.engagement_score || "--";

  // Create gauge chart
  createPerformanceGaugeChart(performanceScore);
}

function createPerformanceGaugeChart(performanceScore) {
  const canvas = document.getElementById("performanceScoreChart");
  const ctx = canvas.getContext("2d");

  const score = performanceScore.overall_score || 0;
  const rating_color = performanceScore.rating_color || "#3b82f6";

  new Chart(ctx, {
    type: "doughnut",
    data: {
      datasets: [
        {
          data: [score, 100 - score],
          backgroundColor: [rating_color, "#e2e8f0"],
          borderWidth: 0,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      cutout: "75%",
      rotation: -90,
      circumference: 180,
      plugins: {
        legend: {
          display: false,
        },
        tooltip: {
          enabled: false,
        },
      },
    },
  });
}

function updatePriorityActions(priorityActions) {
  console.log("updatePriorityActions called with:", priorityActions);

  const container = document.getElementById("priorityActionsList");
  container.innerHTML = "";

  if (!priorityActions || priorityActions.length === 0) {
    container.innerHTML = '<p style="text-align: center; color: #718096;">No priority actions</p>';
    return;
  }

  priorityActions.forEach((action) => {
    const card = createActionCard(action);
    container.appendChild(card);
  });
}

function updateRecommendations(recommendations) {
  console.log("updateRecommendations called with:", recommendations);

  const container = document.getElementById("recommendationsList");
  container.innerHTML = "";

  if (!recommendations || recommendations.length === 0) {
    container.innerHTML = '<p style="text-align: center; color: #718096;">No recommendations available</p>';
    return;
  }

  recommendations.forEach((recommendation) => {
    const card = createActionCard(recommendation);
    container.appendChild(card);
  });
}

function createActionCard(action) {
  const card = document.createElement("div");
  card.className = `action-card ${action.priority}`;
  card.setAttribute("data-category", action.category);

  const priorityIcon = getPriorityIcon(action.priority);

  card.innerHTML = `
        <div class="action-header">
            <div class="action-title">
                <span>${priorityIcon}</span>
                <span>${action.title}</span>
            </div>
            <span class="action-priority-badge ${action.priority}">${action.priority}</span>
        </div>

        <div class="action-description">${action.description}</div>

        ${
          action.actionable_steps && action.actionable_steps.length > 0
            ? `
            <div class="action-steps">
                <div class="action-steps-title">Actionable Steps:</div>
                <ul class="action-steps-list">
                    ${action.actionable_steps.map((step) => `<li>${step}</li>`).join("")}
                </ul>
            </div>
        `
            : ""
        }

        ${
          action.impact || action.effort
            ? `
            <div class="action-impact">
                ${action.impact ? `<div class="action-impact-item"><span class="action-impact-label">Impact:</span><span class="action-impact-value">${action.impact}</span></div>` : ""}
                ${action.effort ? `<div class="action-impact-item"><span class="action-impact-label">Effort:</span><span class="action-impact-value">${action.effort}</span></div>` : ""}
            </div>
        `
            : ""
        }
    `;

  return card;
}

function getPriorityIcon(priority) {
  const icons = {
    critical: "🔴",
    high: "🟠",
    medium: "🔵",
    low: "🟢",
  };
  return icons[priority] || "⚪";
}

function setupFilters() {
  const filterButtons = document.querySelectorAll(".filter-button");

  filterButtons.forEach((button) => {
    button.addEventListener("click", function () {
      // Update active state
      filterButtons.forEach((btn) => btn.classList.remove("active"));
      this.classList.add("active");

      // Filter recommendations
      const filter = this.getAttribute("data-filter");
      filterRecommendations(filter);
    });
  });
}

function filterRecommendations(filter) {
  const container = document.getElementById("recommendationsList");
  container.innerHTML = "";

  let filtered = allRecommendations;

  if (filter !== "all") {
    filtered = allRecommendations.filter((rec) => rec.category === filter);
  }

  if (filtered.length === 0) {
    container.innerHTML = `<p style="text-align: center; color: #718096;">No recommendations found for category: ${filter}</p>`;
    return;
  }

  filtered.forEach((recommendation) => {
    const card = createActionCard(recommendation);
    container.appendChild(card);
  });
}

function showError(message) {
  const container = document.getElementById("insightsContainer");
  container.innerHTML = `
        <div style="grid-column: 1 / -1; text-align: center; padding: 2rem;">
            <p style="color: #ef4444; font-size: 1rem; margin-bottom: 0.5rem;">⚠️ Error</p>
            <p style="color: #718096; font-size: 0.9rem;">${message}</p>
        </div>
    `;
}
