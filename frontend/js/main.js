/**
 * Traffic Violation Management System
 * Main JavaScript File
 * Location: frontend/static/js/main.js
 */

// ============================================
// GLOBAL VARIABLES
// ============================================

let currentUser = null;
let violations = [];
let violationTypes = [];
let areas = [];

// API Base URL (adjust if needed)
const API_BASE_URL = window.location.origin;

// ============================================
// INITIALIZATION
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('Traffic Violation System Initialized');
    
    // Check if user is logged in
    checkAuthentication();
    
    // Load initial data if authenticated
    if (isAuthenticated()) {
        loadInitialData();
    }
});

// ============================================
// AUTHENTICATION
// ============================================

/**
 * Check if user is authenticated
 */
function isAuthenticated() {
    const user = sessionStorage.getItem('user');
    return user !== null;
}

/**
 * Check authentication and redirect if needed
 */
function checkAuthentication() {
    const currentPage = window.location.pathname;
    const user = sessionStorage.getItem('user');
    
    // If on dashboard but not logged in, redirect to login
    if (currentPage.includes('dashboard') && !user) {
        window.location.href = 'login.html';
        return;
    }
    
    // If on login but already logged in, redirect to dashboard
    if (currentPage.includes('login') && user) {
        window.location.href = 'dashboard.html';
        return;
    }
    
    // Load user data if authenticated
    if (user) {
        currentUser = JSON.parse(user);
        updateUserInterface();
    }
}

/**
 * Update UI based on current user
 */
function updateUserInterface() {
    if (!currentUser) return;
    
    // Update user info in header
    const roleElement = document.getElementById('userRole');
    const nameElement = document.getElementById('userName');
    
    if (roleElement) {
        roleElement.textContent = capitalizeFirst(currentUser.role);
    }
    
    if (nameElement) {
        nameElement.textContent = currentUser.name || currentUser.full_name || currentUser.username;
    }
    
    // Show/hide features based on role
    updateRoleBasedUI();
}

/**
 * Update UI elements based on user role
 */
function updateRoleBasedUI() {
    const role = currentUser.role;
    
    // Hide register violation tab for citizens
    if (role === 'citizen') {
        const registerTab = document.querySelector('[onclick*="register"]');
        if (registerTab) {
            registerTab.style.display = 'none';
        }
    }
    
    // Hide analytics for citizens
    if (role === 'citizen') {
        const analyticsTab = document.querySelector('[onclick*="analytics"]');
        if (analyticsTab) {
            analyticsTab.style.display = 'none';
        }
    }
}

/**
 * Handle user logout
 */
function logout() {
    if (confirm('Are you sure you want to logout?')) {
        sessionStorage.clear();
        window.location.href = 'login.html';
    }
}

// ============================================
// DATA LOADING
// ============================================

/**
 * Load all initial data
 */
async function loadInitialData() {
    try {
        await Promise.all([
            loadViolationTypes(),
            loadAreas(),
            loadViolations()
        ]);
        
        updateDashboard();
        loadViolationsTable();
        loadAnalytics();
    } catch (error) {
        console.error('Error loading initial data:', error);
        showAlert('Failed to load data. Please refresh the page.', 'error');
    }
}

/**
 * Load violation types from API
 */
async function loadViolationTypes() {
    // In production, fetch from API
    // const response = await fetch(`${API_BASE_URL}/api/violation-types`);
    // const data = await response.json();
    // violationTypes = data.data;
    
    // Mock data for now
    violationTypes = [
        { type_id: 1, type_name: 'Speeding', base_fine: 500 },
        { type_id: 2, type_name: 'Red Light Violation', base_fine: 1000 },
        { type_id: 3, type_name: 'No Helmet', base_fine: 300 },
        { type_id: 4, type_name: 'Wrong Parking', base_fine: 200 },
        { type_id: 5, type_name: 'DUI', base_fine: 5000 },
        { type_id: 6, type_name: 'No Seat Belt', base_fine: 500 },
        { type_id: 7, type_name: 'Mobile Phone Usage', base_fine: 750 }
    ];
    
    populateViolationTypesDropdown();
}

