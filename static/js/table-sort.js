/**
 * Client-side Receipts Table Sorting
 */

function initTableSorting() {
  const table = document.querySelector('.receipts-table');
  if (!table) return;

  const staticUrl = window.STATIC_URL || '/static/';
  const headers = table.querySelectorAll('th[data-sort]');

  headers.forEach((th) => {
    th.addEventListener('click', () => {
      const colIndex = parseInt(th.dataset.col, 10);
      const isAsc = th.classList.contains('sort-asc');
      
      headers.forEach((h) => {
        h.classList.remove('sort-asc', 'sort-desc');
        const icon = h.querySelector('.th-sort-btn img');
        if (icon) icon.src = `${staticUrl}icons/sort-table.svg`;
      });

      const icon = th.querySelector('.th-sort-btn img');
      if (isAsc) {
        th.classList.add('sort-desc');
        if (icon) icon.src = `${staticUrl}icons/sort-down.svg`;
        sortTable(table, colIndex, false);
      } else {
        th.classList.add('sort-asc');
        if (icon) icon.src = `${staticUrl}icons/sort-up.svg`;
        sortTable(table, colIndex, true);
      }
    });
  });
}

function sortTable(table, colIndex, asc) {
  const tbody = table.querySelector('tbody');
  if (!tbody) return;
  const rows = Array.from(tbody.querySelectorAll('tr'));

  rows.sort((a, b) => {
    const aText = a.cells[colIndex]?.innerText.trim() || '';
    const bText = b.cells[colIndex]?.innerText.trim() || '';

    // Numeric comparison for amounts if applicable
    const aNum = parseFloat(aText.replace(/[^\d.,]/g, '').replace(',', '.'));
    const bNum = parseFloat(bText.replace(/[^\d.,]/g, '').replace(',', '.'));

    if (!isNaN(aNum) && !isNaN(bNum) && colIndex === 2) {
      return asc ? aNum - bNum : bNum - aNum;
    }

    return asc ? aText.localeCompare(bText, 'ru') : bText.localeCompare(aText, 'ru');
  });

  rows.forEach((row) => tbody.appendChild(row));
}

document.addEventListener('DOMContentLoaded', () => {
  initTableSorting();
});
