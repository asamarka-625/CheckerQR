let participantIndex = 0;

function setError(input, msg) {
    let error =
        input.parentElement.querySelector('.error');

    if (!error) {
        error = document.createElement('div');
        error.className = 'error';

        input.parentElement.appendChild(error);
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
    }
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
            <label>Дополнительная информация</label>

            <textarea
                class="participant-extra"
                placeholder="Любая дополнительная информация">${extraInfo}</textarea>
        </div>

        <button
            type="button"
            class="remove-btn">
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

        const extraInfo =
            card.querySelector(
                '.participant-extra'
            ).value.trim();

        if (!name) {
            return null;
        }

        result.push({
            full_name: name,
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