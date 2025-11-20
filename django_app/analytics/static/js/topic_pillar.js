// Topic Pillar Analysis JavaScript
let topicPillarData = null;
let currentPage = 1;
const postsPerPage = 6; // 6 posts per page

document.addEventListener("DOMContentLoaded", function () {
  loadTopicPillarData();
});

async function loadTopicPillarData() {
  try {
    console.log("Fetching topic pillar data from /api/topic-pillars/...");
    const response = await fetch("/api/topic-pillars/");
    console.log("Response received:", response.status);

    const data = await response.json();
    console.log("Data parsed:", data);

    if (data.error) {
      console.error("Error:", data.error);
      return;
    }

    topicPillarData = data;

    // Render topics overview
    renderTopicsGrid(data.topics);

    // Create engagement chart
    createEngagementChart(data.topic_engagement);

    // Populate topic filter
    populateTopicFilter(data.topics);

    // Show all posts by default
    showAllPosts();
  } catch (error) {
    console.error("Error loading topic pillar data:", error);
  }
}

function renderTopicsGrid(topics) {
  const grid = document.getElementById("topics-grid");
  grid.innerHTML = "";

  topics.forEach((topic) => {
    const topicCard = document.createElement("div");
    topicCard.className = "topic-card";
    topicCard.innerHTML = `
            <div class="topic-header">
                <h6>${topic.label}</h6>
            </div>
            <div class="topic-words">
                ${topic.words
                  .slice(0, 5)
                  .map((word) => `<span class="topic-word">${word}</span>`)
                  .join("")}
            </div>
        `;
    grid.appendChild(topicCard);
  });
}

function createEngagementChart(topicEngagement) {
  const ctx = document.getElementById("topicEngagementChart").getContext("2d");

  // Sort by total engagement
  const sorted = [...topicEngagement].sort((a, b) => b.total_engagement - a.total_engagement);

  const labels = sorted.map((t) => t.topic_label);
  const data = sorted.map((t) => t.total_engagement);

  // Color palette
  const colors = [
    "rgb(251, 175, 58)", // Yellow
    "rgb(87, 188, 189)", // Teal
    "rgb(74, 85, 162)", // Royal blue
    "rgb(26, 32, 44)", // Navy
    "rgb(255, 159, 64)", // Orange
    "rgb(153, 102, 255)", // Purple
    "rgb(255, 99, 132)", // Pink
    "rgb(75, 192, 192)", // Cyan
    "rgb(255, 205, 86)", // Light yellow
  ];

  new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Total Engagement",
          data: data,
          backgroundColor: colors.slice(0, data.length),
          borderWidth: 0,
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
          callbacks: {
            afterLabel: function (context) {
              const idx = context.dataIndex;
              const engagement = sorted[idx];
              return [`Likes: ${engagement.total_likes.toLocaleString()}`, `Replies: ${engagement.total_replies.toLocaleString()}`, `Retweets: ${engagement.total_retweets.toLocaleString()}`, `Posts: ${engagement.tweet_count}`];
            },
          },
        },
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            callback: function (value) {
              return value.toLocaleString();
            },
          },
        },
      },
    },
  });
}

function populateTopicFilter(topics) {
  const select = document.getElementById("topicFilter");

  // Add "All Topics" option
  const allOption = document.createElement("option");
  allOption.value = "";
  allOption.textContent = "All Topics (Show All Posts)";
  select.appendChild(allOption);

  topics.forEach((topic) => {
    const option = document.createElement("option");
    option.value = topic.topic_id;
    option.textContent = `${topic.label} - ${topic.words.slice(0, 3).join(", ")}`;
    select.appendChild(option);
  });

  // Add event listener
  select.addEventListener("change", function () {
    currentPage = 1; // Reset to page 1 when filter changes
    const topicId = parseInt(this.value);
    if (!isNaN(topicId)) {
      showPostsForTopic(topicId);
    } else {
      showAllPosts();
    }
  });
}

