/**
 * Authentication and Registration Form Client-Side Validation
 */

function initAuthFormValidation() {
  const form = document.querySelector('.auth-form');
  if (!form) return;

  const inputs = form.querySelectorAll('.form-input');

  const setError = (input, message) => {
    const group = input.closest('.form-group');
    if (!group) return;
    const tooltipText = group.querySelector('.error-tooltip-text');
    if (tooltipText) tooltipText.textContent = message;
    group.classList.add('has-error');
  };

  const clearError = (input) => {
    const group = input.closest('.form-group');
    if (!group) return;
    group.classList.remove('has-error');
  };

  const validateField = (input) => {
    const val = input.value.trim();
    const id = input.id;

    if (!val) {
      if (input.required) {
        setError(input, 'Заполните это поле');
        return false;
      }
      clearError(input);
      return true;
    }

    if (id === 'id_username') {
      if (val.length < 3) {
        setError(input, 'Логин должен быть от 3 символов');
        return false;
      }
      if (!/^[a-zA-Z0-9@.+_-]+$/.test(val)) {
        setError(input, 'Недопустимые символы в логине');
        return false;
      }
    } else if (id === 'id_email') {
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val)) {
        setError(input, 'Введите корректный email адрес');
        return false;
      }
    } else if (id === 'id_password1') {
      if (val.length < 8) {
        setError(input, 'Пароль должен содержать от 8 символов');
        return false;
      }
      const pass2 = document.getElementById('id_password2');
      if (pass2 && pass2.value && pass2.value !== val) {
        setError(pass2, 'Пароли не совпадают');
      } else if (pass2 && pass2.value && pass2.value === val) {
        clearError(pass2);
      }
    } else if (id === 'id_password2') {
      const pass1 = document.getElementById('id_password1');
      if (pass1 && val !== pass1.value) {
        setError(input, 'Пароли не совпадают');
        return false;
      }
    } else if (id === 'id_password') {
      if (val.length < 1) {
        setError(input, 'Введите пароль');
        return false;
      }
    }

    clearError(input);
    return true;
  };

  inputs.forEach((input) => {
    input.addEventListener('input', () => {
      const group = input.closest('.form-group');
      if (group?.classList.contains('has-error')) {
        validateField(input);
      }
      if (input.id === 'id_password2') {
        const pass1 = document.getElementById('id_password1');
        if (pass1 && input.value === pass1.value) {
          clearError(input);
        }
      }
    });

    input.addEventListener('blur', () => {
      if (input.dataset.touched === 'true') {
        validateField(input);
      }
    });

    input.addEventListener('focus', () => {
      input.dataset.touched = 'true';
    });
  });

  form.addEventListener('submit', (e) => {
    let hasError = false;
    let firstErrorInput = null;

    inputs.forEach((input) => {
      input.dataset.touched = 'true';
      const valid = validateField(input);
      if (!valid) {
        hasError = true;
        if (!firstErrorInput) firstErrorInput = input;
      }
    });

    if (hasError) {
      e.preventDefault();
      if (firstErrorInput) firstErrorInput.focus();
    }
  });
}

document.addEventListener('DOMContentLoaded', () => {
  initAuthFormValidation();
});