/**
 * Load areas from API
 */
async function loadAreas() {
    // In production, fetch from API
    // const response = await fetch(`${API_BASE_URL}/api/areas`);
    // const data = await response.json();
    // areas = data.data;
    
    // Mock data for now
    areas = [
        { area_id: 1, area_name: 'MG Road', city: 'Bangalore' },
        { area_id: 2, area_name: 'Connaught Place', city: 'Delhi' },
        { area_id: 3, area_name: 'Marine Drive', city: 'Mumbai' },
        { area_id: 4, area_name: 'Anna Salai', city: 'Chennai' },
        { area_id: 5, area_name: 'Park Street', city: 'Kolkata' }
    ];
    
    populateAreasDropdown();
}

/**
 * Load violations from API
 */
async function loadViolations() {
    // In production, fetch from API
    // const response = await fetch(`${API_BASE_URL}/api/violations`);
    // const data = await response.json();
    // violations = data.data;
    
    // Mock data for now
    violations = [
        {
            violation_id: 1,
            vehicle_number: 'KA01AB1234',
            owner_name: 'John Doe',
            type_name: 'Speeding',
            area_name: 'MG Road',
            violation_date: '2025-01-15 10:30',
            fine_amount: 500,
            status: 'paid'
        },
        {
            violation_id: 2,
            vehicle_number: 'DL02CD5678',
            owner_name: 'Jane Smith',
            type_name: 'Red Light Violation',
            area_name: 'Connaught Place',
            violation_date: '2025-01-14 14:45',
            fine_amount: 1000,
            status: 'unpaid'
        },
        {
            violation_id: 3,
            vehicle_number: 'MH03EF9012',
            owner_name: 'Mike Brown',
            type_name: 'No Helmet',
            area_name: 'Marine Drive',
            violation_date: '2025-01-13 09:15',
            fine_amount: 300,
            status: 'paid'
        }
    ];
}

// ============================================
// DROPDOWN POPULATION
// ============================================

/**
 * Populate violation types dropdown
 */
function populateViolationTypesDropdown() {
    const select = document.getElementById('violationType');
    if (!select) return;
    
    // Clear existing options except the first one
    select.innerHTML = '<option value="">Select Type</option>';
    
    violationTypes.forEach(type => {
        const option = document.createElement('option');
        option.value = type.type_id;
        option.textContent = `${type.type_name} - ₹${type.base_fine}`;
        option.dataset.fine = type.base_fine;
        select.appendChild(option);
    });
    
    // Add change event listener
    select.addEventListener('change', function() {
        const selectedOption = this.options[this.selectedIndex];
        const fineInput = document.getElementById('fineAmount');
        if (fineInput && selectedOption.dataset.fine) {
            fineInput.value = selectedOption.dataset.fine;
        }
    });
}

/**
 * Populate areas dropdown
 */
function populateAreasDropdown() {
    const select = document.getElementById('area');
    if (!select) return;
    
    // Clear existing options except the first one
    select.innerHTML = '<option value="">Select Area</option>';
    
    areas.forEach(area => {
        const option = document.createElement('option');
        option.value = area.area_id;
        option.textContent = `${area.area_name}, ${area.city}`;
        select.appendChild(option);
    });
}

// ============================================
// TAB SWITCHING
// ============================================

/**
 * Switch between tabs
 */
function switchTab(tabName) {
    // Hide all tab contents
    const tabContents = document.querySelectorAll('.tab-content');
    tabContents.forEach(tab => tab.classList.remove('active'));
    
    // Remove active class from all buttons
    const tabButtons = document.querySelectorAll('.tab-btn');
    tabButtons.forEach(btn => btn.classList.remove('active'));
    
    // Show selected tab
    const selectedTab = document.getElementById(tabName);
    if (selectedTab) {
        selectedTab.classList.add('active');
    }
    
    // Add active class to clicked button
    event.target.classList.add('active');
    
    // Refresh data for specific tabs
    if (tabName === 'dashboard') {
        updateDashboard();
    } else if (tabName === 'violations') {
        loadViolationsTable();
    } else if (tabName === 'analytics') {
        loadAnalytics();
    }
}

