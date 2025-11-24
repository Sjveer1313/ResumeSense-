// Main JavaScript for ResumeSense

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('analyzeForm');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const btnText = document.getElementById('btnText');
    const btnLoader = document.getElementById('btnLoader');
    const resultsSection = document.getElementById('results');
    const errorDiv = document.getElementById('error');
    setupInsightTabs();

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Reset UI
        resultsSection.style.display = 'none';
        errorDiv.style.display = 'none';
        
        // Show loading state
        analyzeBtn.disabled = true;
        btnText.textContent = 'Analyzing...';
        btnLoader.style.display = 'inline-block';

        try {
            const formData = new FormData(form);
            
            const response = await fetch('/api/analyze', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Analysis failed');
            }

            // Display results
            displayResults(data);
            resultsSection.style.display = 'block';
            
        } catch (error) {
            console.error('Error:', error);
            errorDiv.textContent = error.message || 'An error occurred during analysis. Please try again.';
            errorDiv.style.display = 'block';
        } finally {
            // Reset button state
            analyzeBtn.disabled = false;
            btnText.textContent = 'Analyze Resume';
            btnLoader.style.display = 'none';
        }
    });

    function displayResults(data) {
        // Quality Score
        const qualityScore = data.quality_score || 0;
        document.getElementById('qualityScore').textContent = qualityScore.toFixed(1);
        const qualityFill = document.getElementById('qualityFill');
        qualityFill.style.width = qualityScore + '%';
        qualityFill.style.background = getScoreColor(qualityScore);

        // ATS Score
        if (data.ats_score !== undefined) {
            document.getElementById('atsCard').style.display = 'block';
            document.getElementById('atsScore').textContent = data.ats_score.toFixed(1);
            const atsFill = document.getElementById('atsFill');
            atsFill.style.width = data.ats_score + '%';
            atsFill.style.background = getScoreColor(data.ats_score);
            
            // ATS Report
            displayATSReport(data.ats_report);
        }

        // Match Score
        if (data.match_score !== null && data.match_score !== undefined) {
            document.getElementById('matchCard').style.display = 'block';
            document.getElementById('matchScore').textContent = data.match_score.toFixed(1) + '%';
            const matchFill = document.getElementById('matchFill');
            matchFill.style.width = data.match_score + '%';
            matchFill.style.background = getScoreColor(data.match_score);
            
            // Match Details
            displayMatchDetails(data.match_details);
        }

        // Power Verbs
        if (data.power_verbs) {
            displayPowerVerbs(data.power_verbs);
        }

        // Resume insights (projects & achievements)
        displayResumeInsights(data.resume_insights);
    }

    function displayATSReport(atsReport) {
        const atsPanel = document.getElementById('atsPanel');
        const recommendationsDiv = document.getElementById('atsRecommendations');

        atsPanel.style.display = 'block';
        recommendationsDiv.innerHTML = '';

        const summary = document.createElement('div');
        summary.className = 'recommendation-item neutral';
        summary.innerHTML = `
            <div>
                <strong>Section Coverage</strong><br>
                Education: ${atsReport.section_checks.education ? '✅' : '⚠️'} |
                Experience: ${atsReport.section_checks.experience ? '✅' : '⚠️'} |
                Skills: ${atsReport.section_checks.skills ? '✅' : '⚠️'}
            </div>
        `;
        recommendationsDiv.appendChild(summary);

        // Display recommendations
        if (atsReport.recommendations && atsReport.recommendations.length > 0) {
            const title = document.createElement('h4');
            title.textContent = 'Recommendations';
            recommendationsDiv.appendChild(title);

            atsReport.recommendations.forEach(rec => {
                const recItem = document.createElement('div');
                recItem.className = 'recommendation-item';
                recItem.textContent = rec;
                recommendationsDiv.appendChild(recItem);
            });
        } else {
            const ok = document.createElement('p');
            ok.style.color = '#28a745';
            ok.style.fontWeight = '600';
            ok.textContent = '✓ Resume passes key ATS checks.';
            recommendationsDiv.appendChild(ok);
        }
    }

    function displayPowerVerbs(verbsData) {
        const verbsPanel = document.getElementById('verbsPanel');
        const verbFindingsDiv = document.getElementById('verbFindings');

        verbsPanel.style.display = 'block';

        if (verbsData.findings && verbsData.findings.length > 0) {
            verbFindingsDiv.innerHTML = '';
            
            verbsData.findings.forEach(finding => {
                const findingDiv = document.createElement('div');
                findingDiv.className = 'verb-finding';
                
                findingDiv.innerHTML = `
                    <strong>Found: "${finding.weak_verb}"</strong>
                    <p style="color: #6c757d; margin: 8px 0; font-size: 0.9em;">${finding.context}</p>
                    <div class="verb-suggestions">
                        <span style="color: #6c757d; margin-right: 8px;">Suggestions:</span>
                        ${finding.suggestions.map(verb => 
                            `<span class="verb-suggestion">${verb}</span>`
                        ).join('')}
                    </div>
                `;
                
                verbFindingsDiv.appendChild(findingDiv);
            });
        } else {
            verbFindingsDiv.innerHTML = '<p style="color: #28a745; font-weight: 600;">✓ No weak verbs found! Your resume uses strong action verbs.</p>';
        }

        // Display stats if available
        if (verbsData.stats) {
            const statsDiv = document.createElement('div');
            statsDiv.style.marginTop = '20px';
            statsDiv.style.padding = '15px';
            statsDiv.style.background = 'white';
            statsDiv.style.borderRadius = '8px';
            statsDiv.innerHTML = `
                <h4>Power Verb Statistics</h4>
                <p>Strong Verbs: ${verbsData.stats.strong_verb_count} | 
                   Weak Verbs: ${verbsData.stats.weak_verb_count} | 
                   Power Verb Score: ${verbsData.stats.power_verb_score.toFixed(1)}%</p>
            `;
            verbFindingsDiv.appendChild(statsDiv);
        }
    }

    function displayMatchDetails(matchDetails) {
        if (!matchDetails) return;

        const matchPanel = document.getElementById('matchPanel');
        const matchDetailsDiv = document.getElementById('matchDetails');

        matchPanel.style.display = 'block';

        let html = '';

        // Common keywords
        if (matchDetails.common_keywords && matchDetails.common_keywords.length > 0) {
            html += '<h4>Matched Keywords:</h4>';
            html += '<div class="match-keywords">';
            matchDetails.common_keywords.forEach(keyword => {
                html += `<span class="keyword matched">${keyword}</span>`;
            });
            html += '</div>';
        }

        // Missing keywords
        if (matchDetails.missing_keywords && matchDetails.missing_keywords.length > 0) {
            html += '<h4 style="margin-top: 20px;">Missing Keywords:</h4>';
            html += '<div class="match-keywords">';
            matchDetails.missing_keywords.forEach(keyword => {
                html += `<span class="keyword missing">${keyword}</span>`;
            });
            html += '</div>';
        }

        // Important keywords
        if (matchDetails.matched_important_keywords && matchDetails.matched_important_keywords.length > 0) {
            html += '<h4 style="margin-top: 20px;">Matched Important Keywords:</h4>';
            html += '<div class="match-keywords">';
            matchDetails.matched_important_keywords.forEach(keyword => {
                html += `<span class="keyword matched">${keyword}</span>`;
            });
            html += '</div>';
        }

        // Stats
        html += '<div style="margin-top: 20px; padding: 15px; background: white; border-radius: 8px;">';
        html += `<p><strong>Important Keywords Matched:</strong> ${matchDetails.important_keywords_matched} / ${matchDetails.important_keywords_total}</p>`;
        html += '</div>';

        matchDetailsDiv.innerHTML = html;
    }

    function displayResumeInsights(insights) {
        const panel = document.getElementById('insightsPanel');

        if (!insights || ((!insights.projects || insights.projects.length === 0) &&
            (!insights.achievements || insights.achievements.length === 0))) {
            panel.style.display = 'none';
            return;
        }

        panel.style.display = 'block';
        renderProjects(insights.projects || []);
        renderAchievements(insights.achievements || []);
    }

    function renderProjects(projects) {
        const container = document.getElementById('projectsList');
        if (!projects.length) {
            container.innerHTML = '<p class="empty-message">No project highlights detected. Add quantified, tech-focused projects to boost credibility.</p>';
            return;
        }

        container.innerHTML = projects.map(project => {
            const techStackHtml = project.tech_stack && project.tech_stack.length
                ? `<div class="tech-stack">
                        ${project.tech_stack.map(tech => `<span class="tech-badge">${tech}</span>`).join('')}
                   </div>`
                : '';

            const confidence = project.confidence !== undefined
                ? `<div class="card-meta">Confidence ${Math.round(project.confidence * 100)}%</div>`
                : '';

            return `
                <div class="project-card">
                    ${confidence}
                    <h4>${project.title}</h4>
                    <p>${project.summary}</p>
                    ${techStackHtml}
                </div>
            `;
        }).join('');
    }

    function renderAchievements(achievements) {
        const container = document.getElementById('achievementsList');
        if (!achievements.length) {
            container.innerHTML = '<p class="empty-message">No co-curricular achievements detected. Highlight leadership roles, awards, or community work.</p>';
            return;
        }

        container.innerHTML = achievements.map(item => {
            const impactHtml = item.impact_keywords && item.impact_keywords.length
                ? `<div class="tech-stack" style="margin-top: 10px;">
                        ${item.impact_keywords.map(keyword => `<span class="tech-badge">${keyword}</span>`).join('')}
                   </div>`
                : '';

            return `
                <div class="achievement-card">
                    <div class="card-meta">${item.category}</div>
                    <h4>${item.title}</h4>
                    <p>${item.details}</p>
                    ${impactHtml}
                </div>
            `;
        }).join('');
    }

    function setupInsightTabs() {
        const tabButtons = document.querySelectorAll('.tab-btn');
        const tabContents = document.querySelectorAll('.tab-content');

        tabButtons.forEach(button => {
            button.addEventListener('click', () => {
                if (button.classList.contains('active')) return;

                tabButtons.forEach(btn => btn.classList.remove('active'));
                tabContents.forEach(tab => tab.classList.remove('active'));

                button.classList.add('active');
                const target = document.getElementById(button.dataset.target);
                if (target) {
                    target.classList.add('active');
                }
            });
        });
    }

    function getScoreColor(score) {
        if (score >= 80) {
            return 'linear-gradient(90deg, #28a745 0%, #20c997 100%)';
        } else if (score >= 60) {
            return 'linear-gradient(90deg, #ffc107 0%, #ff9800 100%)';
        } else {
            return 'linear-gradient(90deg, #dc3545 0%, #c82333 100%)';
        }
    }
});


