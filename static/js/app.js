/**
 * SIMAN - PT Lentera Anugerah Dimensi
 * Water Blue Theme Application with Soft Blue Borders & Glowing Red Accent
 */

// API Base URL
const API_BASE_URL = '/api';

// Theme Configuration - Water Blue with Red Glowing Accent
const THEME = {
    waterBlue1: '#4dabf7',
    waterBlue2: '#339af0',
    waterBlue3: '#228be6',
    waterBlue4: '#1c7ed6',
    waterBlue5: '#1b6ec2',
    redGlowing: '#ff1133',
    redGlowingLight: '#ff3355',
    redGlowingDark: '#cc0022',
    textDark: '#1b4e8f',
    softWhite: '#f0f8ff',
    textMuted: '#495057'
};

// Console Greeting
console.log("%c💧 SIMAN - PT Lentera Anugerah Dimensi 💧", `color: ${THEME.waterBlue2}; font-size: 16px; font-weight: bold;`);
console.log("%c✦ Water Blue Theme with Black Borders & Glowing Red Accent ✦", `color: ${THEME.redGlowing}; font-size: 12px;`);
console.log("%c✦ Enterprise Resource Planning System ✦", `color: ${THEME.textMuted}; font-size: 10px;`);

// ==================== UTILITY FUNCTIONS ====================

// Get CSRF Token
function getCookie(name) {
    if (!document || !document.cookie) return null;
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}