// ============================================
// DASHBOARD
// ============================================

/**
 * Update dashboard statistics
 */
function updateDashboard() {
    const total = violations.reduce((sum, v) => sum + v.fine_amount, 0);
    const collected = violations.filter(v => v.status === 'paid')
        .reduce((sum, v) => sum + v.fine_amount, 0);
    const pending = total - collected;
    
    // Update stat cards
    updateElement('totalViolations', violations.length);
    updateElement('totalFines', formatCurrency(total));
    updateElement('collectedAmount', formatCurrency(collected));
    updateElement('pendingAmount', formatCurrency(pending));
    
    // Update recent violations table
    updateRecentViolationsTable();
}

/**
 * Update recent violations table
 */
function updateRecentViolationsTable() {
    const tbody = document.getElementById('recentViolationsBody');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    const recentViolations = violations.slice(0, 5);
    
    recentViolations.forEach(v => {
        const row = createTableRow([
            v.violation_id,
            v.vehicle_number,
            v.type_name,
            v.area_name,
            formatDateTime(v.violation_date),
            formatCurrency(v.fine_amount),
            createStatusBadge(v.status)
        ]);
        tbody.appendChild(row);
    });
}

// ============================================
// VIOLATION REGISTRATION
// ============================================

/**
 * Handle violation form submission
 */
function registerViolation(event) {
    event.preventDefault();
    
    // Get form data
    const formData = {
        vehicle_number: getValue('vehicleNumber'),
        type_id: getValue('violationType'),
        area_id: getValue('area'),
        violation_date: getValue('violationDate'),
        fine_amount: getValue('fineAmount'),
        notes: getValue('notes')
    };
    
    // Validate form
    if (!validateViolationForm(formData)) {
        return;
    }
    
    // In production, send to API
    // submitViolationToAPI(formData);
    
    // Mock submission
    const newViolation = {
        violation_id: violations.length + 1,
        vehicle_number: formData.vehicle_number.toUpperCase(),
        owner_name: 'Unknown',
        type_name: getViolationTypeName(formData.type_id),
        area_name: getAreaName(formData.area_id),
        violation_date: formData.violation_date.replace('T', ' '),
        fine_amount: parseFloat(formData.fine_amount),
        status: 'unpaid'
    };
    
    violations.unshift(newViolation);
    
    // Show success message
    showAlert('Violation registered successfully!', 'success', 'registerAlert');
    
    // Reset form
    document.getElementById('violationForm').reset();
    
    // Update dashboard
    updateDashboard();
    loadViolationsTable();
}

/**
 * Validate violation form
 */
function validateViolationForm(data) {
    if (!data.vehicle_number) {
        showAlert('Please enter vehicle number', 'error', 'registerAlert');
        return false;
    }
    
    if (!data.type_id) {
        showAlert('Please select violation type', 'error', 'registerAlert');
        return false;
    }
    
    if (!data.area_id) {
        showAlert('Please select area', 'error', 'registerAlert');
        return false;
    }
    
    if (!data.violation_date) {
        showAlert('Please select date and time', 'error', 'registerAlert');
        return false;
    }
    
    return true;
}

// ============================================
// VIOLATIONS TABLE
// ============================================

/**
 * Load violations table
 */
