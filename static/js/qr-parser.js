/**
 * Fiscal Receipt QR Code Parser for Fast Autofill
 */

function initQrCodeParser() {
  const qrInput = document.getElementById('inputQRString');
  if (!qrInput) return;

  const parseAndFill = () => {
    let val = qrInput.value.trim();
    if (!val) return;

    if (val.includes('?')) {
      val = val.split('?')[1];
    }

    const params = new URLSearchParams(val);
    const fn = params.get('fn');
    const fd = params.get('i') || params.get('fd');
    const fp = params.get('fp');
    const s = params.get('s');
    const t = params.get('t');

    if (fn) {
      const fnInput = document.getElementById('inputFN');
      if (fnInput) {
        fnInput.value = fn;
        fnInput.dispatchEvent(new Event('input', { bubbles: true }));
        fnInput.dispatchEvent(new Event('blur', { bubbles: true }));
      }
    }

    if (fd) {
      const fdInput = document.getElementById('inputFD');
      if (fdInput) {
        fdInput.value = fd;
        fdInput.dispatchEvent(new Event('input', { bubbles: true }));
        fdInput.dispatchEvent(new Event('blur', { bubbles: true }));
      }
    }

    if (fp) {
      const fpInput = document.getElementById('inputFP');
      if (fpInput) {
        fpInput.value = fp;
        fpInput.dispatchEvent(new Event('input', { bubbles: true }));
        fpInput.dispatchEvent(new Event('blur', { bubbles: true }));
      }
    }

    if (s) {
      const sumInput = document.getElementById('inputSum');
      if (sumInput) {
        const cleanS = s.replace(',', '.');
        const num = parseFloat(cleanS);
        if (!isNaN(num)) {
          sumInput.value = `${num.toFixed(2)} ₽`;
        } else {
          sumInput.value = s;
        }
        sumInput.dispatchEvent(new Event('input', { bubbles: true }));
        sumInput.dispatchEvent(new Event('blur', { bubbles: true }));
      }
    }

    if (t) {
      const dateInput = document.getElementById('inputDate');
      if (dateInput) {
        let formattedDate = '';
        const compactMatch = t.match(/^(\d{4})(\d{2})(\d{2})T(\d{2})(\d{2})/);
        const isoMatch = t.match(/^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})/);

        if (compactMatch) {
          const [, year, month, day, hour, min] = compactMatch;
          formattedDate = `${day}.${month}.${year} ${hour}:${min}`;
        } else if (isoMatch) {
          const [, year, month, day, hour, min] = isoMatch;
          formattedDate = `${day}.${month}.${year} ${hour}:${min}`;
        }

        if (formattedDate) {
          dateInput.value = formattedDate;
          dateInput.dispatchEvent(new Event('input', { bubbles: true }));
          dateInput.dispatchEvent(new Event('blur', { bubbles: true }));
        }
      }
    }
  };

  qrInput.addEventListener('input', parseAndFill);
  qrInput.addEventListener('paste', () => {
    setTimeout(parseAndFill, 50);
  });
}

document.addEventListener('DOMContentLoaded', () => {
  initQrCodeParser();
});
