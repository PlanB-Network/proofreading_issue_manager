/**
 * Forms Module - Handles form validation and submission
 * @module forms
 */

export class FormValidator {
    /**
     * Create a form validator
     * @param {string} formId - The form element ID
     */
    constructor(formId) {
        this.form = document.getElementById(formId);
        this.errors = new Map();
    }

    /**
     * Validate the form
     * @returns {boolean} Whether the form is valid
     */
    validate() {
        if (!this.form) return false;
        
        this.errors.clear();
        const inputs = this.form.querySelectorAll('input[required], select[required]');
        let isValid = true;
        
        inputs.forEach(input => {
            const value = input.value.trim();
            const name = input.name || input.id;
            
            // Required field validation
            if (!value) {
                this.addError(name, 'This field is required');
                this.markFieldError(input);
                isValid = false;
            } else {
                this.clearFieldError(input);
                
                // Additional validations based on input type
                if (input.type === 'email' && !this.validateEmail(value)) {
                    this.addError(name, 'Please enter a valid email');
                    this.markFieldError(input);
                    isValid = false;
                }
            }
        });
        
        return isValid;
    }

    /**
     * Validate email format
     * @param {string} email - Email to validate
     * @returns {boolean} Whether email is valid
     */
    validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }

    /**
     * Add error for a field
     * @param {string} field - Field name
     * @param {string} message - Error message
     */
    addError(field, message) {
        this.errors.set(field, message);
    }

    /**
     * Get errors
     * @returns {Map} Field errors
     */
    getErrors() {
        return this.errors;
    }

    /**
     * Mark field as having error
     * @param {HTMLElement} input - Input element
     */
    markFieldError(input) {
        input.classList.add('error');
        input.classList.remove('success');
        
        // Show error message if container exists
        const errorEl = input.parentElement.querySelector('.error-message');
        if (errorEl) {
            errorEl.textContent = this.errors.get(input.name || input.id) || '';
            errorEl.style.display = 'block';
        }
    }

    /**
     * Clear field error
     * @param {HTMLElement} input - Input element
     */
    clearFieldError(input) {
        input.classList.remove('error');
        
        const errorEl = input.parentElement.querySelector('.error-message');
        if (errorEl) {
            errorEl.style.display = 'none';
        }
    }

    /**
     * Get form data as object
     * @returns {Object} Form data
     */
    getFormData() {
        const formData = new FormData(this.form);
        const data = {};
        
        for (const [key, value] of formData.entries()) {
            data[key] = value;
        }
        
        return data;
    }

    /**
     * Show loading state
     * @param {HTMLElement} submitBtn - Submit button
     */
    showLoading(submitBtn) {
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.dataset.originalText = submitBtn.textContent;
            submitBtn.textContent = 'Loading...';
            submitBtn.classList.add('loading');
        }
    }

    /**
     * Hide loading state
     * @param {HTMLElement} submitBtn - Submit button
     */
    hideLoading(submitBtn) {
        if (submitBtn && submitBtn.dataset.originalText) {
            submitBtn.disabled = false;
            submitBtn.textContent = submitBtn.dataset.originalText;
            submitBtn.classList.remove('loading');
        }
    }

    /**
     * Reset form
     */
    reset() {
        this.form.reset();
        this.errors.clear();
        
        // Clear all error states
        const inputs = this.form.querySelectorAll('.error');
        inputs.forEach(input => this.clearFieldError(input));
    }
}

/**
 * Form utilities
 */
export class FormUtils {
    /**
     * Serialize form data to JSON
     * @param {HTMLFormElement} form - Form element
     * @returns {Object} Form data as object
     */
    static serializeForm(form) {
        const formData = new FormData(form);
        const data = {};
        
        for (const [key, value] of formData.entries()) {
            // Handle multiple values (like checkboxes)
            if (data[key]) {
                if (Array.isArray(data[key])) {
                    data[key].push(value);
                } else {
                    data[key] = [data[key], value];
                }
            } else {
                data[key] = value;
            }
        }
        
        return data;
    }

    /**
     * Fill form with data
     * @param {HTMLFormElement} form - Form element
     * @param {Object} data - Data to fill
     */
    static fillForm(form, data) {
        Object.keys(data).forEach(key => {
            const input = form.elements[key];
            if (input) {
                if (input.type === 'checkbox' || input.type === 'radio') {
                    input.checked = data[key] === input.value;
                } else {
                    input.value = data[key];
                }
            }
        });
    }

    /**
     * Clear form errors
     * @param {HTMLFormElement} form - Form element
     */
    static clearErrors(form) {
        const errorElements = form.querySelectorAll('.error');
        errorElements.forEach(el => {
            el.classList.remove('error');
        });
        
        const errorMessages = form.querySelectorAll('.error-message');
        errorMessages.forEach(el => {
            el.style.display = 'none';
        });
    }
}