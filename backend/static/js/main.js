// TaskRhythm - Main JavaScript
// Minimal client-side interactivity with custom modals

// Custom Modal Handler
let currentConfirmCallback = null;

function showModal(title, message, onConfirm) {
    const modal = document.getElementById('customModal');
    const modalTitle = document.getElementById('modalTitle');
    const modalMessage = document.getElementById('modalMessage');
    
    modalTitle.textContent = title;
    modalMessage.textContent = message;
    currentConfirmCallback = onConfirm;
    
    modal.classList.add('show');
}

function hideModal() {
    const modal = document.getElementById('customModal');
    modal.classList.remove('show');
    currentConfirmCallback = null;
}

function confirmModal() {
    if (currentConfirmCallback) {
        currentConfirmCallback();
    }
    hideModal();
}

function cancelModal() {
    hideModal();
}

// Custom confirm replacement
window.customConfirm = function(message, title = 'Confirm Action') {
    return new Promise((resolve) => {
        showModal(title, message, () => resolve(true));
    });
};

document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide success/error messages after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.5s';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });

    // Handle custom confirm dialogs
    document.addEventListener('click', function(e) {
        const confirmBtn = e.target.closest('[data-confirm]');
        if (confirmBtn) {
            e.preventDefault();
            e.stopPropagation();
            
            const message = confirmBtn.getAttribute('data-confirm');
            const title = confirmBtn.getAttribute('data-confirm-title') || 'Confirm Action';
            const form = confirmBtn.closest('form');
            
            showModal(title, message, () => {
                if (form) {
                    // Create a hidden input to bypass the event listener
                    const input = document.createElement('input');
                    input.type = 'hidden';
                    input.name = '_confirmed';
                    input.value = '1';
                    form.appendChild(input);
                    
                    // Remove the data-confirm attribute temporarily
                    confirmBtn.removeAttribute('data-confirm');
                    
                    // Submit the form
                    form.submit();
                }
            });
            
            return false;
        }
    }, true); // Use capture phase

    // Close modal when clicking outside
    const modal = document.getElementById('customModal');
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                hideModal();
            }
        });
    }

    // Form validation feedback (skip for forms with data-confirm)
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const hasConfirm = form.querySelector('[data-confirm]');
            if (!hasConfirm) {
                const submitButton = this.querySelector('button[type="submit"]');
                if (submitButton && !submitButton.disabled) {
                    submitButton.disabled = true;
                    const originalText = submitButton.textContent;
                    submitButton.textContent = 'Processing...';
                    
                    // Re-enable if form fails to submit
                    setTimeout(() => {
                        submitButton.disabled = false;
                        submitButton.textContent = originalText;
                    }, 3000);
                }
            }
        });
    });

    console.log('TaskRhythm loaded - Work with your energy, not against it! 💙');
});

