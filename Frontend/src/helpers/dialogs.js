let toastRoot;
let confirmRoot;
let styleInstalled = false;

function ensureStyles() {
  if (styleInstalled || typeof document === 'undefined') return;

  const style = document.createElement('style');
  style.textContent = `
    .app-toast-root {
      position: fixed;
      right: 1rem;
      top: 1rem;
      z-index: 3000;
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
      max-width: min(24rem, calc(100vw - 2rem));
      pointer-events: none;
    }

    .app-toast {
      pointer-events: auto;
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 0.75rem;
      align-items: start;
      padding: 0.875rem 1rem;
      border-radius: 0.5rem;
      border: 1px solid #d1d5db;
      background: #ffffff;
      color: #111827;
      box-shadow: 0 14px 30px rgba(15, 23, 42, 0.18);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      font-size: 0.9rem;
      line-height: 1.4;
    }

    .app-toast.warning {
      border-color: #fbbf24;
    }

    .app-toast.error {
      border-color: #f87171;
    }

    .app-toast-close {
      border: none;
      background: transparent;
      color: #6b7280;
      cursor: pointer;
      font-size: 1.25rem;
      line-height: 1;
      padding: 0;
    }

    .app-dialog-overlay {
      position: fixed;
      inset: 0;
      z-index: 4000;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 1rem;
      background: rgba(15, 23, 42, 0.48);
    }

    .app-dialog {
      width: min(26rem, 100%);
      border-radius: 0.5rem;
      border: 1px solid #e5e7eb;
      background: #ffffff;
      color: #111827;
      box-shadow: 0 24px 60px rgba(15, 23, 42, 0.28);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    .app-dialog-body {
      padding: 1.25rem;
      font-size: 0.95rem;
      line-height: 1.5;
    }

    .app-dialog-actions {
      display: flex;
      justify-content: flex-end;
      gap: 0.75rem;
      padding: 0 1.25rem 1.25rem;
    }

    .app-dialog-button {
      border: 1px solid #d1d5db;
      border-radius: 0.375rem;
      padding: 0.625rem 1rem;
      background: #ffffff;
      color: #374151;
      cursor: pointer;
      font-size: 0.875rem;
      font-weight: 600;
    }

    .app-dialog-button.primary {
      border-color: #2563eb;
      background: #2563eb;
      color: #ffffff;
    }

    .app-dialog-button.danger {
      border-color: #dc2626;
      background: #dc2626;
      color: #ffffff;
    }

    @media (prefers-color-scheme: dark) {
      .app-toast,
      .app-dialog {
        border-color: #374151;
        background: #1f2937;
        color: #f9fafb;
      }

      .app-toast-close {
        color: #d1d5db;
      }

      .app-dialog-button {
        border-color: #4b5563;
        background: #374151;
        color: #f9fafb;
      }
    }
  `;
  document.head.appendChild(style);
  styleInstalled = true;
}

function getToastRoot() {
  ensureStyles();

  if (!toastRoot) {
    toastRoot = document.createElement('div');
    toastRoot.className = 'app-toast-root';
    document.body.appendChild(toastRoot);
  }

  return toastRoot;
}

export function showAppAlert(message, options = {}) {
  if (typeof document === 'undefined') return;

  const root = getToastRoot();
  const toast = document.createElement('div');
  const variant = options.variant || 'info';
  const duration = options.duration ?? 4500;

  toast.className = `app-toast ${variant}`;

  const text = document.createElement('div');
  text.textContent = String(message ?? '');

  const close = document.createElement('button');
  close.className = 'app-toast-close';
  close.type = 'button';
  close.setAttribute('aria-label', 'Dismiss message');
  close.textContent = 'x';

  const dismiss = () => toast.remove();
  close.addEventListener('click', dismiss);

  toast.append(text, close);
  root.appendChild(toast);

  if (duration > 0) {
    window.setTimeout(dismiss, duration);
  }
}

export function confirmAction(message, options = {}) {
  if (typeof document === 'undefined') {
    return Promise.resolve(false);
  }

  ensureStyles();

  return new Promise((resolve) => {
    if (confirmRoot) {
      confirmRoot.remove();
    }

    confirmRoot = document.createElement('div');
    confirmRoot.className = 'app-dialog-overlay';

    const dialog = document.createElement('div');
    dialog.className = 'app-dialog';
    dialog.setAttribute('role', 'dialog');
    dialog.setAttribute('aria-modal', 'true');

    const body = document.createElement('div');
    body.className = 'app-dialog-body';
    body.textContent = String(message ?? '');

    const actions = document.createElement('div');
    actions.className = 'app-dialog-actions';

    const cancel = document.createElement('button');
    cancel.className = 'app-dialog-button';
    cancel.type = 'button';
    cancel.textContent = options.cancelText || 'Cancel';

    const confirm = document.createElement('button');
    confirm.className = `app-dialog-button ${options.danger ? 'danger' : 'primary'}`;
    confirm.type = 'button';
    confirm.textContent = options.confirmText || 'Confirm';

    const close = (value) => {
      confirmRoot?.remove();
      confirmRoot = null;
      resolve(value);
    };

    cancel.addEventListener('click', () => close(false));
    confirm.addEventListener('click', () => close(true));
    confirmRoot.addEventListener('click', (event) => {
      if (event.target === confirmRoot) close(false);
    });

    actions.append(cancel, confirm);
    dialog.append(body, actions);
    confirmRoot.appendChild(dialog);
    document.body.appendChild(confirmRoot);
    cancel.focus();
  });
}

export function installDialogPatch() {
  if (typeof window === 'undefined' || window.__appDialogPatchInstalled) {
    return;
  }

  window.alert = (message) => {
    showAppAlert(message);
  };

  window.confirm = (message) => {
    showAppAlert(message, { variant: 'warning', duration: 6500 });
    return false;
  };

  window.__appDialogPatchInstalled = true;
}
