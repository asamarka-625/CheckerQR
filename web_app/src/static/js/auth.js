let accessToken = null;
let csrfToken = null;
let refreshTimeout = null;

async function silentRefresh() {
    if (window.location.pathname === `/${PREFIX}/login`) {
        return;
    }

    try {
        const response = await fetch(`/${PREFIX}/api/v1/auth/refresh`, { method: 'POST' });

        if (response.ok) {
            const data = await response.json();
            accessToken = data.access_token;
            csrfToken = data.csrf_token;

            if (refreshTimeout) clearTimeout(refreshTimeout);
            refreshTimeout = setTimeout(silentRefresh, 14 * 60 * 1000);

        } else {
            window.location.href = `/${PREFIX}/login`;
        }
    } catch (error) {
        console.error("Ошибка фонового обновления");
    }
}

async function apiRequest(url, options = {}) {
    if (!accessToken) await silentRefresh();

    const isFormData = options.body instanceof FormData;

    const buildHeaders = () => ({
        ...(isFormData ? {} : { 'Content-Type': 'application/json' }),
        'Authorization': `Bearer ${accessToken}`,
        'X-CSRF-Token': csrfToken,
        ...options.headers
    });

    let response = await fetch(`/${PREFIX}${url}`, { ...options, headers: buildHeaders() });

    if (response.status === 401) {
        await silentRefresh();
        response = await fetch(`/${PREFIX}${url}`, { ...options, headers: buildHeaders() });
    }

    return response;
}

async function logoutRequest() {
    try {
        const response = await apiRequest(`/api/v1/auth/logout`, {
            method: 'POST'
        });

        if (response.ok) {
            const data = await response.json();
            accessToken = null;
            csrfToken = null;
            if (refreshTimeout) clearTimeout(refreshTimeout);

            window.location.href = `/${PREFIX}/login`;
        }
    } catch (error) {
        console.error("Ошибка выхода из сессии", error);
    }
}

document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible') {
        silentRefresh();
    }
});

