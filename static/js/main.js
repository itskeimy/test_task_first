/**
 * Main Application Bundle (Aggregator for Modular Scripts)
 * For maximum backward compatibility across all templates.
 */

document.addEventListener('DOMContentLoaded', () => {
  if (typeof initProfileDropdown === 'function') initProfileDropdown();
  if (typeof initFlashMessages === 'function') initFlashMessages();
  if (typeof initModals === 'function') initModals();
  if (typeof initQrCodeParser === 'function') initQrCodeParser();
  if (typeof initReceiptForm === 'function') initReceiptForm();
  if (typeof initTableSorting === 'function') initTableSorting();
});
