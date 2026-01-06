let applicantsData = [];

document.addEventListener('DOMContentLoaded', function () {
  loadApplicants();
});

async function loadApplicants() {
  const loading = document.getElementById('loading');
  const container = document.getElementById('applicants-container');
  const noApplicants = document.getElementById('no-applicants');

  loading.style.display = 'block';
  container.style.display = 'none';
  noApplicants.style.display = 'none';

  try {
    const response = await fetch('/api/recruiter/applicants');
    const data = await response.json();

    if (data.applicants && data.applicants.length > 0) {
      // Sort by interview date ascending to feel like a journey
      applicantsData = data.applicants.sort((a, b) => {
        const da = a.interview_date || '';
        const db = b.interview_date || '';
        return da.localeCompare(db);
      });
      displaySessions(applicantsData);
      container.style.display = 'block';
    } else {
      noApplicants.style.display = 'block';
    }
  } catch (error) {
    console.error('Error loading sessions:', error);
    noApplicants.style.display = 'block';
  } finally {
    loading.style.display = 'none';
  }
}

function averageCategory(category) {
  const values = Object.values(category || {});
  if (!values.length) return 0;
  const sum = values.reduce((acc, v) => acc + (v || 0), 0);
  return Math.round(sum / values.length);
}

function displaySessions(applicants) {
  const grid = document.getElementById('applicants-grid');
  grid.innerHTML = '';

  applicants.forEach((applicant, index) => {
    const node = document.createElement('div');
    node.className = 'applicant-bubble';
    node.onclick = () => showCharacteristics(index);

    const techAvg = averageCategory(applicant.technical_skills);
    const behAvg = averageCategory(applicant.behavioral_traits);
    const softAvg = averageCategory(applicant.soft_skills);

    node.innerHTML = `
      <div class="applicant-name">Session ${index + 1}</div>
      <div class="applicant-info">${applicant.interview_date || 'Date unknown'}</div>
      <div class="applicant-info">Length: ${applicant.conversation_count || 0} exchanges • ${
      applicant.conversation_duration || '0h 0m 0s'
    }</div>
      <div class="applicant-score">Overall score: ${applicant.final_score || 0}/100</div>
      <div class="skills-mini-grid">
        <div class="skill-mini-item">
          <span class="skill-mini-label">Technical</span>
          <span class="skill-mini-value">${techAvg}</span>
        </div>
        <div class="skill-mini-item">
          <span class="skill-mini-label">Behavioral</span>
          <span class="skill-mini-value">${behAvg}</span>
        </div>
        <div class="skill-mini-item">
          <span class="skill-mini-label">Soft</span>
          <span class="skill-mini-value">${softAvg}</span>
        </div>
      </div>
    `;

    grid.appendChild(node);
  });
}

function buildGrowthPlan(applicant) {
  const scores = [];

  function pushScores(categoryName, categoryObj) {
    Object.entries(categoryObj || {}).forEach(([key, value]) => {
      scores.push({
        key,
        label: key.replace(/_/g, ' '),
        category: categoryName,
        value: value || 0,
      });
    });
  }

  pushScores('Technical', applicant.technical_skills);
  pushScores('Behavioral', applicant.behavioral_traits);
  pushScores('Cultural', applicant.cultural_fit);
  pushScores('Soft', applicant.soft_skills);

  scores.sort((a, b) => a.value - b.value);

  const weakest = scores.slice(0, 3);
  const strongest = scores.slice(-3).reverse();

  let html = '<div class="characteristics-section">';
  html += '<div class="section-title">Your Growth Plan</div>';
  html += '<p class="growth-subcopy">These suggestions are based on this session only. Aim for small, consistent improvements.</p>';

  if (strongest.length) {
    html += '<div class="skills-grid">';
    html += '<div class="skill-item">';
    html += '<div class="skill-name">Current strengths</div>';
    html += '<ul class="insights-list">';
    strongest.forEach((s) => {
      html += `<li><strong>${s.label}</strong> – ${s.value}/100</li>`;
    });
    html += '</ul></div>';
  }

  if (weakest.length) {
    html += '<div class="skill-item">';
    html += '<div class="skill-name">Focus areas for next 3 practices</div>';
    html += '<ul class="insights-list">';
    weakest.forEach((w) => {
      html += `<li>Prioritise <strong>${w.label}</strong> – build one concrete story or answer that shows improvement here.</li>`;
    });
    html += '</ul></div>';
    html += '</div>';
  }

  const recommendations = applicant.insights && applicant.insights.recommendations
    ? applicant.insights.recommendations
    : [];

  if (recommendations.length) {
    html += '<div class="characteristics-section">';
    html += '<div class="section-title">Suggested next drills</div>';
    html += '<ul class="insights-list">';
    recommendations.slice(0, 5).forEach((r) => {
      html += `<li>${r}</li>`;
    });
    html += '</ul></div>';
  }

  html += '</div>';
  return html;
}

