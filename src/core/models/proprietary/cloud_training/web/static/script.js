// WebSocket connection
let ws = null;
let currentJob = null;
let metricsChart = null;
let costChart = null;

// Initialize WebSocket connection
function initWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;
    
    ws = new WebSocket(wsUrl);
    
    ws.onopen = () => {
        console.log('WebSocket connected');
        loadJobs();
    };
    
    ws.onclose = () => {
        console.log('WebSocket disconnected');
        setTimeout(initWebSocket, 5000); // Reconnect after 5 seconds
    };
    
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleWebSocketMessage(data);
    };
    
    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
    };
}

// Handle WebSocket messages
function handleWebSocketMessage(data) {
    switch (data.type) {
        case 'status':
            updateJobStatus(data.job_name, data.status);
            break;
        case 'metrics':
            updateJobMetrics(data.job_name, data.metrics);
            break;
        case 'cost':
            updateJobCost(data.job_name, data.cost);
            break;
        case 'logs':
            updateJobLogs(data.job_name, data.logs);
            break;
        case 'error':
            showError(data.message);
            break;
    }
}

// Load training jobs
async function loadJobs() {
    try {
        const response = await fetch('/api/jobs');
        const data = await response.json();
        renderJobList(data.jobs);
    } catch (error) {
        console.error('Failed to load jobs:', error);
        showError('Failed to load training jobs');
    }
}

// Render job list
function renderJobList(jobs) {
    const jobList = document.querySelector('.job-list');
    jobList.innerHTML = '';
    
    jobs.forEach(job => {
        const jobCard = createJobCard(job);
        jobList.appendChild(jobCard);
    });
}

// Create job card
function createJobCard(job) {
    const card = document.createElement('div');
    card.className = 'job-card';
    
    card.innerHTML = `
        <h2>${job.job_name}</h2>
        <div class="job-status status-${job.status.toLowerCase()}">${job.status}</div>
        <div class="job-info">
            <p>Started: ${new Date(job.start_time).toLocaleString()}</p>
            <p>Instance: ${job.instance_type}</p>
        </div>
        <div class="controls">
            <button class="button button-primary" onclick="viewJobDetails('${job.job_name}')">View Details</button>
            ${job.status === 'Running' ? `
                <button class="button button-danger" onclick="stopJob('${job.job_name}')">Stop</button>
            ` : ''}
        </div>
    `;
    
    return card;
}

// View job details
async function viewJobDetails(jobName) {
    try {
        const response = await fetch(`/api/jobs/${jobName}`);
        const job = await response.json();
        
        currentJob = job;
        renderJobDetails(job);
        
        // Subscribe to job updates
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({
                type: 'subscribe',
                job_name: jobName
            }));
        }
    } catch (error) {
        console.error('Failed to load job details:', error);
        showError('Failed to load job details');
    }
}

// Render job details
function renderJobDetails(job) {
    const details = document.querySelector('.job-details');
    details.style.display = 'block';
    
    details.innerHTML = `
        <h2>${job.job_name}</h2>
        <div class="metrics-grid">
            <div class="metric-card">
                <h3>Status</h3>
                <div class="metric-value">${job.status}</div>
            </div>
            <div class="metric-card">
                <h3>Instance Type</h3>
                <div class="metric-value">${job.instance_type}</div>
            </div>
            <div class="metric-card">
                <h3>Started</h3>
                <div class="metric-value">${new Date(job.start_time).toLocaleString()}</div>
            </div>
            <div class="metric-card">
                <h3>Duration</h3>
                <div class="metric-value">${formatDuration(job.duration)}</div>
            </div>
        </div>
        <div class="chart-container">
            <canvas id="metricsChart"></canvas>
        </div>
        <div class="chart-container">
            <canvas id="costChart"></canvas>
        </div>
        <div class="logs-container">
            <div class="log-entries"></div>
        </div>
        <div class="controls">
            ${job.status === 'Running' ? `
                <button class="button button-danger" onclick="stopJob('${job.job_name}')">Stop Training</button>
            ` : ''}
            <button class="button button-primary" onclick="downloadModel('${job.job_name}')">Download Model</button>
        </div>
    `;
    
    // Initialize charts
    initCharts();
}

