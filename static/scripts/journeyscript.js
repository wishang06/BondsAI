let sessionsData = [];
let currentSessionIndex = -1;
let pathPoints = [];

document.addEventListener('DOMContentLoaded', function () {
  loadSessions();
});

async function loadSessions() {
  const loading = document.getElementById('loading');
  const roadmapContainer = document.getElementById('roadmap-container');
  const noSessions = document.getElementById('no-sessions');

  loading.style.display = 'block';
  roadmapContainer.style.display = 'none';
  noSessions.style.display = 'none';

  try {
    const response = await fetch('/api/recruiter/applicants');
    const data = await response.json();

    if (data.applicants && data.applicants.length > 0) {
      sessionsData = data.applicants.sort((a, b) => {
        const da = a.interview_date || '';
        const db = b.interview_date || '';
        return da.localeCompare(db);
      });

      updateStatsBar();
      displayRoadmap();
      roadmapContainer.style.display = 'block';
    } else {
      noSessions.style.display = 'block';
    }
  } catch (error) {
    console.error('Error loading sessions:', error);
    noSessions.style.display = 'block';
  } finally {
    loading.style.display = 'none';
  }
}

function updateStatsBar() {
  const streakCount = document.getElementById('streak-count');
  const totalSessions = document.getElementById('total-sessions');
  const avgScore = document.getElementById('avg-score');

  totalSessions.textContent = sessionsData.length;
  
  if (sessionsData.length > 0) {
    const totalScore = sessionsData.reduce((sum, s) => sum + (s.final_score || 0), 0);
    const avg = Math.round(totalScore / sessionsData.length);
    avgScore.textContent = `${avg}/100`;
  } else {
    avgScore.textContent = '0/100';
  }

  streakCount.textContent = calculateStreak();
}

function calculateStreak() {
  if (sessionsData.length === 0) return 0;
  return Math.min(sessionsData.length, 7);
}

function displayRoadmap() {
  const landmarksContainer = document.getElementById('landmarks-container');
  const pathSvg = document.getElementById('path-svg');
  const sectionBanners = document.getElementById('section-banners');
  
  landmarksContainer.innerHTML = '';
  pathSvg.innerHTML = '';
  sectionBanners.innerHTML = '';
  
  const maxSessions = 5;
  const sessionsToShow = sessionsData.slice(-maxSessions);
  
  // Draw path
  drawPath(pathSvg, sessionsToShow.length);
  
  // Add section banner
  if (sessionsToShow.length > 0) {
    addSectionBanner(sessionsToShow.length, pathPoints);
  }
  
  // Create landmarks
  sessionsToShow.forEach((session, index) => {
    const landmark = createLandmark(session, index, sessionsToShow.length, pathPoints);
    landmarksContainer.appendChild(landmark);
  });
  
  // Add locked landmarks
  for (let i = sessionsToShow.length; i < maxSessions; i++) {
    const lockedLandmark = createLandmark(null, i, maxSessions, pathPoints, true);
    landmarksContainer.appendChild(lockedLandmark);
  }
}

function drawPath(svg, numSessions) {
  const width = 1200;
  const height = 600;
  svg.setAttribute('viewBox', `0 0 ${width} ${height}`);
  svg.setAttribute('preserveAspectRatio', 'xMidYMid meet');
  
  pathPoints = [];
  const startX = 100;
  const endX = width - 100;
  const y = height / 2;
  const segmentWidth = (endX - startX) / (numSessions + 1);
  
  // Create straight horizontal path points
  for (let i = 0; i < numSessions; i++) {
    const x = startX + segmentWidth * (i + 1);
    pathPoints.push({ x, y });
  }
  
  // Create straight line path
  const path = `M ${startX} ${y} L ${endX} ${y}`;
  
  // Draw outline
  const outlinePath = document.createElementNS('http://www.w3.org/2000/svg', 'path');
  outlinePath.setAttribute('d', path);
  outlinePath.setAttribute('class', 'path-line-outline');
  svg.appendChild(outlinePath);
  
  // Draw main path
  const mainPath = document.createElementNS('http://www.w3.org/2000/svg', 'path');
  mainPath.setAttribute('d', path);
  mainPath.setAttribute('class', 'path-line');
  svg.appendChild(mainPath);
  
  // Draw texture
  const texturePath = document.createElementNS('http://www.w3.org/2000/svg', 'path');
  texturePath.setAttribute('d', path);
  texturePath.setAttribute('class', 'path-texture');
  svg.appendChild(texturePath);
}

function addSectionBanner(numSessions, pathPoints) {
  const sectionBanners = document.getElementById('section-banners');
  if (!sectionBanners || numSessions === 0 || !pathPoints[0]) return;
  
  const banner = document.createElement('div');
  banner.className = 'section-banner';
  
  const point = pathPoints[0];
  const xPercent = (point.x / 1200) * 100;
  const yPercent = (point.y / 600) * 100 - 12;
  
  banner.style.left = `${xPercent}%`;
  banner.style.top = `${yPercent}%`;
  banner.textContent = `Section ${Math.ceil(numSessions / 2)} - Interview Practice`;
  sectionBanners.appendChild(banner);
}

