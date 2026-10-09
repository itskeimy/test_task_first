/**
 * Core UI Logic (Global Profile Dropdown, Alerts, Navigation)
 */

document.addEventListener('DOMContentLoaded', () => {
  initProfileDropdown();
  initFlashMessages();
});

/* --- Profile Dropdown Controller --- */
function initProfileDropdown() {
  const userProfile = document.getElementById('userProfileTrigger');
  const dropdown = document.getElementById('profileDropdown');

  if (!userProfile || !dropdown) return;

  userProfile.addEventListener('click', (e) => {
    e.stopPropagation();
    dropdown.classList.toggle('open');
  });

  document.addEventListener('click', (e) => {
    if (!dropdown.contains(e.target) && !userProfile.contains(e.target)) {
      dropdown.classList.remove('open');
    }
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      dropdown.classList.remove('open');
    }
  });
}

/* --- Auto-dismiss Flash Messages --- */
function initFlashMessages() {
  const messages = document.querySelectorAll('.alert-error, .alert-success');
  if (!messages.length) return;

  setTimeout(() => {
    messages.forEach((msg) => {
      msg.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
      msg.style.opacity = '0';
      msg.style.transform = 'translateY(-6px)';
      setTimeout(() => msg.remove(), 400);
    });
  }, 6000);
}
