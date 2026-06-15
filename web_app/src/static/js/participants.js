let participantIndex = 0;

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

function formatPhone(value) {
    let digits = value.replace(/\D/g, '');

    // убираем первую 7 или 8, если она есть
    if (digits.startsWith('8')) {
        digits = '7' + digits.slice(1);
    }

    if (digits.startsWith('7')) {
        digits = digits.slice(1); // убираем 7, она фиксирована

        digits = digits.slice(0, 10);

        let result = '+7';

        if (digits.length > 0) result += ' (' + digits.slice(0, 3);
        if (digits.length >= 3) result += ') ' + digits.slice(3, 6);
        if (digits.length >= 6) result += '-' + digits.slice(6, 8);
        if (digits.length >= 8) result += '-' + digits.slice(8, 10);

        return result;
    }

    return '+7';
}

function validatePhone(value) {
    const digits = value.replace(/\D/g, '');
    return digits.length === 11 && digits.startsWith('7');
}

function isValidPhone(value) {
    const digits = value.replace(/\D/g, '');
    return digits.length === 11 && digits.startsWith('7');
}

function addParticipant(
    fullName = '',
    extraInfo = ''
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
                value="+7 "
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
        const formatted = formatPhone(e.target.value);

        // важно: сохраняем позицию курсора (простая версия)
        const cursor = e.target.selectionStart;

        e.target.value = formatted;

        // валидация на каждый ввод
        if (!isValidPhone(formatted)) {
            setError(phoneInput, 'Введите корректный номер');
        } else {
            clearError(phoneInput);

        }

        // грубая стабилизация курсора
        e.target.setSelectionRange(cursor, cursor);
    });

    div.querySelector('.remove-btn')
        .addEventListener('click', () => {
            div.remove();
        });

    const container =
        document.getElementById(
            'participantsContainer'
        );

    container.appendChild(div);
}

function getParticipants() {
    const cards =
        document.querySelectorAll(
            '.participant-card'
        );

    const result = [];
    for (const card of cards) {
        const name =
            card.querySelector(
                '.participant-name'
            ).value.trim();

        const phone =
            card.querySelector('.participant-phone').value.trim();

        const extraInfo =
            card.querySelector(
                '.participant-extra'
            ).value.trim();

        if (!name || !phone || !validatePhone(phone)) {
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
            addBtn.addEventListener(
                'click',
                () => addParticipant()
            );
        }

        const existing =
            window.EXISTING_PARTICIPANTS || [];

        if (existing.length) {
            existing.forEach(p => {
                addParticipant(
                    p.full_name,
                    p.extra_info || ''
                );
            });

        } else {
            addParticipant();
        }
    }
);