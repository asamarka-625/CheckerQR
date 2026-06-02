const isEdit = Boolean(window.EVENT_ID);
const selectedUsers = new Map();

function getDateTime() {
    const startDate =
        document.getElementById('startDate').value;

    const startTime =
        document.getElementById('startTime').value || '00:00';

    const endDate =
        document.getElementById('endDate').value;

    const endTime =
        document.getElementById('endTime').value || '00:00';

    if (!startDate || !endDate) return null;

    const start = new Date(`${startDate}T${startTime}`);
    const end = new Date(`${endDate}T${endTime}`);

    if (start >= end) return null;

    return { start, end };
}

async function saveEvent() {
    const title =
        document.getElementById('title').value.trim();

    if (!title) {
        alert('Введите название');
        return;
    }

    const dateTime = getDateTime();

    if (!dateTime) {
        alert('Ошибка дат/времени');
        return;
    }

    const payload = {
        title,
        start_datetime: dateTime.start,
        end_datetime: dateTime.end,
        access_users: [...selectedUsers.keys()]
    };

    if (!isEdit) {
        const participants = getParticipants();
        if (!participants) {
            alert('Ошибка заполнения формы участников');
            return;
        }

        if (participants.length === 0) {
            alert('Список участников пуст');
            return;
        }

        payload["participants"] = getParticipants();
    }

    const saveBtn = document.getElementById('saveBtn');

    try {
        saveBtn.disabled = true;

        const url = isEdit
            ? `/api/v1/event/${window.EVENT_ID}`
            : `/api/v1/event/create`;

        const method = isEdit ? 'PATCH' : 'POST';

        const response = await apiRequest(url, {
            method,
            body: JSON.stringify(payload)
        });

        if (!response.ok) throw new Error();

        alert(isEdit ? 'Обновлено' : 'Создано');

        location.href = `/${PREFIX}/events`;

    } catch {
        alert('Ошибка сохранения');
    } finally {
        saveBtn.disabled = false;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('saveBtn')
        .addEventListener('click', saveEvent);

    const searchInput = document.getElementById('userSearchInput');
    const resultsBox = document.getElementById('userSearchResults');
    const selectedBox = document.getElementById('selectedUsers');

    if (isEdit) {
        const existing = window.EXISTING_ACCESS_USERS || [];

        existing.forEach(user => {
            selectedUsers.set(user.id, user.full_name);
        });

        renderSelectedUsers();
    }

    function renderSelectedUsers() {
        selectedBox.innerHTML = '';

        selectedUsers.forEach((name, id) => {
            const el = document.createElement('div');
            el.className = 'user-chip';

            el.innerHTML = `
                <span>${name}</span>
                <button type="button">×</button>
            `;

            el.querySelector('button').addEventListener('click', () => {
                selectedUsers.delete(id);
                renderSelectedUsers();
            });

            selectedBox.appendChild(el);
        });
    }

    let searchTimeout = null;

    searchInput.addEventListener('input', () => {
        const name = searchInput.value.trim();

        if (searchTimeout) clearTimeout(searchTimeout);

        if (!name) {
            resultsBox.innerHTML = '';
            return;
        }

        searchTimeout = setTimeout(async () => {
            try {
                const response = await apiRequest(
                    `/api/v1/user/search/${encodeURIComponent(name)}`
                );

                if (!response.ok) return;

                const users = await response.json();

                resultsBox.innerHTML = '';

                users.forEach(user => {
                    const item = document.createElement('div');
                    item.className = 'search-item';

                    item.textContent = `${user.full_name} [${user.id}]`;

                    item.addEventListener('click', () => {
                        selectedUsers.set(user.id, user.full_name);

                        renderSelectedUsers();

                        searchInput.value = '';
                        resultsBox.innerHTML = '';
                    });

                    resultsBox.appendChild(item);
                });

            } catch (e) {
                console.error(e);
            }
        }, 300);
    });
});