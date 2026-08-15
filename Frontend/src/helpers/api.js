const LOCAL_API_ORIGINS = new Set([
  'http://localhost:5000',
  'http://127.0.0.1:5000',
]);

const configuredBaseUrl = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '');

export function apiUrl(input) {
  if (typeof input !== 'string') {
    return input;
  }

  try {
    const url = new URL(input);
    if (LOCAL_API_ORIGINS.has(url.origin)) {
      return `${configuredBaseUrl}${url.pathname}${url.search}${url.hash}`;
    }
  } catch {
    if (input.startsWith('/api/')) {
      return `${configuredBaseUrl}${input}`;
    }
  }

  return input;
}

export function installApiBaseUrlPatch() {
  if (typeof window === 'undefined' || window.__apiBaseUrlPatchInstalled) {
    return;
  }

  const originalFetch = window.fetch.bind(window);

  window.fetch = (input, init) => {
    if (typeof input === 'string') {
      return originalFetch(apiUrl(input), init);
    }

    if (input instanceof Request) {
      return originalFetch(new Request(apiUrl(input.url), input), init);
    }

    return originalFetch(input, init);
  };

  window.__apiBaseUrlPatchInstalled = true;
}
