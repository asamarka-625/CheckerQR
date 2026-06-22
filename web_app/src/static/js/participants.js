let participantIndex = 0;

const PARTICIPANTS_PAGE_SIZE = 20;
let participantsCurrentPage = 1;

function getParticipantCards() {
    return Array.from(
        document.getElementById('participantsContainer')
            .querySelectorAll('.participant-card')
    );
}

function renderParticipantsPagination() {
    const cards = getParticipantCards();
    const total = cards.length;
    const totalPages = Math.max(1, Math.ceil(total / PARTICIPANTS_PAGE_SIZE));

    if (participantsCurrentPage > totalPages) participantsCurrentPage = totalPages;
    if (participantsCurrentPage < 1) participantsCurrentPage = 1;

    const start = (participantsCurrentPage - 1) * PARTICIPANTS_PAGE_SIZE;
    const end = start + PARTICIPANTS_PAGE_SIZE;

    // показываем только текущую страницу, остальные оставляем в DOM скрытыми
    cards.forEach((card, i) => {
        card.style.display = (i >= start && i < end) ? '' : 'none';
    });

    const controls = document.getElementById('participantsPagination');
    if (!controls) return;

    if (totalPages <= 1) {
        controls.innerHTML = '';
        controls.style.display = 'none';
        return;
    }

    controls.style.display = 'flex';
    controls.innerHTML = '';

    const prev = document.createElement('button');
    prev.type = 'button';
    prev.className = 'page-btn';
    prev.textContent = '← Назад';
    prev.disabled = participantsCurrentPage <= 1;
    prev.addEventListener('click', () => {
        participantsCurrentPage--;
        renderParticipantsPagination();
    });

    const info = document.createElement('span');
    info.className = 'page-info';
    info.textContent =
        `Страница ${participantsCurrentPage} из ${totalPages} · участников: ${total}`;

    const next = document.createElement('button');
    next.type = 'button';
    next.className = 'page-btn';
    next.textContent = 'Вперёд →';
    next.disabled = participantsCurrentPage >= totalPages;
    next.addEventListener('click', () => {
        participantsCurrentPage++;
        renderParticipantsPagination();
    });

    controls.appendChild(prev);
    controls.appendChild(info);
    controls.appendChild(next);
}

function goToParticipantCard(card) {
    const idx = getParticipantCards().indexOf(card);
    if (idx === -1) return;
    participantsCurrentPage = Math.floor(idx / PARTICIPANTS_PAGE_SIZE) + 1;
    renderParticipantsPagination();
}

function setError(input, msg) {
    let error =
        input.parentElement.querySelector('.error');

    if (!error) {
        error = document.createElement('div');
        error.className = 'error';

        input.parentElement.appendChild(error);
    } else {
        error.style.display = "block";
    }

    input.classList.add('invalid');
    error.textContent = msg;
}

function clearError(input) {
    input.classList.remove('invalid');
    const error =
        input.parentElement.querySelector('.error');

    if (error) {
        error.textContent = '';
        error.style.display = "none";
    }
}

function addParticipant(
    fullName = '',
    extraInfo = '',
    phone = ''
) {
    participantIndex++;
    const div = document.createElement('div');
    div.className = 'participant-card';

    div.innerHTML = `
        <div class="participant-title">
            Участник #${participantIndex}
        </div>

        <div class="field">
            <label>ФИО</label>

            <input
                type="text"
                class="participant-name"
                value="${fullName}"
                placeholder="Введите ФИО">
        </div>

        <div class="field">
            <label>Телефон</label>

            <input
                type="tel"
                class="participant-phone"
                value=""
                placeholder="+7 (999) 123-45-67">
        </div>

        <div class="field">
            <label>Дополнительная информация</label>

            <textarea
                class="participant-extra"
                placeholder="Любая дополнительная информация">${extraInfo}</textarea>
        </div>

        <button type="button" class="remove-btn">
            Удалить
        </button>
    `;

    const nameInput =
        div.querySelector('.participant-name');

    nameInput.addEventListener('input', (e) => {
        if (!e.target.value.trim()) {
            setError(
                nameInput,
                'Введите ФИО'
            );

        } else {
            clearError(nameInput);
        }
    });

    const phoneInput = div.querySelector('.participant-phone');

    phoneInput.addEventListener('keydown', (e) => {
        const value = e.target.value;
        const cursor = e.target.selectionStart;

        // нельзя удалить +7
        if (
            (e.key === "Backspace" && cursor <= 3) ||
            (e.key === "Delete" && cursor <= 2)
        ) {
            e.preventDefault();
        }
    });
    
    phoneInput.addEventListener('input', (e) => {
        const formatted = e.target.value;

        // важно: сохраняем позицию курсора (простая версия)
        const cursor = e.target.selectionStart;

        // грубая стабилизация курсора
        e.target.setSelectionRange(cursor, cursor);
    });

    div.querySelector('.remove-btn')
        .addEventListener('click', () => {
            div.remove();
            renderParticipantsPagination();
        });

    const container =
        document.getElementById(
            'participantsContainer'
        );

    container.appendChild(div);

    return div;
}

function getParticipants() {
    const cards =
        document.querySelectorAll(
            '.participant-card'
        );

    const result = [];
    for (const card of cards) {
        const name =
            card.querySelector('.participant-name').value.trim();

        const phone =
            card.querySelector('.participant-phone').value.trim();

        const extraInfo =
            card.querySelector('.participant-extra').value.trim();

        if (!name || !phone) {
            goToParticipantCard(card);
            return null;
        }

        result.push({
            full_name: name,
            phone: phone,
            extra_info: extraInfo
        });
    }

    return result;
}

document.addEventListener(
    'DOMContentLoaded',
    () => {
        const addBtn =
            document.getElementById(
                'addParticipantBtn'
            );

        if (addBtn) {
            addBtn.addEventListener('click', () => {
                addParticipant();
                // переходим на последнюю страницу, чтобы показать новую карточку
                const total = getParticipantCards().length;
                participantsCurrentPage =
                    Math.ceil(total / PARTICIPANTS_PAGE_SIZE);
                renderParticipantsPagination();
            });
        }

        const importBtn = document.getElementById('importParticipantsBtn');
        const importInput = document.getElementById('importParticipantsInput');

        if (importBtn && importInput) {
            importBtn.addEventListener('click', () => importInput.click());

            importInput.addEventListener('change', async () => {
                const file = importInput.files[0];
                if (!file) return;

                const formData = new FormData();
                formData.append('file', file);

                try {
                    const response = await apiRequest(
                        '/api/v1/event/parse-participants',
                        { method: 'POST', body: formData }
                    );

                    if (!response.ok) {
                        const err = await response.json().catch(() => null);
                        alert(formatImportError(err) || 'Не удалось обработать файл');
                        return;
                    }

                    const participants = await response.json();
                    participants.forEach(p =>
                        addParticipant(p.full_name, p.extra_info || '', p.phone)
                    );

                } catch {
                    alert('Ошибка загрузки файла');
                } finally {
                    importInput.value = '';
                }
            });
        }

        const existing =
            window.EXISTING_PARTICIPANTS || [];

        if (existing.length) {
            existing.forEach(p => {
                addParticipant(
                    p.full_name,
                    p.extra_info || '',
                    p.phone
                );
            });
        }

        renderParticipantsPagination();
    }
);