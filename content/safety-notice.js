(() => {
  const dialog = document.getElementById('safety-popup');
  if (!dialog || typeof dialog.showModal !== 'function') return;
  const storageKey = 'berlin-safety-notice-v1';
  const open = () => {
    if (dialog.open) return;
    dialog.showModal();
    document.documentElement.classList.add('safety-popup-open');
  };
  document.querySelectorAll('[data-open-safety-notice]').forEach(button => {
    button.addEventListener('click', open);
  });
  dialog.querySelector('[data-safety-understand]').addEventListener('click', () => {
    try { sessionStorage.setItem(storageKey, 'understood'); } catch (_) {}
    dialog.close();
  });
  dialog.querySelector('[data-safety-back]').addEventListener('click', () => {
    dialog.close();
    if (document.referrer && window.history.length > 1) window.history.back();
    else window.location.assign('about:blank');
  });
  dialog.addEventListener('close', () => {
    document.documentElement.classList.remove('safety-popup-open');
  });
  let understood = false;
  try { understood = sessionStorage.getItem(storageKey) === 'understood'; } catch (_) {}
  if (!understood || new URLSearchParams(window.location.search).get('safety') === '1') open();
})();