function createLandmark(session, index, totalSessions, pathPoints, isLocked = false) {
  const landmark = document.createElement('div');
  landmark.className = 'landmark';
  
  // Get position from path points (straight line)
  let point;
  if (pathPoints && pathPoints[index]) {
    point = pathPoints[index];
  } else {
    const width = 1200;
    const height = 600;
    const startX = 100;
    const endX = width - 100;
    const segmentWidth = (endX - startX) / (totalSessions + 1);
    point = {
      x: startX + segmentWidth * (index + 1),
      y: height / 2
    };
  }
  
  const xPercent = (point.x / 1200) * 100;
  const yPercent = (point.y / 600) * 100;
  
  landmark.style.left = `${xPercent}%`;
  landmark.style.top = `${yPercent}%`;
  
  if (isLocked) {
    const badge = document.createElement('div');
    badge.className = 'landmark-badge locked';
    const icon = document.createElement('div');
    icon.className = 'landmark-icon';
    icon.textContent = '🔒';
    badge.appendChild(icon);
    landmark.appendChild(badge);
    landmark.onclick = () => alert('Complete previous sessions to unlock!');
  } else {
    const score = session.final_score || 0;
    const stars = Math.min(3, Math.floor(score / 33));
    
    // Stars above
    if (stars > 0) {
      const starsDiv = document.createElement('div');
      starsDiv.className = 'landmark-stars';
      for (let i = 0; i < stars; i++) {
        const star = document.createElement('span');
        star.className = 'star';
        star.textContent = '⭐';
        starsDiv.appendChild(star);
      }
      landmark.appendChild(starsDiv);
    }
    
    // Badge
    const badge = document.createElement('div');
    const isCurrent = index === totalSessions - 1;
    badge.className = `landmark-badge ${isCurrent ? 'current' : 'completed'}`;
    const icon = document.createElement('div');
    icon.className = 'landmark-icon';
    icon.textContent = index + 1;
    badge.appendChild(icon);
    landmark.appendChild(badge);
    
    // Score below
    const scoreBadge = document.createElement('div');
    scoreBadge.className = 'landmark-score-badge';
    scoreBadge.textContent = `${score}`;
    landmark.appendChild(scoreBadge);
    
    landmark.onclick = () => showSessionDetails(index);
  }
  
  return landmark;
}

async function showSessionDetails(index) {
  currentSessionIndex = index;
  const session = sessionsData[index];
  const modal = document.getElementById('session-modal');
  const nameElement = document.getElementById('modal-session-name');
  const infoElement = document.getElementById('modal-session-info');
  const contentArea = document.getElementById('modal-content-area');

  if (!modal || !nameElement || !infoElement || !contentArea) return;

  nameElement.textContent = `Practice Session ${index + 1}`;
  infoElement.textContent = `Completed on ${session.interview_date || 'Unknown'} • ${
    session.conversation_count || 0
  } exchanges • Score: ${session.final_score || 0}/100`;

  let rawAssessmentText = '';
  if (session.filepath) {
    try {
      const filename = encodeURIComponent(session.filepath.split(/[/\\]/).pop());
      const response = await fetch(`/api/assessment/raw/${filename}`);
      const data = await response.json();
      rawAssessmentText = data.assessment_text || '';
    } catch (error) {
      console.error('Error loading raw assessment:', error);
    }
  }

  window.currentRawAssessment = rawAssessmentText;

  let content = '<div class="characteristics-section">';
  content += '<div class="section-title">📊 Skill Categories</div>';
  content += '<div class="skill-buttons-container">';
  
  const techAvg = averageCategory(session.technical_skills);
  content += `<button class="skill-category-button" data-category="technical_skills">
    <div class="skill-category-name">💻 Technical Skills</div>
    <div class="skill-category-score">${techAvg}/100</div>
  </button>`;
  
  const behAvg = averageCategory(session.behavioral_traits);
  content += `<button class="skill-category-button" data-category="behavioral_traits">
    <div class="skill-category-name">🤝 Behavioral Traits</div>
    <div class="skill-category-score">${behAvg}/100</div>
  </button>`;
  
  const cultAvg = averageCategory(session.cultural_fit);
  content += `<button class="skill-category-button" data-category="cultural_fit">
    <div class="skill-category-name">🌟 Cultural Fit</div>
    <div class="skill-category-score">${cultAvg}/100</div>
  </button>`;
  
  const softAvg = averageCategory(session.soft_skills);
  content += `<button class="skill-category-button" data-category="soft_skills">
    <div class="skill-category-name">💬 Soft Skills</div>
    <div class="skill-category-score">${softAvg}/100</div>
  </button>`;
  
  content += '</div></div>';
  content += '<div id="detailed-feedback-panel" class="detailed-feedback-panel"></div>';
  
  if (session.insights?.weaknesses?.length > 0) {
    content += '<div class="improvement-section">';
    content += '<div class="improvement-section-title">📈 Areas for Improvement</div>';
    content += '<ul class="improvement-list">';
    session.insights.weaknesses.forEach(w => {
      content += `<li>${escapeHtml(w)}</li>`;
    });
    content += '</ul></div>';
  }
  
  if (session.insights?.recommendations?.length > 0) {
    content += '<div class="recommendations-section">';
    content += '<div class="recommendations-section-title">🎯 Recommended Future Steps</div>';
    content += '<ul class="recommendations-list">';
    session.insights.recommendations.forEach(r => {
      content += `<li>${escapeHtml(r)}</li>`;
    });
    content += '</ul></div>';
  }

  contentArea.innerHTML = content;
  
  document.querySelectorAll('.skill-category-button').forEach(btn => {
    btn.addEventListener('click', function() {
      showCategoryFeedback(this.getAttribute('data-category'));
    });
  });
  
  modal.style.display = 'flex';
}