function showAllPosts() {
  const postsSection = document.getElementById("postsSection");
  const postsTitle = document.getElementById("postsTitle");

  postsTitle.textContent = "All Posts from All Topics";

  // Collect all posts from all topics
  const allPosts = [];
  for (const topicId in topicPillarData.topic_posts) {
    const posts = topicPillarData.topic_posts[topicId];
    const topic = topicPillarData.topics.find((t) => t.topic_id === parseInt(topicId));

    posts.forEach((post) => {
      allPosts.push({
        ...post,
        topic_label: topic.label,
      });
    });
  }

  // Sort by topic strength (descending)
  allPosts.sort((a, b) => b.topic_strength - a.topic_strength);

  renderPosts(allPosts, "All Topics");
  postsSection.style.display = "block";
}

function showPostsForTopic(topicId) {
  const postsSection = document.getElementById("postsSection");
  const postsTitle = document.getElementById("postsTitle");

  // Get topic label
  const topic = topicPillarData.topics.find((t) => t.topic_id === topicId);
  postsTitle.textContent = `Top Posts for ${topic.label}`;

  // Get posts for this topic
  const posts = topicPillarData.topic_posts[topicId];

  if (!posts || posts.length === 0) {
    const postsGrid = document.getElementById("postsGrid");
    postsGrid.innerHTML = '<p style="text-align: center; color: #718096;">No posts found for this topic</p>';
    postsSection.style.display = "block";
    return;
  }

  // Add topic label to each post
  const postsWithLabel = posts.map((post) => ({
    ...post,
    topic_label: topic.label,
  }));

  renderPosts(postsWithLabel, topic.label);
  postsSection.style.display = "block";
}

function renderPosts(posts, topicLabel) {
  const postsGrid = document.getElementById("postsGrid");

  // Clear grid
  postsGrid.innerHTML = "";

  if (!posts || posts.length === 0) {
    postsGrid.innerHTML = '<p style="text-align: center; color: #718096;">No posts found</p>';
    return;
  }

  // Calculate pagination
  const totalPages = Math.ceil(posts.length / postsPerPage);
  const startIndex = (currentPage - 1) * postsPerPage;
  const endIndex = startIndex + postsPerPage;
  const currentPosts = posts.slice(startIndex, endIndex);

  // Create post cards
  currentPosts.forEach((post) => {
    const card = document.createElement("div");
    card.className = "post-card";

    // Calculate total engagement
    const totalEngagement = post.likes + post.replies + post.retweets;

    card.innerHTML = `
            <div class="post-header">
                <span class="post-type-badge">${post.tweet_type}</span>
                <span class="topic-strength-badge">${(post.topic_strength * 100).toFixed(1)}% match</span>
            </div>
            ${topicLabel === "All Topics" ? `<div class="post-topic-label">Topic: ${post.topic_label}</div>` : ""}
            <div class="post-content">
                <p>${escapeHtml(post.full_text)}</p>
            </div>
            <div class="post-stats">
                <div class="stat-item">
                    <span class="stat-icon">❤️</span>
                    <span class="stat-value">${post.likes.toLocaleString()}</span>
                    <span class="stat-label">Likes</span>
                </div>
                <div class="stat-item">
                    <span class="stat-icon">💬</span>
                    <span class="stat-value">${post.replies.toLocaleString()}</span>
                    <span class="stat-label">Replies</span>
                </div>
                <div class="stat-item">
                    <span class="stat-icon">🔁</span>
                    <span class="stat-value">${post.retweets.toLocaleString()}</span>
                    <span class="stat-label">Retweets</span>
                </div>
                <div class="stat-item highlight">
                    <span class="stat-icon">📊</span>
                    <span class="stat-value">${totalEngagement.toLocaleString()}</span>
                    <span class="stat-label">Total</span>
                </div>
            </div>
        `;

    // Add click event to open modal
    card.addEventListener("click", function () {
      openPostModal(post.id_str);
    });

    postsGrid.appendChild(card);
  });

  // Render pagination
  renderPagination(totalPages, posts, topicLabel);
}