function loadViolationsTable() {
    const tbody = document.getElementById('violationsTableBody');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    violations.forEach(v => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${v.violation_id}</td>
            <td>${v.vehicle_number}</td>
            <td>${v.owner_name}</td>
            <td>${v.type_name}</td>
            <td>${v.area_name}</td>
            <td>${formatDateTime(v.violation_date)}</td>
            <td>${formatCurrency(v.fine_amount)}</td>
            <td>${createStatusBadgeHTML(v.status)}</td>
            <td>${createActionButtons(v)}</td>
        `;
        tbody.appendChild(row);
    });
}

/**
 * Create action buttons for violation
 */
function createActionButtons(violation) {
    if (violation.status === 'unpaid' && currentUser && currentUser.role !== 'citizen') {
        return `<button class="btn btn-sm btn-success" onclick="markAsPaid(${violation.violation_id})">Mark Paid</button>`;
    }
    return '-';
}

/**
 * Mark violation as paid
 */
function markAsPaid(violationId) {
    const violation = violations.find(v => v.violation_id === violationId);
    
    if (!violation) {
        showAlert('Violation not found', 'error');
        return;
    }
    
    if (confirm(`Mark violation #${violationId} as paid?`)) {
        violation.status = 'paid';
        
        // In production, send to API
        // updateViolationStatusAPI(violationId, 'paid');
        
        showAlert('Payment recorded successfully!', 'success');
        updateDashboard();
        loadViolationsTable();
        loadAnalytics();
    }
}

/**
 * Search violations
 */
