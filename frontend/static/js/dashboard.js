// Dashboard functionality

const API_BASE = '/api';
let refreshInterval;

// Check authentication
function checkAuth() {
    const token = localStorage.getItem('access_token');
    if (!token) {
        window.location.href = '/login';
        return false;
    }
    return true;
}

// API helper function
async function apiCall(endpoint, method = 'GET', body = null) {
    const token = localStorage.getItem('access_token');

    console.log('API Call:', method, endpoint);
    console.log('Token exists:', !!token);

    if (!token) {
        console.error('No token found, redirecting to login');
        window.location.href = '/login';
        return null;
    }

    const options = {
        method,
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    };

    if (body && method !== 'GET') {
        options.body = JSON.stringify(body);
    }

    try {
        const response = await fetch(`${API_BASE}${endpoint}`, options);

        console.log('Response status:', response.status);

        if (response.status === 401) {
            console.error('Token expired or invalid');
            localStorage.removeItem('access_token');
            localStorage.removeItem('username');
            window.location.href = '/login';
            return null;
        }

        if (!response.ok) {
            const errorText = await response.text();
            console.error('API Error:', response.status, errorText);
            throw new Error(`HTTP ${response.status}: ${errorText}`);
        }

        return await response.json();
    } catch (error) {
        console.error('Fetch error:', error);
        throw error;
    }
}

