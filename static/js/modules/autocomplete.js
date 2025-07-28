/**
 * Autocomplete Module - Handles autocomplete functionality for input fields
 * @module autocomplete
 */

import { debounce } from './utils.js';

export class AutocompleteField {
    /**
     * Create an autocomplete field
     * @param {HTMLInputElement} input - Input element
     * @param {Function} searchFunction - Function to search for suggestions
     * @param {Object} options - Configuration options
     */
    constructor(input, searchFunction, options = {}) {
        this.input = input;
        this.searchFunction = searchFunction;
        this.options = {
            minChars: 0,
            delay: 300,
            maxResults: 10,
            onSelect: null,
            displayProperty: 'display',
            valueProperty: 'value',
            searchProperty: 'searchText',
            ...options
        };
        
        this.dropdown = null;
        this.selectedIndex = -1;
        this.results = [];
        
        this.init();
    }

    /**
     * Initialize autocomplete
     */
    init() {
        // Create dropdown
        this.createDropdown();
        
        // Bind events
        this.bindEvents();
    }

    /**
     * Create dropdown element
     */
    createDropdown() {
        this.dropdown = document.createElement('div');
        this.dropdown.className = 'autocomplete-dropdown';
        this.dropdown.style.display = 'none';
        
        // Position dropdown relative to input
        const parent = this.input.parentElement;
        parent.style.position = 'relative';
        parent.appendChild(this.dropdown);
    }

    /**
     * Bind input events
     */
    bindEvents() {
        // Debounced search
        const debouncedSearch = debounce(() => this.search(), this.options.delay);
        
        // Input events
        this.input.addEventListener('input', debouncedSearch);
        this.input.addEventListener('focus', () => {
            if (this.input.value.length >= this.options.minChars) {
                this.search();
            }
        });
        
        // Keyboard navigation
        this.input.addEventListener('keydown', (e) => this.handleKeydown(e));
        
        // Click outside to close
        document.addEventListener('click', (e) => {
            if (!this.input.contains(e.target) && !this.dropdown.contains(e.target)) {
                this.hideDropdown();
            }
        });
    }

    /**
     * Search for suggestions
     */
    async search() {
        const query = this.input.value;
        
        if (query.length < this.options.minChars) {
            this.hideDropdown();
            return;
        }
        
        try {
            this.showLoading();
            const results = await this.searchFunction(query);
            this.results = Array.isArray(results) ? results : results.data || [];
            this.renderResults();
        } catch (error) {
            console.error('Autocomplete search error:', error);
            this.hideDropdown();
        }
    }

    /**
     * Render search results
     */
    renderResults() {
        if (this.results.length === 0) {
            this.hideDropdown();
            return;
        }
        
        this.dropdown.innerHTML = '';
        this.selectedIndex = -1;
        
        this.results.slice(0, this.options.maxResults).forEach((result, index) => {
            const item = document.createElement('div');
            item.className = 'autocomplete-item';
            item.textContent = this.getDisplayValue(result);
            item.dataset.index = index;
            
            item.addEventListener('click', () => this.selectItem(index));
            item.addEventListener('mouseenter', () => this.highlightItem(index));
            
            this.dropdown.appendChild(item);
        });
        
        this.showDropdown();
    }

    /**
     * Get display value for result
     * @param {Object} result - Result object
     * @returns {string} Display value
     */
    getDisplayValue(result) {
        if (typeof result === 'string') return result;
        return result[this.options.displayProperty] || result.toString();
    }

    /**
     * Get value for result
     * @param {Object} result - Result object
     * @returns {string} Value
     */
    getValue(result) {
        if (typeof result === 'string') return result;
        return result[this.options.valueProperty] || this.getDisplayValue(result);
    }

    /**
     * Handle keydown events
     * @param {KeyboardEvent} e - Keyboard event
     */
    handleKeydown(e) {
        if (!this.isDropdownVisible()) return;
        
        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                this.moveSelection(1);
                break;
            case 'ArrowUp':
                e.preventDefault();
                this.moveSelection(-1);
                break;
            case 'Enter':
                e.preventDefault();
                if (this.selectedIndex >= 0) {
                    this.selectItem(this.selectedIndex);
                }
                break;
            case 'Escape':
                this.hideDropdown();
                break;
        }
    }

    /**
     * Move selection up or down
     * @param {number} direction - Direction to move (1 or -1)
     */
    moveSelection(direction) {
        const items = this.dropdown.querySelectorAll('.autocomplete-item');
        const maxIndex = items.length - 1;
        
        this.selectedIndex += direction;
        
        if (this.selectedIndex < 0) {
            this.selectedIndex = maxIndex;
        } else if (this.selectedIndex > maxIndex) {
            this.selectedIndex = 0;
        }
        
        this.highlightItem(this.selectedIndex);
    }

    /**
     * Highlight item at index
     * @param {number} index - Item index
     */
    highlightItem(index) {
        const items = this.dropdown.querySelectorAll('.autocomplete-item');
        
        items.forEach((item, i) => {
            if (i === index) {
                item.classList.add('highlighted');
                this.selectedIndex = index;
            } else {
                item.classList.remove('highlighted');
            }
        });
    }

    /**
     * Select item at index
     * @param {number} index - Item index
     */
    selectItem(index) {
        const result = this.results[index];
        if (!result) return;
        
        this.input.value = this.getValue(result);
        this.hideDropdown();
        
        // Trigger change event
        this.input.dispatchEvent(new Event('change', { bubbles: true }));
        
        // Call custom onSelect handler
        if (this.options.onSelect) {
            this.options.onSelect(result);
        }
    }

    /**
     * Show loading state
     */
    showLoading() {
        this.dropdown.innerHTML = '<div class="autocomplete-loading">Loading...</div>';
        this.showDropdown();
    }

    /**
     * Show dropdown
     */
    showDropdown() {
        this.dropdown.style.display = 'block';
        this.positionDropdown();
    }

    /**
     * Hide dropdown
     */
    hideDropdown() {
        this.dropdown.style.display = 'none';
        this.selectedIndex = -1;
    }

    /**
     * Check if dropdown is visible
     * @returns {boolean} Whether dropdown is visible
     */
    isDropdownVisible() {
        return this.dropdown.style.display !== 'none';
    }

    /**
     * Position dropdown relative to input
     */
    positionDropdown() {
        const inputRect = this.input.getBoundingClientRect();
        const parentRect = this.input.parentElement.getBoundingClientRect();
        
        this.dropdown.style.top = `${inputRect.bottom - parentRect.top}px`;
        this.dropdown.style.left = `${inputRect.left - parentRect.left}px`;
        this.dropdown.style.width = `${inputRect.width}px`;
    }

    /**
     * Destroy autocomplete
     */
    destroy() {
        if (this.dropdown && this.dropdown.parentElement) {
            this.dropdown.parentElement.removeChild(this.dropdown);
        }
    }
}