function renderPagination(totalPages, posts, topicLabel) {
  const postsGrid = document.getElementById("postsGrid");

  if (totalPages <= 1) return; // No pagination needed

  const paginationDiv = document.createElement("div");
  paginationDiv.className = "pagination";
  paginationDiv.style.cssText = `
        grid-column: 1 / -1;
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 0.5rem;
        margin-top: 2rem;
    `;

  // Previous button
  const prevBtn = document.createElement("button");
  prevBtn.textContent = "← Previous";
  prevBtn.className = "pagination-btn";
  prevBtn.disabled = currentPage === 1;
  prevBtn.onclick = () => {
    if (currentPage > 1) {
      currentPage--;
      renderPosts(posts, topicLabel);
    }
  };
  paginationDiv.appendChild(prevBtn);

  // Page numbers
  const pageInfo = document.createElement("span");
  pageInfo.className = "page-info";
  pageInfo.textContent = `Page ${currentPage} of ${totalPages}`;
  paginationDiv.appendChild(pageInfo);

  // Next button
  const nextBtn = document.createElement("button");
  nextBtn.textContent = "Next →";
  nextBtn.className = "pagination-btn";
  nextBtn.disabled = currentPage === totalPages;
  nextBtn.onclick = () => {
    if (currentPage < totalPages) {
      currentPage++;
      renderPosts(posts, topicLabel);
    }
  };
  paginationDiv.appendChild(nextBtn);

  postsGrid.appendChild(paginationDiv);
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

// Modal functions using Bootstrap
let bootstrapModal = null;

function openPostModal(permalink) {
  const modalElement = document.getElementById("postModal");
  const modalBody = document.getElementById("modalBody");

  // Initialize Bootstrap modal if not already
  if (!bootstrapModal) {
    bootstrapModal = new bootstrap.Modal(modalElement);
  }

  // Show modal with loading state
  modalBody.innerHTML = `
    <div class="text-center py-5">
      <div class="spinner-border text-warning" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-3 text-muted">Loading post details...</p>
    </div>
  `;

  // Show the modal
  bootstrapModal.show();

  // Fetch post details
  fetch(`/api/post-detail/?permalink=${encodeURIComponent(permalink)}`)
    .then((response) => response.json())
    .then((data) => {
      if (data.error) {
        modalBody.innerHTML = `
          <div class="alert alert-danger" role="alert">
            <strong>Error:</strong> ${data.error}
          </div>
        `;
        return;
      }

      // Render post details
      renderPostDetails(data, modalBody);
    })
    .catch((error) => {
      console.error("Error fetching post details:", error);
      modalBody.innerHTML = `
        <div class="alert alert-danger" role="alert">
          <strong>Failed to load post details</strong>
          <p class="mb-0">${error.message}</p>
        </div>
      `;
    });
}

function renderPostDetails(data, container) {
  let html = '';

  // Post meta buttons section (likes, replies, hashtags as badges)
  html += `
    <div style="display: flex; gap: 0.75rem; flex-wrap: wrap; margin-bottom: 1.5rem; justify-content: center;">
      <span class="badge bg-danger" style="font-size: 0.95rem; padding: 0.6rem 1rem; display: flex; align-items: center; gap: 0.5rem;">
        <span>❤️</span>
        <span>${data.likes.toLocaleString()} Likes</span>
      </span>
      <span class="badge bg-primary" style="font-size: 0.95rem; padding: 0.6rem 1rem; display: flex; align-items: center; gap: 0.5rem;">
        <span>💬</span>
        <span>${data.replies.toLocaleString()} Replies</span>
      </span>
      <span class="badge bg-secondary" style="font-size: 0.95rem; padding: 0.6rem 1rem; display: flex; align-items: center; gap: 0.5rem;">
        <span>🔁</span>
        <span>${data.retweets ? data.retweets.toLocaleString() : 0} Retweets</span>
      </span>
      <span class="badge bg-info" style="font-size: 0.95rem; padding: 0.6rem 1rem;">
        ${data.tweet_type}
      </span>
    </div>
  `;

  // Hashtags section as button-like badges
  if (data.hashtags && data.hashtags.length > 0) {
    html += `
      <div style="margin-bottom: 1.5rem;">
        <h6 style="color: #4a5568; margin-bottom: 0.75rem; font-size: 0.95rem; font-weight: 600;">
          <span style="margin-right: 0.5rem;">#️⃣</span>
          Hashtags Used
        </h6>
        <div style="display: flex; gap: 0.5rem; flex-wrap: wrap;">
    `;
    data.hashtags.forEach((tag) => {
      html += `<span class="badge" style="background: linear-gradient(135deg, rgb(251, 175, 58), rgb(227, 93, 96)); font-size: 0.85rem; padding: 0.5rem 0.85rem; font-weight: 500;">#${escapeHtml(tag)}</span>`;
    });
    html += `
        </div>
      </div>
    `;
  }

  // Word cloud section (matching sentiment page design)
  html += `
    <div style="margin-bottom: 1rem;">
      <h6 style="color: #4a5568; margin-bottom: 0.75rem; font-size: 0.95rem; font-weight: 600;">
        <span style="margin-right: 0.5rem;">☁️</span>
        Reply Word Cloud
        <span style="font-size: 0.8rem; font-weight: normal; color: #718096;">
          (${data.reply_count} replies analyzed)
        </span>
      </h6>
  `;

  if (data.wordcloud_data && data.wordcloud_data.length > 0) {
    // Create word cloud container with better styling
    html += `
      <div class="wordcloud-canvas" style="
        display: flex;
        flex-wrap: wrap;
        gap: 0.8rem;
        justify-content: center;
        align-items: center;
        padding: 2rem;
        min-height: 250px;
        background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
        border-radius: 12px;
        overflow: visible;
        box-shadow: inset 0 2px 8px rgba(0,0,0,0.05);
      ">
    `;

    // Take top 30 words for better variety
    const topWords = data.wordcloud_data.slice(0, 30);
    const maxValue = Math.max(...topWords.map((d) => d.value));
    const minValue = Math.min(...topWords.map((d) => d.value));

    // Color palette - multiple colors for variety
    const colors = [
      'rgb(87, 188, 189)',   // Teal
      'rgb(251, 175, 58)',   // Yellow
      'rgb(227, 93, 96)',    // Coral
      'rgb(74, 85, 162)',    // Royal blue
      'rgb(153, 102, 255)',  // Purple
    ];

    topWords.forEach((word, index) => {
      // More dramatic font size range: 10px to 36px
      const fontSize = minValue === maxValue
        ? 16
        : 10 + ((word.value - minValue) / (maxValue - minValue)) * 26;

      // Better opacity range: 0.7 to 1.0
      const opacity = 0.7 + ((word.value - minValue) / (maxValue - minValue)) * 0.3;

      // Rotate some words for visual interest
      const rotation = (index % 4 === 0) ? -15 : (index % 4 === 1) ? 15 : (index % 4 === 2) ? -8 : 0;

      // Pick color based on size (larger = teal, smaller = other colors)
      const colorIndex = fontSize > 25 ? 0 : (index % colors.length);
      const color = colors[colorIndex];

      // Font weight varies with size
      const fontWeight = fontSize > 20 ? 700 : 600;

      html += `
        <span class="wordcloud-word-item"
              style="
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
              "
              data-opacity="${opacity}"
              data-rotation="${rotation}"
              title="${word.text}: ${word.value} occurrences"
              onmouseenter="this.style.opacity='1'; this.style.transform='rotate(0deg) scale(1.15)'; this.style.textShadow='0 4px 12px rgba(0,0,0,0.2)';"
              onmouseleave="this.style.opacity='${opacity}'; this.style.transform='rotate(${rotation}deg) scale(1)'; this.style.textShadow='0 2px 4px rgba(0,0,0,0.1)';">
          ${escapeHtml(word.text)}
        </span>
      `;
    });

    html += "</div>";
  } else {
    html += '<div style="text-align: center; color: #718096; padding: 2rem;">No reply data available for this post</div>';
  }

  html += "</div>";

  container.innerHTML = html;
}