// Load dashboard data
async function loadDashboard() {
    try {
        const summary = await apiCall('/devices/summary');

        if (!summary) return;

        // Update metrics
        document.getElementById('totalDevices').textContent = summary.total_devices.toLocaleString();
        document.getElementById('onlineDevices').textContent = summary.online.toLocaleString();
        document.getElementById('warningDevices').textContent = summary.warning.toLocaleString();
        document.getElementById('errorDevices').textContent = summary.error.toLocaleString();
        document.getElementById('totalSites').textContent = summary.total_sites;
        document.getElementById('healthPercentage').textContent = summary.health_percentage + '%';

        // Update regions
        updateRegion('region1', summary.regions.region1);
        updateRegion('region2', summary.regions.region2);

        // Update device types
        updateDeviceTypes(summary.device_type_distribution);

        // Update last updated time
        document.getElementById('lastUpdated').textContent = new Date().toLocaleTimeString();

    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

// Update region display
function updateRegion(regionId, regionData) {
    const statusBadge = document.querySelector(`#${regionId}Status .status-badge`);
    statusBadge.textContent = regionData.is_active ? 'Active' : 'Standby';
    statusBadge.className = 'status-badge ' + (regionData.is_active ? 'active' : 'inactive');

    document.getElementById(`${regionId}Devices`).textContent = regionData.total_devices.toLocaleString();
    document.getElementById(`${regionId}Healthy`).textContent = regionData.healthy_devices.toLocaleString();
    document.getElementById(`${regionId}Latency`).textContent = regionData.avg_latency_ms;
}

// Update device types display
function updateDeviceTypes(distribution) {
    const grid = document.getElementById('deviceTypesGrid');
    grid.innerHTML = '';

    for (const [type, count] of Object.entries(distribution)) {
        const card = document.createElement('div');
        card.className = 'device-type-card';
        card.innerHTML = `
            <h4>${type}</h4>
            <div class="count">${count.toLocaleString()}</div>
        `;
        grid.appendChild(card);
    }
}

// Load sites data
async function loadSites() {
    try {
        const sites = await apiCall('/devices/sites');

        if (!sites) return;

        const tbody = document.getElementById('sitesTableBody');
        tbody.innerHTML = '';

        sites.forEach(site => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${site.site_id}</td>
                <td>${site.region}</td>
                <td>${site.total_devices}</td>
                <td style="color: var(--success-color);">${site.online_devices}</td>
                <td style="color: var(--warning-color);">${site.warning_devices}</td>
                <td style="color: var(--error-color);">${site.error_devices}</td>
                <td>${site.avg_temperature ? site.avg_temperature.toFixed(1) + '°C' : '-'}</td>
                <td>${site.avg_efficiency ? site.avg_efficiency.toFixed(1) + '%' : '-'}</td>
            `;
            tbody.appendChild(row);
        });
    } catch (error) {
        console.error('Error loading sites:', error);
    }
}

// Initialize user info
function initUserInfo() {
    const username = localStorage.getItem('username') || 'User';
    document.getElementById('userName').textContent = username;
}

// Logout functionality
document.getElementById('logoutBtn').addEventListener('click', async () => {
    try {
        await apiCall('/auth/logout', 'POST');
    } catch (error) {
        console.error('Logout error:', error);
    } finally {
        localStorage.removeItem('access_token');
        localStorage.removeItem('username');
        window.location.href = '/login';
    }
});

// Failover simulation
document.getElementById('failoverBtn').addEventListener('click', async () => {
    const btn = document.getElementById('failoverBtn');
    const status = document.getElementById('failoverStatus');

    btn.disabled = true;
    btn.textContent = 'Simulating...';
    status.textContent = 'Initiating failover...';

    try {
        const result = await apiCall('/devices/failover?from_region=region1&to_region=region2', 'POST');

        if (result && result.success) {
            status.textContent = `Failover completed! Switched to ${result.to_region}`;
            status.style.color = 'var(--success-color)';

            // Reload dashboard after 1 second
            setTimeout(() => {
                loadDashboard();
            }, 1000);
        } else {
            status.textContent = 'Failover failed';
            status.style.color = 'var(--error-color)';
        }
    } catch (error) {
        console.error('Failover error:', error);
        status.textContent = 'Error during failover';
        status.style.color = 'var(--error-color)';
    } finally {
        btn.disabled = false;
        btn.textContent = 'Simulate Failover';

        // Reset status after 5 seconds
        setTimeout(() => {
            status.textContent = 'Ready to test failover';
            status.style.color = 'var(--text-secondary)';
        }, 5000);
    }
});

// Log analysis
document.getElementById('analyzeLogsBtn').addEventListener('click', async () => {
    const btn = document.getElementById('analyzeLogsBtn');
    btn.disabled = true;
    btn.textContent = 'Analyzing...';

    try {
        const analysis = await apiCall('/monitoring/logs/analyze');

        if (analysis && !analysis.error) {
            // Show results
            document.getElementById('logAnalysisResults').style.display = 'block';

            // Populate table
            const tbody = document.getElementById('errorIpsTableBody');
            tbody.innerHTML = '';

            if (analysis.top_error_ips && analysis.top_error_ips.length > 0) {
                analysis.top_error_ips.forEach((item, index) => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${index + 1}</td>
                        <td>${item.ip}</td>
                        <td>${item.count}</td>
                        <td>${item.percentage}%</td>
                    `;
                    tbody.appendChild(row);
                });
            } else {
                tbody.innerHTML = '<tr><td colspan="4">No error IPs found</td></tr>';
            }
        } else {
            alert('Error analyzing logs: ' + (analysis.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Log analysis error:', error);
        alert('Error analyzing logs');
    } finally {
        btn.disabled = false;
        btn.textContent = 'Analyze Logs';
    }
});

// Generate sample logs
document.getElementById('generateLogsBtn').addEventListener('click', async () => {
    const btn = document.getElementById('generateLogsBtn');
    btn.disabled = true;
    btn.textContent = 'Generating...';

    try {
        const result = await apiCall('/monitoring/logs/generate-sample?num_lines=1000', 'POST');

        if (result && result.message) {
            alert('Sample logs generated successfully!');
        }
    } catch (error) {
        console.error('Generate logs error:', error);
        alert('Error generating logs');
    } finally {
        btn.disabled = false;
        btn.textContent = 'Generate Sample Logs';
    }
});

// AI Query - SIMPLIFIED
document.getElementById('aiQueryBtn').addEventListener('click', async () => {
    const query = document.getElementById('aiQueryInput').value.trim();
    if (!query) {
        alert('Please enter a query');
        return;
    }

    const btn = document.getElementById('aiQueryBtn');
    const responseDiv = document.getElementById('aiResponse');
    const textDiv = document.getElementById('aiResponseText');
    
    btn.disabled = true;
    btn.textContent = 'Asking AI...';
    
    // CLEAR previous response
    responseDiv.style.display = 'block';
    textDiv.textContent = 'Processing...';
    textDiv.style.color = ''; // Reset color

    try {
        const token = localStorage.getItem('access_token');
        const url = `/api/monitoring/ai/query?query=${encodeURIComponent(query)}&include_context=true`;
        
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        const result = await response.json();

        // Display ONLY the response, nothing else
        if (result.response) {
            textDiv.textContent = result.response;
            
            // Add note ONLY if it's actually a mock
            if (result.mock === true) {
                textDiv.textContent += '\n\n📝 Note: Using mock response. Cohere API may not be configured correctly.';
            }
        } else {
            textDiv.textContent = 'Error: No response received';
            textDiv.style.color = 'red';
        }
    } catch (error) {
        textDiv.textContent = 'Error: ' + error.message;
        textDiv.style.color = 'red';
    } finally {
        btn.disabled = false;
        btn.textContent = 'Ask AI';
    }
});

// Allow Enter key for AI query
document.getElementById('aiQueryInput').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        document.getElementById('aiQueryBtn').click();
    }
});

// Initialize dashboard
async function init() {
    if (!checkAuth()) return;

    initUserInfo();
    await loadDashboard();
    await loadSites();

    // Refresh dashboard every 10 seconds
    refreshInterval = setInterval(() => {
        loadDashboard();
    }, 10000);
}

// Run on page load
init();
