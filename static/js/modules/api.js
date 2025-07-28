/**
 * API Module - Handles all API communication
 * @module api
 */

export class API {
    /**
     * Make an API call
     * @param {string} url - The API endpoint
     * @param {Object} options - Fetch options
     * @returns {Promise<Object>} API response data
     */
    static async call(url, options = {}) {
        try {
            const response = await fetch(url, options);
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.message || error.error || 'API call failed');
            }
            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    /**
     * GET request
     * @param {string} url - The API endpoint
     * @returns {Promise<Object>} API response data
     */
    static async get(url) {
        return this.call(url);
    }

    /**
     * POST request
     * @param {string} url - The API endpoint
     * @param {Object} data - Data to send
     * @returns {Promise<Object>} API response data
     */
    static async post(url, data) {
        return this.call(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
    }

    // Course APIs
    static async getCourses() {
        return this.get('/api/courses');
    }

    static async getCourseInfo(courseId) {
        return this.get(`/api/course/${courseId}`);
    }

    static async previewCourseIssue(data) {
        return this.post('/course/preview', data);
    }

    static async createCourseIssue(data) {
        return this.post('/course/create', data);
    }

    // Tutorial APIs
    static async getTutorials() {
        return this.get('/api/tutorials');
    }

    static async searchTutorials(query) {
        return this.get(`/api/tutorials/search?q=${encodeURIComponent(query)}`);
    }

    static async getTutorialInfo(category, name) {
        return this.get(`/api/tutorial/${category}/${name}`);
    }

    static async previewTutorialIssue(data) {
        return this.post('/tutorial/preview', data);
    }

    static async createTutorialIssue(data) {
        return this.post('/tutorial/create', data);
    }

    // Tutorial Section APIs
    static async getTutorialSections() {
        return this.get('/api/tutorial-sections');
    }

    static async previewTutorialSectionIssue(data) {
        return this.post('/tutorial-section/preview', data);
    }

    static async createTutorialSectionIssue(data) {
        return this.post('/tutorial-section/create', data);
    }

    // Branch APIs
    static async searchBranches(query, language = '') {
        let url = `/api/branches/search?q=${encodeURIComponent(query)}`;
        if (language) {
            url += `&lang=${encodeURIComponent(language)}`;
        }
        return this.get(url);
    }

    static async validateBranch(branchName) {
        return this.get(`/api/branches/validate/${encodeURIComponent(branchName)}`);
    }

    // Language APIs
    static async searchLanguages(query) {
        return this.get(`/api/languages/search?q=${encodeURIComponent(query)}`);
    }

    static async getWeblateLanguages() {
        return this.get('/api/weblate/languages');
    }

    static async searchWeblateLanguages(query) {
        return this.get(`/api/weblate/languages/search?q=${encodeURIComponent(query)}`);
    }

    // Weblate APIs
    static async previewWeblateIssue(data) {
        return this.post('/weblate/preview', data);
    }

    static async createWeblateIssue(data) {
        return this.post('/weblate/create', data);
    }

    // Video Course APIs
    static async previewVideoCourseIssue(data) {
        return this.post('/video-course/preview', data);
    }

    static async createVideoCourseIssue(data) {
        return this.post('/video-course/create', data);
    }

    // Image Course APIs
    static async previewImageCourseIssue(data) {
        return this.post('/image-course/preview', data);
    }

    static async createImageCourseIssue(data) {
        return this.post('/image-course/create', data);
    }

    // Config API
    static async saveConfig(data) {
        return this.post('/config', data);
    }
}