function searchViolations() {
    const searchTerm = getValue('searchInput').toLowerCase();
    
    if (!searchTerm) {
        loadViolationsTable();
        return;
    }
    
    const filtered = violations.filter(v => 
        v.vehicle_number.toLowerCase().includes(searchTerm) ||
        (v.owner_name && v.owner_name.toLowerCase().includes(searchTerm))
    );
    
    const tbody = document.getElementById('violationsTableBody');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    filtered.forEach(v => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${v.violation_id}</td>
            <td>${v.vehicle_number}</td>
            <td>${v.owner_name}</td>
            <td>${v.type_name}</td>
            <td>${v.area_name}</td>
            <td>${formatDateTime(v.violation_date)}</td>
            <td>${formatCurrency(v.fine_amount)}</td>
            <td>${createStatusBadgeHTML(v.status)}</td>
            <td>${createActionButtons(v)}</td>
        `;
        tbody.appendChild(row);
    });
}

// ============================================
// ANALYTICS
// ============================================

/**
 * Load analytics data
 */
function loadAnalytics() {
    updateAnalyticsStats();
    displayAreaChart();
    displayTypeChart();
}

/**
 * Update analytics statistics
 */
function updateAnalyticsStats() {
    const paidCount = violations.filter(v => v.status === 'paid').length;
    const unpaidCount = violations.filter(v => v.status === 'unpaid').length;
    const total = violations.reduce((sum, v) => sum + v.fine_amount, 0);
    const collected = violations.filter(v => v.status === 'paid')
        .reduce((sum, v) => sum + v.fine_amount, 0);
    const collectionRate = total > 0 ? ((collected / total) * 100).toFixed(1) : 0;
    const avgFine = violations.length > 0 ? (total / violations.length).toFixed(2) : 0;
    
    updateElement('collectionRate', collectionRate + '%');
    updateElement('paidCount', paidCount);
    updateElement('unpaidCount', unpaidCount);
    updateElement('avgFine', formatCurrency(avgFine));
}

/**
 * Display area chart
 */
function displayAreaChart() {
    const container = document.getElementById('areaChart');
    if (!container) return;
    
    const areaStats = {};
    violations.forEach(v => {
        areaStats[v.area_name] = (areaStats[v.area_name] || 0) + 1;
    });
    
    let html = '<div class="chart-bar">';
    Object.entries(areaStats).forEach(([area, count]) => {
        const percentage = (count / violations.length * 100).toFixed(1);
        html += `
            <div class="chart-bar-item">
                <div class="chart-bar-label">${area}</div>
                <div class="chart-bar-visual">
                    <div class="chart-bar-fill" style="width: ${percentage}%"></div>
                </div>
                <div class="chart-bar-value">${count} (${percentage}%)</div>
            </div>
        `;
    });
    html += '</div>';
    container.innerHTML = html;
}

/**
 * Display type chart
 */
function displayTypeChart() {
    const container = document.getElementById('typeChart');
    if (!container) return;
    
    const typeStats = {};
    violations.forEach(v => {
        typeStats[v.type_name] = (typeStats[v.type_name] || 0) + 1;
    });
    
    let html = '<div class="chart-bar">';
    Object.entries(typeStats).forEach(([type, count]) => {
        const percentage = (count / violations.length * 100).toFixed(1);
        html += `
            <div class="chart-bar-item">
                <div class="chart-bar-label">${type}</div>
                <div class="chart-bar-visual">
                    <div class="chart-bar-fill" style="width: ${percentage}%"></div>
                </div>
                <div class="chart-bar-value">${count} (${percentage}%)</div>
            </div>
        `;
    });
    html += '</div>';
    container.innerHTML = html;
}

// ============================================
// UTILITY FUNCTIONS
// ============================================

/**
 * Get element value by ID
 */
function getValue(elementId) {
    const element = document.getElementById(elementId);
    return element ? element.value : '';
}

/**
 * Update element text content
 */
function updateElement(elementId, content) {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = content;
    }
}

/**
 * Format currency
 */
function formatCurrency(amount) {
    return '₹' + parseFloat(amount).toLocaleString('en-IN', {
        minimumFractionDigits: 0,
        maximumFractionDigits: 2
    });
}

/**
 * Format date time
 */
function formatDateTime(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleString('en-IN', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

/**
 * Capitalize first letter
 */
function capitalizeFirst(string) {
    if (!string) return '';
    return string.charAt(0).toUpperCase() + string.slice(1);
}

/**
 * Create status badge HTML
 */
function createStatusBadgeHTML(status) {
    return `<span class="badge status-${status}">${status.toUpperCase()}</span>`;
}

/**
 * Create status badge element
 */
function createStatusBadge(status) {
    const badge = document.createElement('span');
    badge.className = `badge status-${status}`;
    badge.textContent = status.toUpperCase();
    return badge.outerHTML;
}

/**
 * Create table row
 */
function createTableRow(cells) {
    const row = document.createElement('tr');
    cells.forEach(cell => {
        const td = document.createElement('td');
        if (typeof cell === 'string') {
            td.innerHTML = cell;
        } else {
            td.textContent = cell;
        }
        row.appendChild(td);
    });
    return row;
}

/**
 * Show alert message
 */
function showAlert(message, type = 'info', containerId = null) {
    const alertDiv = containerId ? 
        document.getElementById(containerId) : 
        createAlertContainer();
    
    if (!alertDiv) return;
    
    alertDiv.innerHTML = `<div class="alert alert-${type}">${message}</div>`;
    alertDiv.style.display = 'block';
    
    setTimeout(() => {
        alertDiv.style.display = 'none';
        alertDiv.innerHTML = '';
    }, 5000);
}

/**
 * Create alert container
 */
function createAlertContainer() {
    let container = document.getElementById('globalAlertContainer');
    if (!container) {
        container = document.createElement('div');
        container.id = 'globalAlertContainer';
        container.style.position = 'fixed';
        container.style.top = '20px';
        container.style.right = '20px';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
    }
    return container;
}

/**
 * Get violation type name by ID
 */
function getViolationTypeName(typeId) {
    const type = violationTypes.find(t => t.type_id == typeId);
    return type ? type.type_name : 'Unknown';
}

/**
 * Get area name by ID
 */
function getAreaName(areaId) {
    const area = areas.find(a => a.area_id == areaId);
    return area ? `${area.area_name}, ${area.city}` : 'Unknown';
}

// ============================================
// EXPORT FUNCTIONS (Make available globally)
// ============================================

window.switchTab = switchTab;
window.logout = logout;
window.registerViolation = registerViolation;
window.searchViolations = searchViolations;
window.markAsPaid = markAsPaid;