/**
 * Utilities Module - Common utility functions
 * @module utils
 */

/**
 * Debounce function execution
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @returns {Function} Debounced function
 */
export function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Throttle function execution
 * @param {Function} func - Function to throttle
 * @param {number} limit - Time limit in milliseconds
 * @returns {Function} Throttled function
 */
export function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/**
 * Copy text to clipboard
 * @param {string} text - Text to copy
 * @param {string} buttonId - Button ID for feedback
 * @returns {Promise<boolean>} Success status
 */
export async function copyToClipboard(text, buttonId) {
    const button = buttonId ? document.getElementById(buttonId) : null;
    const originalText = button ? button.textContent : '';
    
    try {
        if (navigator.clipboard && window.isSecureContext) {
            // Modern async clipboard API
            await navigator.clipboard.writeText(text);
            showCopySuccess(button, originalText);
            return true;
        } else {
            // Fallback
            return fallbackCopyTextToClipboard(text, button, originalText);
        }
    } catch (err) {
        console.error('Failed to copy:', err);
        if (button) {
            return fallbackCopyTextToClipboard(text, button, originalText);
        }
        return false;
    }
}

/**
 * Fallback copy method
 * @param {string} text - Text to copy
 * @param {HTMLElement} button - Button element
 * @param {string} originalText - Original button text
 * @returns {boolean} Success status
 */
function fallbackCopyTextToClipboard(text, button, originalText) {
    const textArea = document.createElement("textarea");
    textArea.value = text;
    textArea.style.position = "fixed";
    textArea.style.left = "-999999px";
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        const successful = document.execCommand('copy');
        if (successful) {
            showCopySuccess(button, originalText);
        }
        return successful;
    } catch (err) {
        console.error('Fallback: Failed to copy', err);
        return false;
    } finally {
        document.body.removeChild(textArea);
    }
}

/**
 * Show copy success feedback
 * @param {HTMLElement} button - Button element
 * @param {string} originalText - Original button text
 */
function showCopySuccess(button, originalText) {
    if (!button) return;
    
    button.textContent = '✅ Copied!';
    button.classList.add('success');
    
    setTimeout(() => {
        button.textContent = originalText;
        button.classList.remove('success');
    }, 2000);
}

/**
 * Format date to readable string
 * @param {Date|string} date - Date to format
 * @returns {string} Formatted date
 */
export function formatDate(date) {
    const d = new Date(date);
    return d.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

/**
 * Format relative time
 * @param {Date|string} date - Date to format
 * @returns {string} Relative time string
 */
export function formatRelativeTime(date) {
    const d = new Date(date);
    const now = new Date();
    const diff = now - d;
    
    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);
    
    if (days > 0) return `${days} day${days === 1 ? '' : 's'} ago`;
    if (hours > 0) return `${hours} hour${hours === 1 ? '' : 's'} ago`;
    if (minutes > 0) return `${minutes} minute${minutes === 1 ? '' : 's'} ago`;
    return 'just now';
}

/**
 * Parse query string
 * @param {string} queryString - Query string to parse
 * @returns {Object} Parsed query parameters
 */
export function parseQueryString(queryString) {
    const params = {};
    const searchParams = new URLSearchParams(queryString);
    
    for (const [key, value] of searchParams) {
        params[key] = value;
    }
    
    return params;
}

/**
 * Build query string from object
 * @param {Object} params - Parameters object
 * @returns {string} Query string
 */
export function buildQueryString(params) {
    const searchParams = new URLSearchParams();
    
    Object.keys(params).forEach(key => {
        if (params[key] !== null && params[key] !== undefined) {
            searchParams.append(key, params[key]);
        }
    });
    
    return searchParams.toString();
}

/**
 * Show notification
 * @param {string} message - Notification message
 * @param {string} type - Notification type (success, error, warning, info)
 * @param {number} duration - Duration in milliseconds
 */
export function showNotification(message, type = 'info', duration = 3000) {
    // Remove existing notifications
    const existing = document.querySelector('.notification');
    if (existing) {
        existing.remove();
    }
    
    // Create notification
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => notification.classList.add('show'), 10);
    
    // Auto remove
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, duration);
}

/**
 * Load script dynamically
 * @param {string} src - Script source URL
 * @returns {Promise} Load promise
 */
export function loadScript(src) {
    return new Promise((resolve, reject) => {
        const script = document.createElement('script');
        script.src = src;
        script.onload = resolve;
        script.onerror = reject;
        document.head.appendChild(script);
    });
}

/**
 * Load CSS dynamically
 * @param {string} href - CSS file URL
 * @returns {Promise} Load promise
 */
export function loadCSS(href) {
    return new Promise((resolve, reject) => {
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = href;
        link.onload = resolve;
        link.onerror = reject;
        document.head.appendChild(link);
    });
}

/**
 * Escape HTML
 * @param {string} text - Text to escape
 * @returns {string} Escaped text
 */
export function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Generate unique ID
 * @param {string} prefix - ID prefix
 * @returns {string} Unique ID
 */
export function generateId(prefix = 'id') {
    return `${prefix}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}