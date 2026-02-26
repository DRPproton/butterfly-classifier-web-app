/**
 * Authentication Page Interactions
 * Handles password visibility toggle and form enhancements
 */

document.addEventListener('DOMContentLoaded', function () {

    // Password Visibility Toggle
    const passwordToggles = document.querySelectorAll('.password-toggle');

    passwordToggles.forEach(toggle => {
        toggle.addEventListener('click', function () {
            const input = this.previousElementSibling;

            if (input && input.type === 'password') {
                input.type = 'text';
                this.textContent = 'visibility_off';
            } else if (input) {
                input.type = 'password';
                this.textContent = 'visibility';
            }
        });
    });

    // Form Validation Enhancement (Optional)
    const authForms = document.querySelectorAll('.auth-form');

    authForms.forEach(form => {
        form.addEventListener('submit', function (e) {
            // Add any custom validation logic here
            const inputs = form.querySelectorAll('input[required]');
            let isValid = true;

            inputs.forEach(input => {
                if (!input.value.trim()) {
                    isValid = false;
                    input.classList.add('border-red-500');
                } else {
                    input.classList.remove('border-red-500');
                }
            });

            if (!isValid) {
                e.preventDefault();
                console.log('Please fill in all required fields');
            }
        });
    });

    // Add smooth transitions to form inputs
    const formInputs = document.querySelectorAll('.form-input');

    formInputs.forEach(input => {
        input.addEventListener('focus', function () {
            this.parentElement.classList.add('input-focused');
        });

        input.addEventListener('blur', function () {
            this.parentElement.classList.remove('input-focused');
        });
    });
});
