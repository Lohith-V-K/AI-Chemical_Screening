document.addEventListener('DOMContentLoaded', () => {

    // --- 1. Number Counter Animation ---
    const counters = document.querySelectorAll('.counter');
    const speed = 200; // The lower the slower

    counters.forEach(counter => {
        const targetAttr = counter.getAttribute('data-target');
        if(!targetAttr) return;
        
        const target = parseFloat(targetAttr);
        const isDecimal = targetAttr.includes('.');
        
        const updateCount = () => {
            const current = parseFloat(counter.innerText) || 0;
            const inc = target / speed;

            if (current < target) {
                if (isDecimal) {
                    counter.innerText = (current + inc).toFixed(1);
                } else {
                    counter.innerText = Math.ceil(current + inc);
                }
                setTimeout(updateCount, 15);
            } else {
                counter.innerText = isDecimal ? target.toFixed(1) : Math.round(target);
            }
        };

        if (target > 0) {
            updateCount();
        }
    });

    // --- 2. Chart.js Initialization ---
    // Only initialize if we are on the dashboard (index.html)
    const toxCanvas = document.getElementById('toxicityChart');
    const perfCanvas = document.getElementById('performanceChart');

    if (toxCanvas && perfCanvas && typeof Chart !== 'undefined') {
        
        // Brand Colors
        const primary = '#1FAF9A';
        const primaryDark = '#0E8F83';
        const safe = '#2ECA7F';
        const warning = '#FFB020';
        const danger = '#FF5A5F';
        const bgGrid = 'rgba(0,0,0,0.03)';

        // Chart defaults
        Chart.defaults.font.family = 'Poppins, sans-serif';
        Chart.defaults.color = '#5B706E';

        // Toxicity Trend Chart (Line)
        new Chart(toxCanvas, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    label: 'Avg Toxicity Level',
                    data: [4.2, 3.8, 3.1, 2.9, 2.6, 2.4],
                    borderColor: primary,
                    backgroundColor: 'rgba(31, 175, 154, 0.1)',
                    borderWidth: 3,
                    tension: 0.4,
                    fill: true,
                    pointBackgroundColor: 'white',
                    pointBorderColor: primary,
                    pointBorderWidth: 2,
                    pointRadius: 4,
                    pointHoverRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: 'rgba(31, 45, 44, 0.9)',
                        padding: 12,
                        titleFont: { size: 13 },
                        bodyFont: { size: 14, weight: 'bold' },
                        cornerRadius: 8,
                        displayColors: false
                    }
                },
                scales: {
                    x: { grid: { display: false } },
                    y: { 
                        grid: { color: bgGrid },
                        beginAtZero: true,
                        max: 6
                    }
                }
            }
        });

        // Alternative Performance (Bar)
        new Chart(perfCanvas, {
            type: 'bar',
            data: {
                labels: ['Thermal', 'Tensile', 'Flexibility', 'Durability'],
                datasets: [
                    {
                        label: 'Original (BPA)',
                        data: [85, 90, 60, 88],
                        backgroundColor: 'rgba(200, 200, 200, 0.5)',
                        borderRadius: 6
                    },
                    {
                        label: 'Alternative (Tritan)',
                        data: [82, 88, 75, 92],
                        backgroundColor: primary,
                        borderRadius: 6
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        align: 'end',
                        labels: {
                            usePointStyle: true,
                            boxWidth: 8,
                            font: { size: 12 }
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(31, 45, 44, 0.9)',
                        padding: 12,
                        titleFont: { size: 13 },
                        bodyFont: { size: 13 },
                        cornerRadius: 8
                    }
                },
                scales: {
                    x: { grid: { display: false } },
                    y: { 
                        grid: { color: bgGrid },
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
    }

    // --- 3. Analyze Page Interactions ---
    const analyzeForm = document.getElementById('analyzeForm');
    const loadingOverlay = document.getElementById('loadingOverlay');
    const resultsSection = document.getElementById('resultsSection');

    if (analyzeForm) {
        analyzeForm.addEventListener('submit', (e) => {
            e.preventDefault(); // Prevent page reload

            // Get chemical name
            const chemName = document.getElementById('chemName').value || 'Unknown Chemical';

            // Hide form elements, show loading
            analyzeForm.style.display = 'none';
            document.getElementById('cardTitle').innerText = 'Analyzing...';
            loadingOverlay.style.display = 'flex';

            // Simulate API Request / Model processing
            setTimeout(() => {
                loadingOverlay.style.display = 'none';
                document.getElementById('cardTitle').innerText = 'Analysis Results: ' + chemName;
                resultsSection.classList.add('show');
            }, 1800); // 1.8s delay for realistic feeling
        });
    }

});

// Global function to reset the analyze form completely
window.resetForm = function() {
    const analyzeForm = document.getElementById('analyzeForm');
    const resultsSection = document.getElementById('resultsSection');
    
    resultsSection.classList.remove('show');
    document.getElementById('cardTitle').innerText = 'Analyze Chemical Form';
    analyzeForm.reset();
    analyzeForm.style.display = 'block';
};
