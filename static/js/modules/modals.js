/**
 * Modals Module - Handles modal dialogs
 * @module modals
 */

export class Modal {
    /**
     * Create a modal
     * @param {string} id - Modal ID
     * @param {Object} options - Modal options
     */
    constructor(id, options = {}) {
        this.id = id;
        this.options = {
            title: 'Modal',
            content: '',
            closable: true,
            onOpen: null,
            onClose: null,
            buttons: [],
            ...options
        };
        
        this.modal = null;
        this.isOpen = false;
        
        this.create();
    }

    /**
     * Create modal element
     */
    create() {
        // Create modal container
        this.modal = document.createElement('div');
        this.modal.id = this.id;
        this.modal.className = 'modal';
        
        // Create modal content
        const content = document.createElement('div');
        content.className = 'modal-content';
        
        // Header
        if (this.options.title) {
            const header = document.createElement('div');
            header.className = 'modal-header';
            
            const title = document.createElement('h2');
            title.textContent = this.options.title;
            header.appendChild(title);
            
            if (this.options.closable) {
                const closeBtn = document.createElement('span');
                closeBtn.className = 'close';
                closeBtn.innerHTML = '&times;';
                closeBtn.onclick = () => this.close();
                header.appendChild(closeBtn);
            }
            
            content.appendChild(header);
        }
        
        // Body
        const body = document.createElement('div');
        body.className = 'modal-body';
        if (typeof this.options.content === 'string') {
            body.innerHTML = this.options.content;
        } else {
            body.appendChild(this.options.content);
        }
        content.appendChild(body);
        
        // Footer with buttons
        if (this.options.buttons.length > 0) {
            const footer = document.createElement('div');
            footer.className = 'modal-footer';
            
            this.options.buttons.forEach(btnConfig => {
                const button = document.createElement('button');
                button.className = btnConfig.className || 'btn btn-secondary';
                button.textContent = btnConfig.text;
                button.onclick = () => {
                    if (btnConfig.onClick) {
                        btnConfig.onClick(this);
                    }
                    if (btnConfig.closeOnClick !== false) {
                        this.close();
                    }
                };
                footer.appendChild(button);
            });
            
            content.appendChild(footer);
        }
        
        this.modal.appendChild(content);
        
        // Click outside to close
        if (this.options.closable) {
            this.modal.onclick = (e) => {
                if (e.target === this.modal) {
                    this.close();
                }
            };
        }
        
        // Add to body
        document.body.appendChild(this.modal);
    }

    /**
     * Open modal
     */
    open() {
        if (this.isOpen) return;
        
        this.modal.style.display = 'block';
        this.isOpen = true;
        
        // Add body class to prevent scrolling
        document.body.classList.add('modal-open');
        
        // Call onOpen callback
        if (this.options.onOpen) {
            this.options.onOpen(this);
        }
    }

    /**
     * Close modal
     */
    close() {
        if (!this.isOpen) return;
        
        this.modal.style.display = 'none';
        this.isOpen = false;
        
        // Remove body class
        document.body.classList.remove('modal-open');
        
        // Call onClose callback
        if (this.options.onClose) {
            this.options.onClose(this);
        }
    }

    /**
     * Update modal content
     * @param {string|HTMLElement} content - New content
     */
    updateContent(content) {
        const body = this.modal.querySelector('.modal-body');
        if (body) {
            if (typeof content === 'string') {
                body.innerHTML = content;
            } else {
                body.innerHTML = '';
                body.appendChild(content);
            }
        }
    }

    /**
     * Update modal title
     * @param {string} title - New title
     */
    updateTitle(title) {
        const titleEl = this.modal.querySelector('.modal-header h2');
        if (titleEl) {
            titleEl.textContent = title;
        }
    }

    /**
     * Destroy modal
     */
    destroy() {
        this.close();
        if (this.modal && this.modal.parentElement) {
            this.modal.parentElement.removeChild(this.modal);
        }
    }
}

/**
 * Confirmation dialog
 * @param {string} message - Confirmation message
 * @param {Function} onConfirm - Confirm callback
 * @param {Function} onCancel - Cancel callback
 * @returns {Modal} Modal instance
 */
export function confirm(message, onConfirm, onCancel) {
    const modal = new Modal('confirm-modal', {
        title: 'Confirm',
        content: message,
        buttons: [
            {
                text: 'Cancel',
                className: 'btn btn-secondary',
                onClick: onCancel
            },
            {
                text: 'Confirm',
                className: 'btn btn-primary',
                onClick: () => {
                    if (onConfirm) onConfirm();
                }
            }
        ]
    });
    
    modal.open();
    return modal;
}

/**
 * Alert dialog
 * @param {string} message - Alert message
 * @param {string} title - Alert title
 * @returns {Modal} Modal instance
 */
export function alert(message, title = 'Alert') {
    const modal = new Modal('alert-modal', {
        title: title,
        content: message,
        buttons: [
            {
                text: 'OK',
                className: 'btn btn-primary'
            }
        ]
    });
    
    modal.open();
    return modal;
}

/**
 * Preview modal for issue preview
 * @param {Object} previewData - Preview data
 * @param {Function} onCreate - Create callback
 * @returns {Modal} Modal instance
 */
export function previewModal(previewData, onCreate) {
    const content = document.createElement('div');
    content.innerHTML = `
        <div class="preview-section">
            <h3>Title:</h3>
            <p>${previewData.title}</p>
        </div>
        <div class="preview-section">
            <h3>Body:</h3>
            <pre>${previewData.body}</pre>
        </div>
        <div class="preview-section">
            <h3>Labels:</h3>
            <div class="labels">
                ${previewData.labels.map(label => `<span class="label">${label}</span>`).join(' ')}
            </div>
        </div>
        <div class="preview-section">
            <h3>Project Fields:</h3>
            <table class="preview-table">
                ${Object.entries(previewData.project_fields).map(([key, value]) => `
                    <tr>
                        <td><strong>${key}:</strong></td>
                        <td>${value}</td>
                    </tr>
                `).join('')}
            </table>
        </div>
    `;
    
    const modal = new Modal('preview-modal', {
        title: 'Issue Preview',
        content: content,
        buttons: [
            {
                text: 'Cancel',
                className: 'btn btn-secondary'
            },
            {
                text: 'Create Issue',
                className: 'btn btn-primary',
                onClick: () => {
                    if (onCreate) onCreate();
                }
            }
        ]
    });
    
    modal.open();
    return modal;
}