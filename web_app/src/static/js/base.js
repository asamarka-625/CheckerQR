const PREFIX = window.location.pathname.split('/')[1];

function showMessage(text, type = 'success') {
    const messageOverlay = document.getElementById('message-overlay');
    const messageBox = document.getElementById('message-box');
    messageBox.textContent = text;
    messageBox.className = type;
    messageOverlay.classList.remove('hidden');

    setTimeout(() => {
        hideMessage();
    }, 3000);
}

function showSuccess(text) {
    showMessage(text, 'success');
}

function showError(text) {
    showMessage(text, 'error');
}

function hideMessage() {
    const messageOverlay = document.getElementById('message-overlay');
    messageOverlay.classList.add('hidden');
}

function formatImportError(err) {
    if (!err || !err.detail) return null;
    const d = err.detail;
    if (typeof d === 'string') return d;
    if (d.errors && Array.isArray(d.errors)) {
        return (d.message ? d.message + ':\n' : '') + d.errors.join('\n');
    }
    return null;
}

document.addEventListener('DOMContentLoaded', function() {
    const messageOverlay = document.getElementById('message-overlay');

    messageOverlay.addEventListener('click', (e) => {
        if (e.target === messageOverlay) {
            hideMessage();
        }
    });

    const logoutBtn = document.getElementById('logoutBtn');

    logoutBtn.addEventListener('click', async () => {
        await logoutRequest();
    });
});