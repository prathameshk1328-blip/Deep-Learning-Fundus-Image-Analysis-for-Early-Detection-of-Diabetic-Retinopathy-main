// Global variables
let uploadedFile = null;
let currentUser = null;

// Check authentication on page load
document.addEventListener('DOMContentLoaded', function() {
    checkAuth();
});

// Check if user is authenticated
async function checkAuth() {
    try {
        const response = await fetch('/check-auth');
        const data = await response.json();
        
        if (data.authenticated) {
            currentUser = data.username;
            showDashboard();
            loadHistory();
        } else {
            showAuth();
        }
    } catch (error) {
        console.error('Auth check error:', error);
        showAuth();
    }
}

// Show authentication section
function showAuth() {
    document.getElementById('authSection').classList.remove('hidden');
    document.getElementById('dashboardSection').classList.add('hidden');
    updateNavButtons(false);
}

// Show dashboard section
function showDashboard() {
    document.getElementById('authSection').classList.add('hidden');
    document.getElementById('dashboardSection').classList.remove('hidden');
    updateNavButtons(true);
}

// Update navigation buttons
function updateNavButtons(isAuthenticated) {
    const navButtons = document.getElementById('navButtons');
    
    if (isAuthenticated) {
        navButtons.innerHTML = `
            <span class="text-sm text-gray-300">Welcome, <strong>${currentUser}</strong></span>
            <button onclick="handleLogout()" class="px-4 py-2 bg-red-500/20 hover:bg-red-500/30 rounded-lg transition-all">
                Logout
            </button>
        `;
    } else {
        navButtons.innerHTML = `
            <button onclick="switchTab('login')" class="px-4 py-2 hover:bg-white/10 rounded-lg transition-all">
                Login
            </button>
        `;
    }
}

// Switch between login and register tabs
function switchTab(tab) {
    const loginTab = document.getElementById('loginTab');
    const registerTab = document.getElementById('registerTab');
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    
    if (tab === 'login') {
        loginTab.classList.add('bg-white/20');
        registerTab.classList.remove('bg-white/20');
        loginForm.classList.remove('hidden');
        registerForm.classList.add('hidden');
    } else {
        registerTab.classList.add('bg-white/20');
        loginTab.classList.remove('bg-white/20');
        registerForm.classList.remove('hidden');
        loginForm.classList.add('hidden');
    }
}

// Handle login
async function handleLogin(event) {
    event.preventDefault();
    
    const username = document.getElementById('loginUsername').value;
    const password = document.getElementById('loginPassword').value;
    
    try {
        const response = await fetch('/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password }),
        });
        
        const data = await response.json();
        
        if (response.ok) {
            currentUser = data.username;
            showNotification('Login successful!', 'success');
            showDashboard();
            loadHistory();
        } else {
            showNotification(data.error || 'Login failed', 'error');
        }
    } catch (error) {
        console.error('Login error:', error);
        showNotification('An error occurred during login', 'error');
    }
}

// Handle registration
async function handleRegister(event) {
    event.preventDefault();
    
    const username = document.getElementById('registerUsername').value;
    const email = document.getElementById('registerEmail').value;
    const password = document.getElementById('registerPassword').value;
    
    try {
        const response = await fetch('/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, email, password }),
        });
        
        const data = await response.json();
        
        if (response.ok) {
            currentUser = data.username;
            showNotification('Registration successful!', 'success');
            showDashboard();
        } else {
            showNotification(data.error || 'Registration failed', 'error');
        }
    } catch (error) {
        console.error('Registration error:', error);
        showNotification('An error occurred during registration', 'error');
    }
}

// Handle logout
async function handleLogout() {
    try {
        const response = await fetch('/logout', {
            method: 'POST',
        });
        
        if (response.ok) {
            currentUser = null;
            uploadedFile = null;
            showNotification('Logged out successfully', 'success');
            showAuth();
        }
    } catch (error) {
        console.error('Logout error:', error);
        showNotification('An error occurred during logout', 'error');
    }
}

// Handle image upload
function handleImageUpload(event) {
    const file = event.target.files[0];
    
    if (file) {
        uploadedFile = file;
        
        // Show preview
        const reader = new FileReader();
        reader.onload = function(e) {
            document.getElementById('previewImg').src = e.target.result;
            document.getElementById('imagePreview').classList.remove('hidden');
            document.getElementById('analyzeBtn').disabled = false;
        };
        reader.readAsDataURL(file);
        
        // Clear previous results
        document.getElementById('predictionResults').classList.add('hidden');
        document.getElementById('resultsContent').classList.remove('hidden');
    }
}

