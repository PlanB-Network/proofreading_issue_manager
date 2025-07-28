/**
 * Course Form Page
 * @module pages/course-form
 */

import { API } from '../modules/api.js';
import { FormValidator } from '../modules/forms.js';
import { AutocompleteField } from '../modules/autocomplete.js';
import { previewModal } from '../modules/modals.js';
import { showNotification } from '../modules/utils.js';

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const courseForm = new CourseForm();
    courseForm.init();
});

class CourseForm {
    constructor() {
        this.form = document.getElementById('course-form');
        this.validator = new FormValidator('course-form');
        this.autocompleteFields = {};
    }

    async init() {
        if (!this.form) return;

        // Initialize autocomplete fields
        this.initAutocomplete();

        // Bind form events
        this.bindEvents();

        // Load initial data
        await this.loadCourses();
    }

    initAutocomplete() {
        // Course ID autocomplete
        const courseInput = document.getElementById('course_id');
        if (courseInput) {
            this.autocompleteFields.course = new AutocompleteField(
                courseInput,
                async (query) => {
                    const data = await API.getCourses();
                    return data.courses.filter(course => 
                        course.toLowerCase().includes(query.toLowerCase())
                    );
                },
                {
                    minChars: 0,
                    onSelect: (course) => this.loadCourseInfo(course)
                }
            );
        }

        // Language autocomplete
        const languageInput = document.getElementById('language');
        if (languageInput) {
            this.autocompleteFields.language = new AutocompleteField(
                languageInput,
                async (query) => {
                    const data = await API.searchLanguages(query);
                    return data.languages;
                },
                {
                    minChars: 1,
                    displayProperty: 'display',
                    valueProperty: 'code',
                    onSelect: (language) => {
                        // Update hidden language code field
                        const codeInput = document.getElementById('language-code');
                        if (codeInput) {
                            codeInput.value = language.code;
                        }
                        // Update branch suggestions
                        this.updateBranchSuggestions(language.code);
                    }
                }
            );
        }

        // Branch autocomplete
        const branchInput = document.getElementById('branch');
        if (branchInput) {
            this.autocompleteFields.branch = new AutocompleteField(
                branchInput,
                async (query) => {
                    const languageCode = document.getElementById('language-code')?.value || '';
                    const data = await API.searchBranches(query, languageCode);
                    return data.branches;
                },
                {
                    minChars: 0,
                    delay: 200
                }
            );
        }
    }

    bindEvents() {
        // Preview button
        const previewBtn = document.getElementById('preview-btn');
        if (previewBtn) {
            previewBtn.addEventListener('click', () => this.previewIssue());
        }

        // Form submit
        this.form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.createIssue();
        });

        // Course ID change
        const courseInput = document.getElementById('course_id');
        if (courseInput) {
            courseInput.addEventListener('change', () => {
                this.loadCourseInfo(courseInput.value);
            });
        }
    }

    async loadCourses() {
        try {
            const datalist = document.getElementById('course-list');
            if (!datalist) return;

            const data = await API.getCourses();
            datalist.innerHTML = data.courses
                .map(course => `<option value="${course}">`)
                .join('');
        } catch (error) {
            console.error('Failed to load courses:', error);
        }
    }

    async loadCourseInfo(courseId) {
        if (!courseId) return;

        const infoDiv = document.getElementById('course-info');
        if (!infoDiv) return;

        try {
            infoDiv.style.display = 'block';
            infoDiv.innerHTML = '<p>Loading course info...</p>';

            const info = await API.getCourseInfo(courseId);
            infoDiv.innerHTML = `
                <div class="course-details">
                    <p><strong>Title:</strong> ${info.title}</p>
                    <p><strong>UUID:</strong> ${info.uuid}</p>
                </div>
            `;
        } catch (error) {
            infoDiv.innerHTML = '<p class="error">Failed to load course info</p>';
        }
    }

    async updateBranchSuggestions(languageCode) {
        // Trigger branch autocomplete refresh with new language context
        const branchInput = document.getElementById('branch');
        if (branchInput && this.autocompleteFields.branch) {
            branchInput.dispatchEvent(new Event('input'));
        }
    }

    async previewIssue() {
        if (!this.validator.validate()) {
            showNotification('Please fill in all required fields', 'error');
            return;
        }

        const formData = this.validator.getFormData();
        
        // Use language code if available
        const languageCode = document.getElementById('language-code')?.value;
        if (languageCode) {
            formData.language = languageCode;
        }

        try {
            const submitBtn = document.getElementById('preview-btn');
            this.validator.showLoading(submitBtn);

            const preview = await API.previewCourseIssue(formData);
            
            previewModal(preview, () => this.createIssue());
        } catch (error) {
            showNotification(`Preview failed: ${error.message}`, 'error');
        } finally {
            const submitBtn = document.getElementById('preview-btn');
            this.validator.hideLoading(submitBtn);
        }
    }

    async createIssue() {
        if (!this.validator.validate()) {
            showNotification('Please fill in all required fields', 'error');
            return;
        }

        const formData = this.validator.getFormData();
        
        // Use language code if available
        const languageCode = document.getElementById('language-code')?.value;
        if (languageCode) {
            formData.language = languageCode;
        }

        try {
            const submitBtn = this.form.querySelector('button[type="submit"]');
            this.validator.showLoading(submitBtn);

            const result = await API.createCourseIssue(formData);
            
            if (result.success) {
                showNotification('Issue created successfully!', 'success');
                
                // Redirect to success page
                setTimeout(() => {
                    window.location.href = `/success?url=${encodeURIComponent(result.issue_url)}&number=${result.issue_number}`;
                }, 1000);
            }
        } catch (error) {
            showNotification(`Failed to create issue: ${error.message}`, 'error');
        } finally {
            const submitBtn = this.form.querySelector('button[type="submit"]');
            this.validator.hideLoading(submitBtn);
        }
    }
}