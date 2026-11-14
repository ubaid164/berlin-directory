(() => {
  const dialog = document.getElementById('safety-popup');
  if (!dialog || typeof dialog.showModal !== 'function') return;
  const storageKey = 'berlin-safety-notice-v1';
  const context = dialog.querySelector('[data-safety-context]');
  const contactURL = 'https://wa.me/491636557013';
  let pendingContact = null;
  let mode = 'visit';
  const open = (nextMode = 'notice') => {
    if (dialog.open) return;
    mode = nextMode;
    pendingContact = mode === 'contact' ? contactURL : null;
    context.hidden = mode !== 'contact' && mode !== 'demo';
    context.textContent = mode === 'contact'
      ? 'Select I Understand to continue to the website contact on WhatsApp, or Go Back to cancel.'
      : mode === 'demo' ? 'This is a demonstration. No Telegram group will open.' : '';
    dialog.showModal();
    document.documentElement.classList.add('safety-popup-open');
  };
  document.querySelectorAll('[data-open-safety-notice]').forEach(button => {
    button.addEventListener('click', () => open('notice'));
  });
  document.querySelectorAll('a[href="' + contactURL + '"]').forEach(link => {
    link.addEventListener('click', event => {
      event.preventDefault();
      open('contact');
    });
  });
  document.querySelectorAll('[data-safety-demo]').forEach(button => {
    button.addEventListener('click', () => open('demo'));
  });
  dialog.querySelector('[data-safety-understand]').addEventListener('click', () => {
    try { sessionStorage.setItem(storageKey, 'understood'); } catch (_) {}
    const destination = pendingContact;
    dialog.close();
    if (destination) window.open(destination, '_blank', 'noopener,noreferrer');
  });
  dialog.querySelector('[data-safety-back]').addEventListener('click', () => {
    const leavingSite = mode === 'visit';
    dialog.close();
    if (leavingSite) {
      if (document.referrer && window.history.length > 1) window.history.back();
      else window.location.assign('about:blank');
    }
  });
  dialog.addEventListener('close', () => {
    document.documentElement.classList.remove('safety-popup-open');
    pendingContact = null;
  });
  let understood = false;
  try { understood = sessionStorage.getItem(storageKey) === 'understood'; } catch (_) {}
  if (!understood || new URLSearchParams(window.location.search).get('safety') === '1') open('visit');
})();
