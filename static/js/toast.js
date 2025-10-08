
(function () {
  const el = () => ({
    box: document.getElementById('toast-component'),
    title: document.getElementById('toast-title'),
    msg: document.getElementById('toast-message'),
    icon: document.getElementById('toast-icon'),
    close: document.getElementById('toast-close'),
  });

  const TYPES = {
    success: { bg: 'bg-green-50', border: '#22c55e', text: 'text-green-700', icon: '✅' },
    error:   { bg: 'bg-red-50',   border: '#ef4444', text: 'text-red-700',   icon: '⛔' },
    normal:  { bg: 'bg-white',    border: '#d1d5db', text: 'text-gray-800',  icon: '🔔' },
    info:    { bg: 'bg-blue-50',  border: '#60a5fa', text: 'text-blue-700',  icon: 'ℹ️' },
  };

  let hideTimer = null;

  function resetStyles(box) {
    box.classList.remove('bg-red-50', 'bg-green-50', 'bg-white', 'bg-blue-50',
                         'text-red-700', 'text-green-700', 'text-gray-800', 'text-blue-700');
    box.style.border = '1px solid #d1d5db';
  }

  function applyType(box, typeKey) {
    const t = TYPES[typeKey] || TYPES.normal;
    resetStyles(box);
    box.classList.add(t.bg, t.text);
    box.style.border = `1px solid ${t.border}`;
    return t.icon;
  }

  // public API
  window.showToast = function (title, message, type = 'normal', duration = 3000) {
    const { box, title: h, msg, icon, close } = el();
    if (!box) return;

    // set content
    h.textContent = title || '';
    msg.textContent = message || '';

    // set styles
    const iconChar = applyType(box, type);
    icon.textContent = iconChar;

    // open anim
    box.classList.remove('opacity-0', 'translate-y-64');
    box.classList.add('opacity-100', 'translate-y-0');

    // clear previous timer if any
    if (hideTimer) clearTimeout(hideTimer);

    // auto hide
    const safeDuration = Math.max(1200, Number(duration) || 3000);
    hideTimer = setTimeout(hideToast, safeDuration);

    // close button
    if (close && !close.dataset.bound) {
      close.addEventListener('click', hideToast);
      close.dataset.bound = '1';
    }
  };

  window.hideToast = function () {
    const { box } = el();
    if (!box) return;
    box.classList.remove('opacity-100', 'translate-y-0');
    box.classList.add('opacity-0', 'translate-y-64');
  };
})();