// Analyze image
async function analyzImage() {
    if (!uploadedFile) {
        showNotification('Please upload an image first', 'error');
        return;
    }
    
    // Show loading
    document.getElementById('resultsContent').classList.add('hidden');
    document.getElementById('loadingContent').classList.remove('hidden');
    document.getElementById('predictionResults').classList.add('hidden');
    
    const formData = new FormData();
    formData.append('image', uploadedFile);
    
    try {
        const response = await fetch('/predict', {
            method: 'POST',
            body: formData,
        });
        
        const data = await response.json();
        
        // Hide loading
        document.getElementById('loadingContent').classList.add('hidden');
        
        if (response.ok) {
            displayResults(data);
            loadHistory(); // Refresh history
        } else {
            showNotification(data.error || 'Prediction failed', 'error');
            document.getElementById('resultsContent').classList.remove('hidden');
        }
    } catch (error) {
        console.error('Prediction error:', error);
        showNotification('An error occurred during prediction', 'error');
        document.getElementById('loadingContent').classList.add('hidden');
        document.getElementById('resultsContent').classList.remove('hidden');
    }
}

// Display prediction results
function displayResults(data) {
    const resultsDiv = document.getElementById('predictionResults');
    
    // Determine severity color
    const severityColors = {
        0: 'text-green-400',
        1: 'text-yellow-400',
        2: 'text-orange-400',
        3: 'text-red-400',
        4: 'text-red-600'
    };
    
    const color = severityColors[data.severity_level] || 'text-gray-400';
    
    // Create bars for all predictions
    let barsHTML = '';
    for (const [label, confidence] of Object.entries(data.all_predictions)) {
        barsHTML += `
            <div class="mb-3">
                <div class="flex justify-between mb-1">
                    <span class="text-sm font-medium">${label}</span>
                    <span class="text-sm">${confidence.toFixed(2)}%</span>
                </div>
                <div class="w-full bg-white/10 rounded-full h-2">
                    <div class="bg-gradient-to-r from-indigo-500 to-purple-600 h-2 rounded-full transition-all duration-500" 
                         style="width: ${confidence}%"></div>
                </div>
            </div>
        `;
    }
    
    resultsDiv.innerHTML = `
        <div class="text-center mb-6">
            <div class="inline-block p-4 bg-white/10 rounded-full mb-4">
                <svg class="w-12 h-12 ${color}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
            </div>
            <h3 class="text-2xl font-bold mb-2">Diagnosis</h3>
            <p class="text-3xl font-bold ${color} mb-2">${data.prediction}</p>
            <p class="text-lg text-gray-300">Confidence: ${data.confidence.toFixed(2)}%</p>
        </div>
        
        <div class="mb-6">
            <h4 class="font-semibold mb-3">All Predictions</h4>
            ${barsHTML}
        </div>
        
        <div class="p-4 bg-blue-500/20 border border-blue-500/30 rounded-lg">
            <p class="text-sm">
                <strong>Note:</strong> This is an AI-based prediction. Please consult with a healthcare professional for proper diagnosis and treatment.
            </p>
        </div>
    `;
    
    resultsDiv.classList.remove('hidden');
}

// Load prediction history
async function loadHistory() {
    try {
        const response = await fetch('/history');
        const data = await response.json();
        
        if (response.ok && data.history && data.history.length > 0) {
            displayHistory(data.history);
        } else {
            document.getElementById('historyContent').innerHTML = `
                <p class="text-gray-400 text-center py-6">No prediction history yet</p>
            `;
        }
    } catch (error) {
        console.error('History loading error:', error);
    }
}

// Display history
function displayHistory(history) {
    const historyDiv = document.getElementById('historyContent');
    
    let historyHTML = '<div class="grid md:grid-cols-2 lg:grid-cols-3 gap-4">';
    
    history.forEach(item => {
        const date = new Date(item.date).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
        
        historyHTML += `
            <div class="bg-white/5 p-4 rounded-lg border border-white/10 hover:bg-white/10 transition-all">
                <div class="flex justify-between items-start mb-2">
                    <span class="font-semibold">${item.prediction}</span>
                    <span class="text-xs bg-indigo-500/30 px-2 py-1 rounded">${item.confidence.toFixed(1)}%</span>
                </div>
                <p class="text-xs text-gray-400">${date}</p>
            </div>
        `;
    });
    
    historyHTML += '</div>';
    historyDiv.innerHTML = historyHTML;
}

// Show notification
function showNotification(message, type = 'info') {
    const colors = {
        success: 'bg-green-500',
        error: 'bg-red-500',
        info: 'bg-blue-500'
    };
    
    const notification = document.createElement('div');
    notification.className = `fixed top-20 right-4 ${colors[type]} text-white px-6 py-3 rounded-lg shadow-lg z-50 fade-in`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Initialize login tab as active
switchTab('login');
