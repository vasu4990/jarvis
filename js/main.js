// ================================
// JARVIS Builder's Handbook
// Main JavaScript
// ================================

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all features
    initThemeToggle();
    initProgressTracker();
    initLayerAccordions();
    initSmoothScroll();
    initTooltips();
    loadUserPreferences();
});

// ================================
// Theme Toggle
// ================================

function initThemeToggle() {
    const themeToggle = document.getElementById('themeToggle');
    if (!themeToggle) return;

    // Load saved theme
    const savedTheme = localStorage.getItem('jarvis-theme') || 'dark';
    document.body.classList.toggle('light-theme', savedTheme === 'light');
    updateThemeIcon(savedTheme);

    themeToggle.addEventListener('click', function() {
        const isLight = document.body.classList.toggle('light-theme');
        const newTheme = isLight ? 'light' : 'dark';
        localStorage.setItem('jarvis-theme', newTheme);
        updateThemeIcon(newTheme);
    });
}

function updateThemeIcon(theme) {
    const themeToggle = document.getElementById('themeToggle');
    if (!themeToggle) return;

    const icon = themeToggle.querySelector('i');
    if (theme === 'light') {
        icon.classList.remove('fa-moon');
        icon.classList.add('fa-sun');
    } else {
        icon.classList.remove('fa-sun');
        icon.classList.add('fa-moon');
    }
}

// ================================
// Progress Tracker
// ================================

function initProgressTracker() {
    updateProgress();
    
    // Update progress every 5 seconds
    setInterval(updateProgress, 5000);
}

function updateProgress() {
    const progressFill = document.getElementById('progressFill');
    const progressPercent = document.getElementById('progressPercent');
    
    if (!progressFill || !progressPercent) return;

    const milestones = getMilestones();
    const completed = milestones.filter(m => m.completed).length;
    const total = milestones.length;
    const percent = Math.round((completed / total) * 100);

    progressFill.style.width = `${percent}%`;
    progressPercent.textContent = `${percent}%`;
}

function getMilestones() {
    const stored = localStorage.getItem('jarvis-milestones');
    if (stored) {
        return JSON.parse(stored);
    }

    // Default milestones
    return [
        { id: 'python-setup', name: 'Python Environment Setup', completed: false },
        { id: 'dependencies', name: 'Install Dependencies', completed: false },
        { id: 'models-download', name: 'Download ML Models', completed: false },
        { id: 'config', name: 'Configure System', completed: false },
        { id: 'esp32-build', name: 'Build ESP32 Hardware', completed: false },
        { id: 'esp32-firmware', name: 'Flash ESP32 Firmware', completed: false },
        { id: 'first-run', name: 'First Successful Run', completed: false },
        { id: 'voice-test', name: 'Voice Command Test', completed: false },
        { id: 'tool-test', name: 'Tool Execution Test', completed: false },
        { id: 'memory-test', name: 'Memory System Test', completed: false }
    ];
}

function saveMilestones(milestones) {
    localStorage.setItem('jarvis-milestones', JSON.stringify(milestones));
    updateProgress();
}

function toggleMilestone(milestoneId) {
    const milestones = getMilestones();
    const milestone = milestones.find(m => m.id === milestoneId);
    if (milestone) {
        milestone.completed = !milestone.completed;
        saveMilestones(milestones);
    }
}

// Expose for roadmap page
window.jarvisProgress = {
    getMilestones,
    saveMilestones,
    toggleMilestone,
    updateProgress
};

// ================================
// Layer Accordions (Architecture Page)
// ================================

function initLayerAccordions() {
    const layerCards = document.querySelectorAll('.layer-card');
    
    layerCards.forEach((card, index) => {
        const header = card.querySelector('.layer-header');
        
        // Open first layer by default
        if (index === 0) {
            card.classList.add('active');
        }
        
        header.addEventListener('click', function() {
            const isActive = card.classList.contains('active');
            
            // Close all layers
            layerCards.forEach(c => c.classList.remove('active'));
            
            // Open clicked layer if it wasn't active
            if (!isActive) {
                card.classList.add('active');
            }
        });
    });
}

// ================================
// Smooth Scroll
// ================================

function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// ================================
// Tooltips
// ================================

function initTooltips() {
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    
    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', function() {
            showTooltip(this, this.getAttribute('data-tooltip'));
        });
        
        element.addEventListener('mouseleave', function() {
            hideTooltip();
        });
    });
}

