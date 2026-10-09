/**
 * Receipt Creation Form Validation & Submission
 */

function initReceiptForm() {
  const form = document.getElementById('receiptForm');
  if (!form) return;

  const inputs = form.querySelectorAll('.form-input');
  const registerModal = document.getElementById('registerModal');
  const successModal = document.getElementById('successModal');

  const fnInput = document.getElementById('inputFN');
  const fdInput = document.getElementById('inputFD');
  const fpInput = document.getElementById('inputFP');
  const dateInput = document.getElementById('inputDate');
  const sumInput = document.getElementById('inputSum');

  // 1. Live formatters & input restrictions
  if (fnInput) {
    fnInput.addEventListener('input', (e) => {
      e.target.value = e.target.value.replace(/\D/g, '').slice(0, 16);
    });
  }

  if (fdInput) {
    fdInput.addEventListener('input', (e) => {
      e.target.value = e.target.value.replace(/\D/g, '').slice(0, 10);
    });
  }

  if (fpInput) {
    fpInput.addEventListener('input', (e) => {
      e.target.value = e.target.value.replace(/\D/g, '').slice(0, 10);
    });
  }

  if (dateInput) {
    dateInput.addEventListener('input', (e) => {
      let v = e.target.value.replace(/\D/g, '').slice(0, 12);
      let formatted = '';
      if (v.length > 0) formatted += v.slice(0, 2);
      if (v.length >= 3) formatted += '.' + v.slice(2, 4);
      if (v.length >= 5) formatted += '.' + v.slice(4, 8);
      if (v.length >= 9) formatted += ' ' + v.slice(8, 10);
      if (v.length >= 11) formatted += ':' + v.slice(10, 12);
      e.target.value = formatted;
    });
  }

  if (sumInput) {
    sumInput.addEventListener('focus', (e) => {
      let v = e.target.value.replace(/\s*₽$/, '').trim();
      e.target.value = v;
    });

    sumInput.addEventListener('blur', (e) => {
      let v = e.target.value.replace(/[^\d.,]/g, '').replace(',', '.');
      const num = parseFloat(v);
      if (!isNaN(num) && num > 0) {
        e.target.value = num.toLocaleString('ru-RU', {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2
        }) + ' ₽';
      }
    });
  }

  // 2. Input wrapper states and live feedback
  inputs.forEach((input) => {
    const wrapper = input.closest('.input-wrapper');
    const clearBtn = wrapper?.querySelector('.input-clear-btn');
    const group = input.closest('.form-group');

    const updateHasValue = () => {
      if (wrapper) {
        if (input.value.trim().length > 0) {
          wrapper.classList.add('has-value');
        } else {
          wrapper.classList.remove('has-value');
        }
      }
    };

    input.addEventListener('input', () => {
      updateHasValue();
      if (group?.classList.contains('has-error')) {
        validateReceiptField(input);
      }
    });

    input.addEventListener('blur', () => {
      if (input.dataset.touched === 'true') {
        validateReceiptField(input);
      }
    });

    input.addEventListener('focus', () => {
      input.dataset.touched = 'true';
    });

    if (clearBtn) {
      clearBtn.addEventListener('click', () => {
        input.value = '';
        updateHasValue();
        input.focus();
        if (group) group.classList.remove('has-error');
      });
    }

    updateHasValue();
  });

  // 3. Form submission via fetch (AJAX)
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    let hasError = false;
    let firstErrorInput = null;

    inputs.forEach((input) => {
      input.dataset.touched = 'true';
      const isValid = validateReceiptField(input);
      if (!isValid) {
        hasError = true;
        if (!firstErrorInput) {
          firstErrorInput = input;
        }
      }
    });

    if (hasError) {
      if (firstErrorInput) firstErrorInput.focus();
      return;
    }

    const submitBtn = document.getElementById('submitReceiptBtn');
    const btnText = submitBtn?.querySelector('.btn-text');
    const btnSpinner = submitBtn?.querySelector('.btn-spinner');
    const generalError = document.getElementById('formGeneralError');

    if (generalError) {
      generalError.style.display = 'none';
      generalError.textContent = '';
    }

    if (submitBtn) submitBtn.disabled = true;
    if (btnText && btnSpinner) {
      btnText.style.display = 'none';
      btnSpinner.style.display = 'inline';
    }

    try {
      const formData = new FormData(form);
      const csrfToken = form.querySelector('[name=csrfmiddlewaretoken]')?.value;

      const response = await fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          ...(csrfToken ? { 'X-CSRFToken': csrfToken } : {})
        }
      });

      const data = await response.json().catch(() => null);

      if (response.ok && data?.success) {
        form.reset();
        inputs.forEach((inp) => {
          inp.closest('.input-wrapper')?.classList.remove('has-value');
          inp.closest('.form-group')?.classList.remove('has-error');
          delete inp.dataset.touched;
        });

        if (registerModal) closeModal(registerModal);
        if (successModal) {
          openModal(successModal);
          const closeBtn = document.getElementById('successModalCloseBtn');
          if (closeBtn) {
            closeBtn.onclick = () => window.location.reload();
          }
        } else {
          window.location.reload();
        }
      } else {
        if (data?.errors) {
          const fieldMap = {
            fn: 'inputFN',
            fd: 'inputFD',
            fp: 'inputFP',
            purchase_date: 'inputDate',
            total_amount: 'inputSum'
          };

          let hasFieldErrors = false;
          for (const [fieldName, errList] of Object.entries(data.errors)) {
            const inputId = fieldMap[fieldName];
            if (inputId) {
              const inp = document.getElementById(inputId);
              const group = inp?.closest('.form-group');
              const tooltip = group?.querySelector('.error-tooltip-text');
              if (group && tooltip) {
                tooltip.textContent = Array.isArray(errList) ? errList[0] : errList;
                group.classList.add('has-error');
                hasFieldErrors = true;
              }
            } else if (fieldName === '__all__') {
              if (generalError) {
                generalError.textContent = Array.isArray(errList) ? errList[0] : errList;
                generalError.style.display = 'block';
              }
            }
          }

          if (!hasFieldErrors && generalError && !generalError.textContent) {
            generalError.textContent = 'Пожалуйста, проверьте правильность введенных реквизитов.';
            generalError.style.display = 'block';
          }
        } else if (data?.message && generalError) {
          generalError.textContent = data.message;
          generalError.style.display = 'block';
        } else if (generalError) {
          generalError.textContent = 'Произошла ошибка при регистрации чека. Попробуйте еще раз.';
          generalError.style.display = 'block';
        }
      }
    } catch (err) {
      console.error('Ошибка отправки формы:', err);
      if (generalError) {
        generalError.textContent = 'Ошибка сети. Проверьте интернет-соединение.';
        generalError.style.display = 'block';
      }
    } finally {
      if (submitBtn) submitBtn.disabled = false;
      if (btnText && btnSpinner) {
        btnText.style.display = 'inline';
        btnSpinner.style.display = 'none';
      }
    }
  });
}

