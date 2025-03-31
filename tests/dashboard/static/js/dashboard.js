// Chart.js configuration
Chart.defaults.font.family = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif';
Chart.defaults.font.size = 12;

// Global variables
let trendsChart;
let performanceChart;
let currentTimeRange = 7;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    initializeCharts();
    setupEventListeners();
    loadData();
});

// Initialize Chart.js charts
function initializeCharts() {
    // Trends Chart
    const trendsCtx = document.getElementById('trendsChart').getContext('2d');
    trendsChart = new Chart(trendsCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Success',
                    data: [],
                    borderColor: '#28a745',
                    backgroundColor: 'rgba(40, 167, 69, 0.1)',
                    fill: true
                },
                {
                    label: 'Failure',
                    data: [],
                    borderColor: '#dc3545',
                    backgroundColor: 'rgba(220, 53, 69, 0.1)',
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });

    // Performance Chart
    const performanceCtx = document.getElementById('performanceChart').getContext('2d');
    performanceChart = new Chart(performanceCtx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Average Duration (s)',
                    data: [],
                    backgroundColor: '#007bff'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// Setup event listeners
function setupEventListeners() {
    // Time range selector
    document.getElementById('timeRange').addEventListener('change', function(e) {
        currentTimeRange = parseInt(e.target.value);
        loadData();
    });

    // Failure details modal
    const modal = document.getElementById('failureModal');
    const closeBtn = document.getElementsByClassName('close')[0];

    closeBtn.onclick = function() {
        modal.style.display = "none";
    }

    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    }
}

// Load data from API endpoints
async function loadData() {
    try {
        const [summary, trends, failures, performance] = await Promise.all([
            fetch(`/api/summary?days=${currentTimeRange}`).then(r => r.json()),
            fetch(`/api/trends?days=${currentTimeRange}`).then(r => r.json()),
            fetch(`/api/failures?days=${currentTimeRange}`).then(r => r.json()),
            fetch(`/api/performance?days=${currentTimeRange}`).then(r => r.json())
        ]);

        updateSummary(summary);
        updateTrendsChart(trends);
        updateFailuresTable(failures);
        updatePerformanceChart(performance);
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        showError('Failed to load dashboard data. Please try again later.');
    }
}

// Update summary cards
function updateSummary(summary) {
    // Overall status
    document.getElementById('totalTests').textContent = summary.total_tests;
    document.getElementById('successRate').textContent = `${summary.success_rate}%`;
    document.getElementById('failureRate').textContent = `${summary.failure_rate}%`;
    document.getElementById('skippedRate').textContent = `${summary.skipped_rate}%`;

    // Performance metrics
    document.getElementById('avgDuration').textContent = `${summary.avg_duration.toFixed(2)}s`;
    document.getElementById('maxDuration').textContent = `${summary.max_duration.toFixed(2)}s`;
    document.getElementById('minDuration').textContent = `${summary.min_duration.toFixed(2)}s`;
    document.getElementById('stdDevDuration').textContent = `${summary.std_dev_duration.toFixed(2)}s`;
}

// Update trends chart
function updateTrendsChart(trends) {
    trendsChart.data.labels = trends.dates;
    trendsChart.data.datasets[0].data = trends.success_counts;
    trendsChart.data.datasets[1].data = trends.failure_counts;
    trendsChart.update();
}

// Update failures table
function updateFailuresTable(failures) {
    const tbody = document.querySelector('#failuresTable tbody');
    tbody.innerHTML = '';

    failures.forEach(failure => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${failure.test_name}</td>
            <td>${failure.category}</td>
            <td class="failure-count">${failure.count}</td>
            <td>${new Date(failure.last_occurrence).toLocaleString()}</td>
            <td>
                <button onclick="showFailureDetails('${failure.test_name}')">Details</button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

// Update performance chart
function updatePerformanceChart(performance) {
    performanceChart.data.labels = performance.categories;
    performanceChart.data.datasets[0].data = performance.avg_durations;
    performanceChart.update();
}

// Show failure details in modal
async function showFailureDetails(testName) {
    try {
        const response = await fetch(`/api/failures/${encodeURIComponent(testName)}?days=${currentTimeRange}`);
        const details = await response.json();
        
        const modal = document.getElementById('failureModal');
        const content = document.getElementById('failureDetails');
        
        content.innerHTML = `
            <h2>${testName}</h2>
            <p><strong>Category:</strong> ${details.category}</p>
            <p><strong>Total Failures:</strong> ${details.count}</p>
            <p><strong>Last Occurrence:</strong> ${new Date(details.last_occurrence).toLocaleString()}</p>
            <h3>Recent Error Messages:</h3>
            <pre>${details.recent_errors.join('\n\n')}</pre>
            <h3>Stack Traces:</h3>
            <pre>${details.stack_traces.join('\n\n')}</pre>
        `;
        
        modal.style.display = "block";
    } catch (error) {
        console.error('Error loading failure details:', error);
        showError('Failed to load failure details. Please try again later.');
    }
}

// Show error message
function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    
    document.querySelector('.container').insertBefore(errorDiv, document.querySelector('.summary-cards'));
    
    setTimeout(() => {
        errorDiv.remove();
    }, 5000);
} 