// Format Currency (IDR)
function formatCurrency(amount) {
    return new Intl.NumberFormat('id-ID', {
        style: 'currency',
        currency: 'IDR',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount);
}

// Format Number
function formatNumber(number) {
    return new Intl.NumberFormat('id-ID').format(number);
}

// Format Date
function formatDate(date) {
    return new Date(date).toLocaleDateString('id-ID', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

// Format DateTime
function formatDateTime(date) {
    return new Date(date).toLocaleDateString('id-ID', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Format Time
function formatTime(date) {
    return new Date(date).toLocaleTimeString('id-ID', {
        hour: '2-digit',
        minute: '2-digit'
    });
}

// ==================== TOAST NOTIFICATIONS ====================

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    let icon = 'info-circle';
    let gradient = `linear-gradient(135deg, ${THEME.waterBlue1}, ${THEME.waterBlue4})`;
    
    switch(type) {
        case 'error':
            icon = 'times-circle';
            gradient = `linear-gradient(135deg, ${THEME.redGlowing}, ${THEME.redGlowingDark})`;
            break;
        case 'success':
            icon = 'check-circle';
            gradient = `linear-gradient(135deg, #28a745, #20c997)`;
            break;
        case 'warning':
            icon = 'exclamation-triangle';
            gradient = `linear-gradient(135deg, #ffc107, #ff9800)`;
            break;
        default:
            icon = 'info-circle';
    }
    
    toast.className = 'toast show align-items-center';
    toast.setAttribute('role', 'alert');
    toast.style.background = 'white';
    toast.style.border = `2px solid ${THEME.textDark}`;
    toast.style.borderLeft = `6px solid ${type === 'error' ? THEME.redGlowing : THEME.waterBlue2}`;
    toast.style.borderRadius = '16px';
    toast.style.marginBottom = '10px';
    toast.style.boxShadow = THEME.shadowMd || '0 4px 20px rgba(0, 0, 0, 0.1)';
    toast.innerHTML = `
        <div class="toast-body d-flex align-items-center">
            <i class="fas fa-${icon}" style="color: ${type === 'error' ? THEME.redGlowing : THEME.waterBlue2}; margin-right: 12px; font-size: 1.2rem;"></i>
            <div class="flex-grow-1">${message}</div>
            <button type="button" class="btn-close ms-3" data-bs-dismiss="toast"></button>
        </div>
    `;

    let container = document.querySelector('.toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
    }

    container.appendChild(toast);
    
    // Auto dismiss after 4 seconds
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// ==================== API REQUESTS ====================

async function apiRequest(endpoint, method = 'GET', data = null) {
    const url = API_BASE_URL + endpoint;
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json'
        },
        credentials: 'include'
    };
    
    if (data) {
        options.body = JSON.stringify(data);
    }

    // Add CSRF token for non-GET requests
    if (method !== 'GET') {
        const csrftoken = getCookie('csrftoken');
        if (csrftoken) options.headers['X-CSRFToken'] = csrftoken;
    }

    try {
        const response = await fetch(url, options);
        
        if (response.status === 401) {
            showToast('Sesi Anda telah berakhir, silakan login kembali!', 'error');
            setTimeout(() => {
                window.location.href = '/login/';
            }, 1500);
            return null;
        }

        const data_response = await response.json();
        
        if (!response.ok && data_response.error) {
            showToast(data_response.error, 'error');
        }
        
        return data_response;
    } catch (error) {
        console.error('API Error:', error);
        showToast('Terjadi kesalahan koneksi! Periksa jaringan Anda.', 'error');
        return null;
    }
}

// ==================== AUTHENTICATION ====================

async function login(email, password, remember = false) {
    const response = await fetch(API_BASE_URL + '/auth/login/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ email, password, remember })
    });

    if (response.ok) {
        showToast('Login berhasil! Selamat datang kembali.', 'success');
        return true;
    } else {
        const data = await response.json();
        showToast(data.detail || 'Login gagal! Periksa email dan password Anda.', 'error');
        return false;
    }
}

async function logout() {
    showToast('Sedang logout...', 'info');
    await fetch(API_BASE_URL + '/auth/logout/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include'
    });
    setTimeout(() => {
        window.location.href = '/login/';
    }, 500);
}

async function getCurrentUser() {
    return await apiRequest('/auth/me/');
}

// ==================== NOTIFICATIONS ====================

async function getNotifications() {
    return await apiRequest('/notifications/');
}

async function markNotificationRead(id) {
    await apiRequest(`/notifications/${id}/read/`, 'POST');
    const notificationElement = document.querySelector(`.notification-item[data-id="${id}"]`);
    if (notificationElement) {
        notificationElement.style.opacity = '0.5';
        setTimeout(() => notificationElement.remove(), 300);
    }
}

async function loadNotificationCount() {
    const countElement = document.getElementById('notification-count');
    if (!countElement) return;

    if (!window.SIMAN_AUTH) return;

    const notifications = await getNotifications();
    if (notifications && Array.isArray(notifications)) {
        const unreadCount = notifications.filter(n => !n.is_read).length;
        countElement.textContent = unreadCount;
        countElement.style.display = unreadCount > 0 ? 'inline-block' : 'none';
        
        if (unreadCount > 0) {
            countElement.style.animation = 'redPulse 2s infinite';
        } else {
            countElement.style.animation = 'none';
        }
    }
}

// ==================== CHARTS ====================

function initChart(canvasId, type, labels, datasets) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;
    
    const themedDatasets = datasets.map((dataset, index) => {
        const colors = [THEME.waterBlue1, THEME.waterBlue2, THEME.waterBlue3, THEME.waterBlue4];
        return {
            ...dataset,
            backgroundColor: type === 'line' ? 'transparent' : colors[index % colors.length] + '20',
            borderColor: colors[index % colors.length],
            pointBackgroundColor: THEME.waterBlue2,
            pointBorderColor: THEME.waterBlue4,
            borderWidth: 2,
            tension: 0.4
        };
    });

    return new Chart(ctx, {
        type: type,
        data: {
            labels: labels,
            datasets: themedDatasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: THEME.textDark,
                        font: { size: 12, family: 'Poppins' }
                    }
                },
                tooltip: {
                    backgroundColor: THEME.softWhite,
                    titleColor: THEME.redGlowing,
                    bodyColor: THEME.textDark,
                    borderColor: THEME.textDark,
                    borderWidth: 1,
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            let value = context.raw;
                            if (typeof value === 'number') {
                                return `${label}: ${formatNumber(value)}`;
                            }
                            return `${label}: ${value}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    grid: { color: THEME.textDark + '20' },
                    ticks: { color: THEME.textMuted },
                    beginAtZero: true
                },
                x: {
                    grid: { display: false },
                    ticks: { color: THEME.textMuted }
                }
            },
            elements: {
                line: {
                    tension: 0.4
                }
            }
        }
    });
}

// ==================== UI HELPERS ====================

function showLoading(containerId) {
    const container = document.getElementById(containerId);
    if (container) {
        const loadingHtml = `
            <div class="loading-overlay">
                <div class="loading-spinner"></div>
            </div>
        `;
        container.insertAdjacentHTML('beforeend', loadingHtml);
    }
}

function hideLoading(containerId) {
    const container = document.getElementById(containerId);
    if (container) {
        const overlay = container.querySelector('.loading-overlay');
        if (overlay) overlay.remove();
    }
}

function addRippleEffect(button) {
    button.addEventListener('click', function(e) {
        const ripple = document.createElement('span');
        ripple.classList.add('ripple');
        const rect = this.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        ripple.style.width = ripple.style.height = `${size}px`;
        ripple.style.left = `${e.clientX - rect.left - size/2}px`;
        ripple.style.top = `${e.clientY - rect.top - size/2}px`;
        this.style.position = 'relative';
        this.style.overflow = 'hidden';
        this.appendChild(ripple);
        setTimeout(() => ripple.remove(), 600);
    });
}

// ==================== INITIALIZATION ====================

document.addEventListener('DOMContentLoaded', function() {
    // Initialize AOS animations
    if (typeof AOS !== 'undefined') {
        AOS.refresh();
    }
    
    // Load notifications
    loadNotificationCount();
    
    // Add ripple effect to all buttons
    document.querySelectorAll('.btn').forEach(btn => {
        addRippleEffect(btn);
    });
    
    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href !== '#') {
                e.preventDefault();
                document.querySelector(href)?.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Form submit loading state
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn && this.checkValidity() !== false) {
                const originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Memproses...';
                submitBtn.disabled = true;
                
                // Reset button after form submission (will be overridden by actual response)
                setTimeout(() => {
                    submitBtn.innerHTML = originalText;
                    submitBtn.disabled = false;
                }, 5000);
            }
        });
    });
    
    // Auto-hide alerts after 5 seconds
    document.querySelectorAll('.alert').forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.5s';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });
    
    // Add red glowing effect to list items on hover
    document.querySelectorAll('.list-group-item, .table tbody tr').forEach(item => {
        item.addEventListener('mouseenter', function() {
            this.style.transition = 'all 0.3s ease';
        });
    });
});

// ==================== EXPORTS ====================

window.SIMAN = {
    apiRequest,
    login,
    logout,
    showToast,
    formatCurrency,
    formatNumber,
    formatDate,
    formatDateTime,
    formatTime,
    getCurrentUser,
    getNotifications,
    markNotificationRead,
    loadNotificationCount,
    initChart,
    showLoading,
    hideLoading,
    THEME
};

// Export theme for global use
window.SIMAN_THEME = THEME;