function showTooltip(element, text) {
    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip';
    tooltip.textContent = text;
    tooltip.id = 'active-tooltip';
    
    document.body.appendChild(tooltip);
    
    const rect = element.getBoundingClientRect();
    tooltip.style.position = 'absolute';
    tooltip.style.left = `${rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2)}px`;
    tooltip.style.top = `${rect.top - tooltip.offsetHeight - 10}px`;
    tooltip.style.opacity = '1';
}

function hideTooltip() {
    const tooltip = document.getElementById('active-tooltip');
    if (tooltip) {
        tooltip.remove();
    }
}

// ================================
// Load User Preferences
// ================================

function loadUserPreferences() {
    // Load code syntax highlight theme
    const codeTheme = localStorage.getItem('jarvis-code-theme') || 'monokai';
    document.documentElement.setAttribute('data-code-theme', codeTheme);
}

// ================================
// Copy to Clipboard
// ================================

function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            showNotification('Copied to clipboard!', 'success');
        }).catch(() => {
            fallbackCopy(text);
        });
    } else {
        fallbackCopy(text);
    }
}

function fallbackCopy(text) {
    const textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.style.position = 'fixed';
    textarea.style.opacity = '0';
    document.body.appendChild(textarea);
    textarea.select();
    
    try {
        document.execCommand('copy');
        showNotification('Copied to clipboard!', 'success');
    } catch (err) {
        showNotification('Failed to copy', 'error');
    }
    
    document.body.removeChild(textarea);
}

// ================================
// Notifications
// ================================

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Trigger animation
    setTimeout(() => {
        notification.classList.add('show');
    }, 10);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
}

// ================================
// Add Copy Buttons to Code Blocks
// ================================

function addCopyButtonsToCodeBlocks() {
    const codeBlocks = document.querySelectorAll('pre code');
    
    codeBlocks.forEach(block => {
        const pre = block.parentElement;
        const wrapper = document.createElement('div');
        wrapper.className = 'code-block-wrapper';
        
        const copyBtn = document.createElement('button');
        copyBtn.className = 'code-copy-btn';
        copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
        copyBtn.title = 'Copy code';
        
        copyBtn.addEventListener('click', function() {
            copyToClipboard(block.textContent);
            copyBtn.innerHTML = '<i class="fas fa-check"></i>';
            setTimeout(() => {
                copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
            }, 2000);
        });
        
        pre.parentNode.insertBefore(wrapper, pre);
        wrapper.appendChild(pre);
        wrapper.appendChild(copyBtn);
    });
}

// Call on DOM ready
document.addEventListener('DOMContentLoaded', addCopyButtonsToCodeBlocks);

// ================================
// Search Functionality
// ================================

function initSearch() {
    const searchInput = document.getElementById('search-input');
    if (!searchInput) return;

    searchInput.addEventListener('input', function(e) {
        const query = e.target.value.toLowerCase();
        performSearch(query);
    });
}

function performSearch(query) {
    // Basic search implementation
    // In production, use a proper search library like Fuse.js
    const searchableElements = document.querySelectorAll('[data-searchable]');
    
    searchableElements.forEach(element => {
        const text = element.textContent.toLowerCase();
        const matches = text.includes(query);
        
        element.style.display = matches || query === '' ? '' : 'none';
    });
}

// ================================
// Analytics (Privacy-Friendly)
// ================================

function trackPageView() {
    // Only track page names, no personal data
    const page = window.location.pathname.split('/').pop() || 'index.html';
    const visits = JSON.parse(localStorage.getItem('jarvis-page-visits') || '{}');
    visits[page] = (visits[page] || 0) + 1;
    localStorage.setItem('jarvis-page-visits', JSON.stringify(visits));
}

document.addEventListener('DOMContentLoaded', trackPageView);

// ================================
// Mobile Navigation
// ================================

function initMobileNav() {
    const menuToggle = document.getElementById('mobile-menu-toggle');
    const navLinks = document.querySelector('.nav-links');
    
    if (!menuToggle || !navLinks) return;

    menuToggle.addEventListener('click', function() {
        navLinks.classList.toggle('mobile-open');
        this.classList.toggle('active');
    });
}

document.addEventListener('DOMContentLoaded', initMobileNav);

// ================================
// Export Utilities
// ================================

window.jarvisUtils = {
    copyToClipboard,
    showNotification,
    toggleMilestone
};