function showCharacteristics(index) {
  const applicant = applicantsData[index];
  const modal = document.getElementById('characteristics-modal');
  const nameElement = document.getElementById('modal-candidate-name');
  const infoElement = document.getElementById('modal-candidate-info');
  const contentElement = document.getElementById('modal-characteristics-content');

  nameElement.textContent = `Practice Session ${index + 1}`;
  infoElement.textContent = `Completed on ${applicant.interview_date || 'Unknown date'} • ${
    applicant.conversation_count || 0
  } exchanges`;

  let content = '';

  if (applicant.soft_skills) {
    content += `
      <div class="characteristics-section">
        <div class="section-title">Core Interview Skills</div>
        <div class="skills-grid">
          <div class="skill-item">
            <div class="skill-name">Communication</div>
            <div class="skill-score">${applicant.soft_skills.communication || 0}/100</div>
          </div>
          <div class="skill-item">
            <div class="skill-name">Decision Making</div>
            <div class="skill-score">${applicant.soft_skills.decision_making || 0}/100</div>
          </div>
          <div class="skill-item">
            <div class="skill-name">Time Management</div>
            <div class="skill-score">${applicant.soft_skills.time_management || 0}/100</div>
          </div>
          <div class="skill-item">
            <div class="skill-name">Leadership</div>
            <div class="skill-score">${applicant.soft_skills.leadership || 0}/100</div>
          </div>
        </div>
      </div>
    `;
  }

  if (applicant.behavioral_traits) {
    content += `
      <div class="characteristics-section">
        <div class="section-title">Behavioral Patterns</div>
        <div class="skills-grid">
          <div class="skill-item">
            <div class="skill-name">Problem Solving</div>
            <div class="skill-score">${applicant.behavioral_traits.problem_solving || 0}/100</div>
          </div>
          <div class="skill-item">
            <div class="skill-name">Teamwork</div>
            <div class="skill-score">${applicant.behavioral_traits.teamwork || 0}/100</div>
          </div>
          <div class="skill-item">
            <div class="skill-name">Initiative</div>
            <div class="skill-score">${applicant.behavioral_traits.initiative || 0}/100</div>
          </div>
          <div class="skill-item">
            <div class="skill-name">Resilience</div>
            <div class="skill-score">${applicant.behavioral_traits.resilience || 0}/100</div>
          </div>
        </div>
      </div>
    `;
  }

  if (applicant.ai_assessment) {
    content += `
      <div class="characteristics-section">
        <div class="section-title">Full Session Feedback</div>
        <div style="background: rgba(59, 130, 246, 0.1); border-radius: 10px; padding: 15px; white-space: pre-wrap; color: rgb(197, 228, 255);">
          ${applicant.ai_assessment}
        </div>
      </div>
    `;
  }

  contentElement.innerHTML = content;

  const growthButton = document.getElementById('growth-plan-button');
  growthButton.onclick = () => {
    const growthHtml = buildGrowthPlan(applicant);
    contentElement.innerHTML = growthHtml + content;
  };

  modal.style.display = 'flex';
}

function closeModal() {
  const modal = document.getElementById('characteristics-modal');
  modal.style.display = 'none';
}

document.getElementById('characteristics-modal').addEventListener('click', function (e) {
  if (e.target === this) {
    closeModal();
  }
});

document.addEventListener('keydown', function (e) {
  if (e.key === 'Escape') {
    closeModal();
  }
});


