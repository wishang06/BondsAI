let applicantsData = [];

// Load applicants when page loads
document.addEventListener('DOMContentLoaded', function() {
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
            applicantsData = data.applicants;
            displayApplicants(data.applicants);
            container.style.display = 'block';
        } else {
            noApplicants.style.display = 'block';
        }
    } catch (error) {
        console.error('Error loading applicants:', error);
        noApplicants.style.display = 'block';
    } finally {
        loading.style.display = 'none';
    }
}

function displayApplicants(applicants) {
    const grid = document.getElementById('applicants-grid');
    grid.innerHTML = '';

    applicants.forEach((applicant, index) => {
        const bubble = document.createElement('div');
        bubble.className = 'applicant-bubble';
        bubble.onclick = () => showCharacteristics(index);
        
        bubble.innerHTML = `
            <div class="applicant-name">${applicant.name || 'Anonymous'}</div>
            <div class="applicant-info">Interview: ${applicant.interview_date}</div>
            <div class="applicant-info">Exchanges: ${applicant.conversation_count}</div>
            <div class="applicant-score">Score: ${applicant.final_score || 'N/A'}/100</div>
        `;
        
        grid.appendChild(bubble);
    });
}

function showCharacteristics(index) {
    const applicant = applicantsData[index];
    const modal = document.getElementById('characteristics-modal');
    const nameElement = document.getElementById('modal-candidate-name');
    const infoElement = document.getElementById('modal-candidate-info');
    const contentElement = document.getElementById('modal-characteristics-content');

    nameElement.textContent = applicant.name || 'Anonymous Candidate';
    infoElement.textContent = `Interview completed on ${applicant.interview_date} • ${applicant.conversation_count} exchanges`;

    // Build characteristics content
    let content = '';

    // Technical Skills
    if (applicant.technical_skills) {
        content += `
            <div class="characteristics-section">
                <div class="section-title">Technical Skills</div>
                <div class="skills-grid">
                    <div class="skill-item">
                        <div class="skill-name">Quantitative Reasoning</div>
                        <div class="skill-score">${applicant.technical_skills.quantitative_reasoning || 0}/100</div>
                    </div>
                    <div class="skill-item">
                        <div class="skill-name">Programming</div>
                        <div class="skill-score">${applicant.technical_skills.programming || 0}/100</div>
                    </div>
                    <div class="skill-item">
                        <div class="skill-name">Market Knowledge</div>
                        <div class="skill-score">${applicant.technical_skills.market_knowledge || 0}/100</div>
                    </div>
                    <div class="skill-item">
                        <div class="skill-name">Data Analysis</div>
                        <div class="skill-score">${applicant.technical_skills.data_analysis || 0}/100</div>
                    </div>
                </div>
            </div>
        `;
    }

    // Behavioral Traits
    if (applicant.behavioral_traits) {
        content += `
            <div class="characteristics-section">
                <div class="section-title">Behavioral Traits</div>
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
                    <div class="skill-item">
                        <div class="skill-name">Adaptability</div>
                        <div class="skill-score">${applicant.behavioral_traits.adaptability || 0}/100</div>
                    </div>
                </div>
            </div>
        `;
    }

    // Cultural Fit
    if (applicant.cultural_fit) {
        content += `
            <div class="characteristics-section">
                <div class="section-title">Cultural Fit</div>
                <div class="skills-grid">
                    <div class="skill-item">
                        <div class="skill-name">Collaborative Thinking</div>
                        <div class="skill-score">${applicant.cultural_fit.collaborative_thinking || 0}/100</div>
                    </div>
                    <div class="skill-item">
                        <div class="skill-name">Continuous Learning</div>
                        <div class="skill-score">${applicant.cultural_fit.continuous_learning || 0}/100</div>
                    </div>
                    <div class="skill-item">
                        <div class="skill-name">Challenge Seeking</div>
                        <div class="skill-score">${applicant.cultural_fit.challenge_seeking || 0}/100</div>
                    </div>
                    <div class="skill-item">
                        <div class="skill-name">Entrepreneurial Spirit</div>
                        <div class="skill-score">${applicant.cultural_fit.entrepreneurial_spirit || 0}/100</div>
                    </div>
                </div>
            </div>
        `;
    }

    // Soft Skills
    if (applicant.soft_skills) {
        content += `
            <div class="characteristics-section">
                <div class="section-title">Soft Skills</div>
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

    // Insights
    if (applicant.insights) {
        if (applicant.insights.strengths && applicant.insights.strengths.length > 0) {
            content += `
                <div class="characteristics-section">
                    <div class="section-title">Key Strengths</div>
                    <ul class="insights-list">
                        ${applicant.insights.strengths.map(strength => `<li>${strength}</li>`).join('')}
                    </ul>
                </div>
            `;
        }

        if (applicant.insights.weaknesses && applicant.insights.weaknesses.length > 0) {
            content += `
                <div class="characteristics-section">
                    <div class="section-title">Areas for Improvement</div>
                    <ul class="insights-list">
                        ${applicant.insights.weaknesses.map(weakness => `<li>${weakness}</li>`).join('')}
                    </ul>
                </div>
            `;
        }

        if (applicant.insights.recommendations && applicant.insights.recommendations.length > 0) {
            content += `
                <div class="characteristics-section">
                    <div class="section-title">Recommendations</div>
                    <ul class="insights-list">
                        ${applicant.insights.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                    </ul>
                </div>
            `;
        }
    }

    // AI Assessment Summary
    if (applicant.ai_assessment) {
        content += `
            <div class="characteristics-section">
                <div class="section-title">AI Assessment Summary</div>
                <div style="background: rgba(59, 130, 246, 0.1); border-radius: 10px; padding: 15px; white-space: pre-wrap; color: white;">${applicant.ai_assessment}</div>
            </div>
        `;
    }

    contentElement.innerHTML = content;
    modal.style.display = 'flex';
}

function closeModal() {
    const modal = document.getElementById('characteristics-modal');
    modal.style.display = 'none';
}

// Close modal when clicking outside
document.getElementById('characteristics-modal').addEventListener('click', function(e) {
    if (e.target === this) {
        closeModal();
    }
});

// Close modal with Escape key
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeModal();
    }
});