function validateReceiptField(input) {
  const group = input.closest('.form-group');
  if (!group) return true;

  const tooltipText = group.querySelector('.error-tooltip-text');
  const rawValue = input.value.trim();
  let isValid = true;
  let errorMsg = 'Ошибка! Заполните поле';

  if (!rawValue) {
    isValid = false;
    errorMsg = 'Ошибка! Заполните поле';
  } else {
    switch (input.id) {
      case 'inputFN': {
        const cleanVal = rawValue.replace(/\s/g, '');
        if (!/^\d+$/.test(cleanVal)) {
          isValid = false;
          errorMsg = 'Ошибка! ФН должен содержать только цифры';
        } else if (cleanVal.length !== 16) {
          isValid = false;
          errorMsg = 'Ошибка! Номер ФН должен состоять из 16 цифр';
        }
        break;
      }

      case 'inputFD': {
        const cleanVal = rawValue.replace(/\s/g, '');
        if (!/^\d+$/.test(cleanVal)) {
          isValid = false;
          errorMsg = 'Ошибка! Номер чека должен содержать только цифры';
        } else if (parseInt(cleanVal, 10) === 0) {
          isValid = false;
          errorMsg = 'Ошибка! Номер чека должен быть больше 0';
        } else if (cleanVal.length > 10) {
          isValid = false;
          errorMsg = 'Ошибка! Номер чека не может быть длиннее 10 цифр';
        }
        break;
      }

      case 'inputFP': {
        const cleanVal = rawValue.replace(/\s/g, '');
        if (!/^\d+$/.test(cleanVal)) {
          isValid = false;
          errorMsg = 'Ошибка! ФП должен содержать только цифры';
        } else if (cleanVal.length < 4 || cleanVal.length > 10) {
          isValid = false;
          errorMsg = 'Ошибка! ФП должен содержать от 4 до 10 цифр';
        }
        break;
      }

      case 'inputDate': {
        const dateMatch = rawValue.match(/^(\d{2})\.(\d{2})\.(\d{4})(?:\s+(\d{2}):(\d{2}))?$/);
        if (!dateMatch) {
          isValid = false;
          errorMsg = 'Ошибка! Формат: дд.мм.гггг чч:мм';
        } else {
          const day = parseInt(dateMatch[1], 10);
          const month = parseInt(dateMatch[2], 10);
          const year = parseInt(dateMatch[3], 10);
          const hour = dateMatch[4] !== undefined ? parseInt(dateMatch[4], 10) : 0;
          const min = dateMatch[5] !== undefined ? parseInt(dateMatch[5], 10) : 0;

          if (month < 1 || month > 12) {
            isValid = false;
            errorMsg = 'Ошибка! Некорректный месяц (01-12)';
          } else if (hour < 0 || hour > 23 || min < 0 || min > 59) {
            isValid = false;
            errorMsg = 'Ошибка! Некорректное время (00:00 - 23:59)';
          } else if (year < 2000 || year > new Date().getFullYear()) {
            isValid = false;
            errorMsg = 'Ошибка! Некорректный год покупки';
          } else {
            const dateObj = new Date(year, month - 1, day, hour, min);
            if (dateObj.getFullYear() !== year || dateObj.getMonth() !== month - 1 || dateObj.getDate() !== day) {
              isValid = false;
              errorMsg = 'Ошибка! Такой даты в календаре не существует';
            } else if (dateObj > new Date(Date.now() + 9 * 3600 * 1000)) {
              isValid = false;
              errorMsg = 'Ошибка! Дата чека не может быть в будущем';
            }
          }
        }
        break;
      }

      case 'inputSum': {
        const cleanVal = rawValue.replace(/\s/g, '').replace('₽', '').replace(',', '.');
        const num = parseFloat(cleanVal);
        if (isNaN(num) || !/^\d+(\.\d{1,2})?$/.test(cleanVal)) {
          isValid = false;
          errorMsg = 'Ошибка! Введите корректную сумму';
        } else if (num <= 0) {
          isValid = false;
          errorMsg = 'Ошибка! Сумма должна быть больше 0';
        } else if (num > 100000000) {
          isValid = false;
          errorMsg = 'Ошибка! Сумма не может превышать 100 000 000 ₽';
        }
        break;
      }

      default:
        break;
    }
  }

  if (!isValid) {
    group.classList.add('has-error');
    if (tooltipText) tooltipText.textContent = errorMsg;
    return false;
  } else {
    group.classList.remove('has-error');
    return true;
  }
}

document.addEventListener('DOMContentLoaded', () => {
  initReceiptForm();
});