// Initialize charts
function initCharts() {
    const metricsCtx = document.getElementById('metricsChart').getContext('2d');
    const costCtx = document.getElementById('costChart').getContext('2d');
    
    metricsChart = new Chart(metricsCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Training Loss',
                data: [],
                borderColor: '#2563eb',
                tension: 0.1
            }, {
                label: 'Validation Loss',
                data: [],
                borderColor: '#10b981',
                tension: 0.1
            }]
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
    
    costChart = new Chart(costCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Cost ($)',
                data: [],
                borderColor: '#f59e0b',
                tension: 0.1
            }]
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

// Update job status
function updateJobStatus(jobName, status) {
    if (currentJob && currentJob.job_name === jobName) {
        currentJob.status = status;
        renderJobDetails(currentJob);
    }
    
    // Update job card
    const jobCard = document.querySelector(`.job-card h2:contains('${jobName}')`).closest('.job-card');
    if (jobCard) {
        const statusElement = jobCard.querySelector('.job-status');
        statusElement.className = `job-status status-${status.toLowerCase()}`;
        statusElement.textContent = status;
        
        // Update controls
        const controls = jobCard.querySelector('.controls');
        if (status === 'Running') {
            controls.innerHTML = `
                <button class="button button-primary" onclick="viewJobDetails('${jobName}')">View Details</button>
                <button class="button button-danger" onclick="stopJob('${jobName}')">Stop</button>
            `;
        } else {
            controls.innerHTML = `
                <button class="button button-primary" onclick="viewJobDetails('${jobName}')">View Details</button>
            `;
        }
    }
}

// Update job metrics
function updateJobMetrics(jobName, metrics) {
    if (currentJob && currentJob.job_name === jobName) {
        metricsChart.data.labels.push(new Date().toLocaleTimeString());
        metricsChart.data.datasets[0].data.push(metrics.training_loss);
        metricsChart.data.datasets[1].data.push(metrics.validation_loss);
        metricsChart.update();
    }
}

// Update job cost
function updateJobCost(jobName, cost) {
    if (currentJob && currentJob.job_name === jobName) {
        costChart.data.labels.push(new Date().toLocaleTimeString());
        costChart.data.datasets[0].data.push(cost.total);
        costChart.update();
    }
}

// Update job logs
function updateJobLogs(jobName, logs) {
    if (currentJob && currentJob.job_name === jobName) {
        const logContainer = document.querySelector('.log-entries');
        logs.forEach(log => {
            const logEntry = document.createElement('div');
            logEntry.className = 'log-entry';
            logEntry.textContent = log;
            logContainer.appendChild(logEntry);
            logContainer.scrollTop = logContainer.scrollHeight;
        });
    }
}

// Stop training job
async function stopJob(jobName) {
    try {
        const response = await fetch(`/api/jobs/${jobName}/stop`, {
            method: 'POST'
        });
        
        if (!response.ok) {
            throw new Error('Failed to stop job');
        }
        
        showSuccess('Training job stopped successfully');
    } catch (error) {
        console.error('Failed to stop job:', error);
        showError('Failed to stop training job');
    }
}

// Download model
async function downloadModel(jobName) {
    try {
        const response = await fetch(`/api/jobs/${jobName}/model`);
        const blob = await response.blob();
        
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${jobName}_model.tar.gz`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        showSuccess('Model downloaded successfully');
    } catch (error) {
        console.error('Failed to download model:', error);
        showError('Failed to download model');
    }
}

// Utility functions
function formatDuration(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const remainingSeconds = seconds % 60;
    
    return `${hours}h ${minutes}m ${remainingSeconds}s`;
}

function showError(message) {
    // Implement error notification
    console.error(message);
}

function showSuccess(message) {
    // Implement success notification
    console.log(message);
}

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    initWebSocket();
}); 