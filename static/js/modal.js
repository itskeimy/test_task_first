/**
 * Reusable Modal Dialog Manager
 */

function openModal(modal) {
  if (!modal) return;
  modal.classList.add('active');
  document.body.style.overflow = 'hidden';
  const firstInput = modal.querySelector('input:not([type=hidden])');
  if (firstInput) {
    setTimeout(() => firstInput.focus(), 120);
  }
}

function closeModal(modal) {
  if (!modal) return;
  modal.classList.remove('active');
  document.body.style.overflow = '';
}

function initModals() {
  const registerModal = document.getElementById('registerModal');
  const successModal = document.getElementById('successModal');
  const openButtons = document.querySelectorAll('.js-open-register-modal');
  const closeButtons = document.querySelectorAll('.js-close-modal');

  // Trigger modal open
  openButtons.forEach((btn) => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      openModal(registerModal);
    });
  });

  // Close buttons inside modal
  closeButtons.forEach((btn) => {
    btn.addEventListener('click', () => {
      const modal = btn.closest('.modal-overlay');
      if (modal) closeModal(modal);
    });
  });

  // Close on backdrop overlay click
  [registerModal, successModal].forEach((modal) => {
    if (!modal) return;
    modal.addEventListener('click', (e) => {
      if (e.target === modal) {
        closeModal(modal);
      }
    });
  });

  // Close on Escape key press
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      if (registerModal?.classList.contains('active')) closeModal(registerModal);
      if (successModal?.classList.contains('active')) closeModal(successModal);
    }
  });
}

document.addEventListener('DOMContentLoaded', () => {
  initModals();
});