function showCategoryFeedback(categoryName) {
  const panel = document.getElementById('detailed-feedback-panel');
  if (!panel) return;
  
  const rawAssessmentText = window.currentRawAssessment || '';
  
  document.querySelectorAll('.skill-category-button').forEach(btn => {
    btn.classList.remove('active');
  });
  
  const clickedButton = document.querySelector(`[data-category="${categoryName}"]`);
  if (clickedButton) clickedButton.classList.add('active');
  
  if (!rawAssessmentText) {
    panel.innerHTML = '<div class="feedback-content">No detailed feedback available.</div>';
    panel.classList.add('active');
    return;
  }
  
  const categoryFeedback = parseCategoryFeedback(rawAssessmentText, categoryName);
  
  if (!categoryFeedback) {
    panel.innerHTML = '<div class="feedback-content">No detailed feedback available.</div>';
    panel.classList.add('active');
    return;
  }
  
  let feedbackHTML = `<div class="feedback-section-title">${formatCategoryName(categoryName)}</div>`;
  feedbackHTML += `<div class="feedback-content">${formatFeedbackText(categoryFeedback)}</div>`;
  
  panel.innerHTML = feedbackHTML;
  panel.classList.add('active');
  
  setTimeout(() => {
    panel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }, 100);
}

function parseCategoryFeedback(assessmentText, categoryName) {
  const patterns = {
    "technical_skills": /####?\s*1\.\s*Technical Skills.*?(?=####?\s*2\.|####?\s*Overall|$)/is,
    "behavioral_traits": /####?\s*2\.\s*Behavioral.*?(?=####?\s*[13]\.|####?\s*Overall|$)/is,
    "cultural_fit": /####?\s*3\.\s*Cultural.*?(?=####?\s*[124]\.|####?\s*Overall|$)/is,
    "soft_skills": /####?\s*4\.\s*Soft Skills.*?(?=####?\s*[1235]\.|####?\s*Overall|$)/is,
  };
  
  const match = assessmentText.match(patterns[categoryName]);
  return match ? match[0].trim() : '';
}

function formatCategoryName(categoryName) {
  const names = {
    "technical_skills": "💻 Technical Skills",
    "behavioral_traits": "🤝 Behavioral Traits",
    "cultural_fit": "🌟 Cultural Fit",
    "soft_skills": "💬 Soft Skills"
  };
  return names[categoryName] || categoryName;
}

function formatFeedbackText(text) {
  return text
    .replace(/####?\s*\d+\.\s*/g, '')
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/\n\n+/g, '</div><div class="feedback-item">')
    .replace(/\n/g, '<br>')
    .replace(/^/, '<div class="feedback-item">')
    .replace(/$/, '</div>');
}

function averageCategory(category) {
  const values = Object.values(category || {});
  if (!values.length) return 0;
  const sum = values.reduce((acc, v) => acc + (v || 0), 0);
  return Math.round(sum / values.length);
}

function escapeHtml(text) {
  if (!text) return '';
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

function closeModal() {
  const modal = document.getElementById('session-modal');
  if (modal) {
    modal.style.display = 'none';
    document.querySelectorAll('.skill-category-button').forEach(btn => {
      btn.classList.remove('active');
    });
    const panel = document.getElementById('detailed-feedback-panel');
    if (panel) panel.classList.remove('active');
  }
}

const sessionModal = document.getElementById('session-modal');
if (sessionModal) {
  sessionModal.addEventListener('click', function (e) {
    if (e.target === this) closeModal();
  });
}

const closeModalBtn = document.getElementById('close-modal-btn');
if (closeModalBtn) {
  closeModalBtn.addEventListener('click', closeModal);
}

document.addEventListener('keydown', function (e) {
  if (e.key === 'Escape') closeModal();
});

window.closeModal = closeModal;
