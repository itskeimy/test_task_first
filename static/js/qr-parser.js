/**
 * Fiscal Receipt QR Code Parser for Fast Autofill (Pure Client-Side)
 */

function initQrCodeParser() {
  const qrInput = document.getElementById('inputQRString');
  if (!qrInput) return;

  const qrUploadBox = document.getElementById('qrUploadBox');
  const qrFileInput = document.getElementById('inputQRFile');
  const qrUploadBtn = document.getElementById('qrUploadBtn');
  const qrStatus = document.getElementById('qrScanStatus');

  const setStatus = (type, message) => {
    if (!qrStatus) return;
    if (!type) {
      qrStatus.style.display = 'none';
      qrStatus.className = 'qr-status-badge';
      qrStatus.textContent = '';
      return;
    }
    qrStatus.style.display = 'block';
    qrStatus.className = `qr-status-badge ${type}`;
    qrStatus.textContent = message;
  };

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

  /**
   * Чисто клиентское распознавание QR-кода:
   * 1. Нативный браузерный BarcodeDetector (Chrome/Android/Edge/Safari) — аппаратный и устойчив к теням
   * 2. Fallback: jsQR через HTML5 Canvas с нормализацией контраста и компенсацией теней
   */
  const decodeQrFromImageElement = async (imgEl) => {
    // 1. Попытка через нативный BarcodeDetector
    if (typeof window.BarcodeDetector === 'function') {
      try {
        const detector = new window.BarcodeDetector({ formats: ['qr_code'] });
        const detected = await detector.detect(imgEl);
        if (detected && detected.length > 0 && detected[0].rawValue) {
          return detected[0].rawValue.trim();
        }
      } catch (_) {}
    }

    // 2. Клиентский fallback через jsQR
    if (typeof jsQR === 'function') {
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d', { willReadFrequently: true });
      if (!ctx) return null;

      let w = imgEl.naturalWidth || imgEl.width;
      let h = imgEl.naturalHeight || imgEl.height;

      // Масштабирование тяжелых мобильных фото (например, 48MP с телефона) для быстрой работы
      const maxDim = 1200;
      if (w > maxDim || h > maxDim) {
        if (w > h) {
          h = Math.round((h * maxDim) / w);
          w = maxDim;
        } else {
          w = Math.round((w * maxDim) / h);
          h = maxDim;
        }
      }

      canvas.width = w;
      canvas.height = h;
      ctx.drawImage(imgEl, 0, 0, w, h);

      // Проход 1: исходное изображение
      let imageData = ctx.getImageData(0, 0, w, h);
      let res = jsQR(imageData.data, w, h, { inversionAttempts: 'attemptBoth' });
      if (res && res.data) return res.data.trim();

      // Проход 2: компенсация теней и выравнивание гистограммы освещения
      const d = imageData.data;
      let minLum = 255;
      let maxLum = 0;
      for (let i = 0; i < d.length; i += 4) {
        const lum = (d[i] * 299 + d[i + 1] * 587 + d[i + 2] * 114) / 1000;
        if (lum < minLum) minLum = lum;
        if (lum > maxLum) maxLum = lum;
      }

      const lumRange = maxLum - minLum;
      if (lumRange > 15) {
        for (let i = 0; i < d.length; i += 4) {
          const lum = (d[i] * 299 + d[i + 1] * 587 + d[i + 2] * 114) / 1000;
          const val = Math.min(255, Math.max(0, ((lum - minLum) / lumRange) * 255));
          d[i] = val;
          d[i + 1] = val;
          d[i + 2] = val;
        }
        ctx.putImageData(imageData, 0, 0);
        imageData = ctx.getImageData(0, 0, w, h);
        res = jsQR(imageData.data, w, h, { inversionAttempts: 'attemptBoth' });
        if (res && res.data) return res.data.trim();
      }
    }

    return null;
  };

  const handleImageFile = (file) => {
    if (!file) return;

    if (!file.type.startsWith('image/') && !file.name.match(/\.(jpe?g|png|webp|bmp|gif)$/i)) {
      setStatus('error', 'Пожалуйста, выберите файл изображения (JPG, PNG, WEBP).');
      return;
    }

    setStatus('loading', 'Распознавание QR-кода...');
    if (qrUploadBtn) qrUploadBtn.disabled = true;

    const img = new Image();
    const objectUrl = URL.createObjectURL(file);

    img.onload = async () => {
      try {
        const qrString = await decodeQrFromImageElement(img);
        if (qrString) {
          setStatus('success', '✓ QR-код успешно распознан!');
          qrInput.value = qrString;
          qrInput.dispatchEvent(new Event('input', { bubbles: true }));
          parseAndFill();
        } else {
          setStatus('error', 'QR-код не обнаружен на фото. Попробуйте сделать снимок ближе или повернуть чек.');
        }
      } catch (err) {
        setStatus('error', 'Ошибка при обработке изображения в браузере.');
      } finally {
        URL.revokeObjectURL(objectUrl);
        if (qrUploadBtn) qrUploadBtn.disabled = false;
        if (qrFileInput) qrFileInput.value = '';
      }
    };

    img.onerror = () => {
      URL.revokeObjectURL(objectUrl);
      setStatus('error', 'Не удалось прочитать файл изображения.');
      if (qrUploadBtn) qrUploadBtn.disabled = false;
      if (qrFileInput) qrFileInput.value = '';
    };

    img.src = objectUrl;
  };

  // 1. Кнопка и выбор файла (поддерживает камеру на телефоне)
  if (qrUploadBtn && qrFileInput) {
    qrUploadBtn.addEventListener('click', () => qrFileInput.click());
    qrFileInput.addEventListener('change', () => {
      if (qrFileInput.files && qrFileInput.files[0]) {
        handleImageFile(qrFileInput.files[0]);
      }
    });
  }

  // 2. Drag & Drop в область блока
  if (qrUploadBox) {
    ['dragenter', 'dragover'].forEach((eventName) => {
      qrUploadBox.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        qrUploadBox.classList.add('drag-over');
      });
    });

    ['dragleave', 'drop'].forEach((eventName) => {
      qrUploadBox.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        qrUploadBox.classList.remove('drag-over');
      });
    });

    qrUploadBox.addEventListener('drop', (e) => {
      const file = e.dataTransfer?.files?.[0];
      if (file) handleImageFile(file);
    });
  }

  // 3. Вставка из буфера обмена (Ctrl+V скриншота)
  document.addEventListener('paste', (e) => {
    const modal = document.getElementById('registerModal');
    if (!modal || !modal.classList.contains('active')) return;

    const items = e.clipboardData?.items;
    if (!items) return;

    for (let i = 0; i < items.length; i++) {
      if (items[i].type.indexOf('image') !== -1) {
        const file = items[i].getAsFile();
        if (file) {
          e.preventDefault();
          handleImageFile(file);
          break;
        }
      }
    }
  });

  qrInput.addEventListener('input', parseAndFill);
  qrInput.addEventListener('paste', () => {
    setTimeout(parseAndFill, 50);
  });
}

document.addEventListener('DOMContentLoaded', () => {
  initQrCodeParser();
});
