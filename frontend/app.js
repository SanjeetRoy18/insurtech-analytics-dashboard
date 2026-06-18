// Define the API endpoint URL hosting your data metrics
const API_URL = 'http://127.0.0.1:5000/api/metrics';

// Execute the application data fetch pipeline when the window finishes loading
window.addEventListener('DOMContentLoaded', () => {
    fetchInsuranceMetrics();
});

/**
 * Connects to the Flask backend and handles the data parsing loop
 */
async function fetchInsuranceMetrics() {
    try {
        const response = await fetch(API_URL);

        if(!response.ok) {
            throw new Error(`HTTP Error Status: ${response.status}`);
        }

        const data = await response.json();

        if(data.status === 'success') {
            // Data payloads verified. Initialize the chart renderers.
            renderBarChart(data.barChart);
            renderPieChart(data.pieChart);
            renderHistogram(data.histogram);
            renderScatterPlot(data.scatterPlot);
            renderInsights(data.insights);
        } else {
            console.error("Backend Error payload reported:", data.message);
        }
    } catch (error) {
        console.error("Failed to connect to the Xceedance Analytics API server:", error);
    }
}

/**
 * Renders the Department Expenditure Bar Chart
 */
async function renderBarChart(chartData) {
    const ctx = document.getElementById('barChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: chartData.labels,
            datasets: [{
                label: 'Average Expenditures ($)',
                data: chartData.values,
                backgroundColor: 'rgba(211, 161, 10, 0.85)', // Corporate Navy
                borderColor: 'rgb(216, 179, 12)',
                borderWidth: 1,
                barThickness: 45
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
}

/**
 * Renders the Insurance Plan Tier Distribution Pie Chart
 */
async function renderPieChart(chartData) {
    const ctx = document.getElementById('pieChart').getContext('2d');
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: chartData.labels,
            datasets: [{
                data: chartData.values,
                backgroundColor: [
                    '#991b1b',
                    '#faaa0b',
                    '#ea580c', 
                    '#451a03'  
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
}

/**
 * Renders the Wellness Utilization Frequency Histogram (using a bar configuration)
 */
function renderHistogram(chartData) {
    const ctx = document.getElementById('histogramChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: chartData.labels,
            datasets: [{
                label: 'Employee Count Frequency',
                data: chartData.values,
                backgroundColor: 'rgba(236, 196, 76, 0.75)', // Tech Teal Tint
                borderColor: '#f5a235',
                borderWidth: 1,
                categoryPercentage: 1.0, // Removes spacing gap to look like a true Histogram
                barPercentage: 0.95
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: { title: { display: true, text: 'Stipend Allotment Windows Used' } },
                y: { beginAtZero: true, title: { display: true, text: 'Staff Frequency' } }
            }
        }
    });
}

/**
 * Renders the Premium vs Claim Scatter Plot
 */
function renderScatterPlot(chartData) {
    const ctx = document.getElementById('scatterChart').getContext('2d');
    new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [{
                label: 'Employee Risk Profiles',
                data: chartData, // Directly accepts the [{'x': val, 'y': val}] structure from Python
                backgroundColor: '#efbf32', // Tech Blue
                borderColor: '#2c2003',
                pointRadius: 6,
                pointHoverRadius: 9
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: { title: { display: true, text: 'Annual Premium ($)' } },
                y: { title: { display: true, text: 'Total Claim Amount ($)' } }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        // Custom tooltip configuration to show employee context on point hover
                        label: function(context) {
                            const rawPoint = context.raw;
                            return ` Employee Profile: Premium: $${rawPoint.x}, Claims: $${rawPoint.y}`;
                        }
                    }
                }
            }
        }
    });
}

/**
 * Injects dynamic diagnostic summary bullets into the executive container
 */
function renderInsights(insightsArray) {
    const listElement = document.getElementById('insights-list');
    
    // Clear out the temporary "Analyzing dataset variations..." loader line
    listElement.innerHTML = '';
    
    // Iterate over the strings calculated by Python Pandas and append them as list elements
    insightsArray.forEach(insightText => {
        const li = document.createElement('li');
        li.innerHTML = insightText; // Using innerHTML so <strong> tags render correctly
        listElement.appendChild(li);
    });
}

/**
 * Toggles the collapse/expand states of the floating chat pane
 */
function toggleChat() {
    const chatBody = document.getElementById('chat-body');
    const chatFooter = document.getElementById('chat-footer');
    const toggleIcon = document.getElementById('toggle-icon');

    if (chatBody.style.display === 'none') {
        chatBody.style.display = 'flex';
        chatFooter.style.display = 'flex';
        toggleIcon.innerText = '▲';
    } else {
        chatBody.style.display = 'none';
        chatFooter.style.display = 'none';
        toggleIcon.innerText = '▼';
    }
}

function handleKeyPress(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
}

/**
 * Handles appending message bubbles and fetching answers asynchronously from Flask
 */
async function sendMessage() {
    const inputElement = document.getElementById('chat-input');
    const messageText = inputElement.value.trim();
    if (!messageText) return;

    const chatBody = document.getElementById('chat-body');

    // 1. Render User Bubble
    const userDiv = document.createElement('div');
    userDiv.className = 'chat-message user';
    userDiv.innerText = messageText;
    chatBody.appendChild(userDiv);

    inputElement.value = '';
    chatBody.scrollTop = chatBody.scrollHeight;

    // 2. Render Temporary Loader Bubble
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'chat-message bot';
    loadingDiv.innerText = 'Typing...';
    chatBody.appendChild(loadingDiv);
    chatBody.scrollTop = chatBody.scrollHeight;

    try {
        // 3. Post to Flask API
        const response = await fetch('http://127.0.0.1:5000/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: messageText })
        });
        const data = await response.json();

        chatBody.removeChild(loadingDiv);

        // 4. Render Response (Handles successful model answer OR fallback instructions text)
        const botDiv = document.createElement('div');
        botDiv.className = 'chat-message bot';
        botDiv.innerText = data.reply;
        chatBody.appendChild(botDiv);

    } catch (error) {
        chatBody.removeChild(loadingDiv);
        const errorDiv = document.createElement('div');
        errorDiv.className = 'chat-message bot';
        errorDiv.innerText = 'Network gateway error. Ensure your Flask server is running.';
        chatBody.appendChild(errorDiv);
    }

    chatBody.scrollTop = chatBody.scrollHeight;
}