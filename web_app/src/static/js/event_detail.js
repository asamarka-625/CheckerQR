function showMessage(
    text,
    type = 'success'
) {
    participantMessage.innerHTML =
        `<div class="${type}">${text}</div>`;
}

function clearValidation(
    input,
    errorElement
) {
    input.classList.remove('invalid-input');

    if (errorElement) {
        errorElement.textContent = '';
    }
}

function setValidationError(
    input,
    errorElement,
    message
) {
    input.classList.add('invalid-input');

    if (errorElement) {
        errorElement.textContent = message;
    }
}

function formatPhone(value) {
    let digits = value.replace(/\D/g, '');

    if (digits.startsWith('8')) {
        digits = '7' + digits.slice(1);
    }

    if (!digits.startsWith('7')) {
        digits = '7' + digits;
    }

    digits = digits.slice(0, 11);
    digits = digits.slice(1); // убираем 7

    let result = '+7';

    if (digits.length > 0) result += ' (' + digits.slice(0, 3);
    if (digits.length >= 3) result += ') ' + digits.slice(3, 6);
    if (digits.length >= 6) result += '-' + digits.slice(6, 8);
    if (digits.length >= 8) result += '-' + digits.slice(8, 10);

    return result;
}

function isValidPhone(value) {
    const digits = value.replace(/\D/g, '');
    return digits.length === 11 && digits.startsWith('7');
}

document.addEventListener('DOMContentLoaded', function () {

    const qrBlocks = document.querySelectorAll(".participant-qr");

    const qrModal = document.getElementById("qrModal");
    const qrModalOverlay = document.getElementById("qrModalOverlay");
    const closeQrModalBtn = document.getElementById("closeQrModalBtn");
    const qrModalContainer = document.getElementById("qrModalContainer");

    qrBlocks.forEach((block) => {
        const link = block.dataset.qrLink;

        new QRCode(block, {
            text: link,
            width: 120,
            height: 120
        });

        block.addEventListener("click", () => {
            qrModalContainer.innerHTML = "";

            new QRCode(qrModalContainer, {
                text: link,
                width: 360,
                height: 360
            });

            qrModal.classList.remove("hidden");
        });
    });

    function closeQrModal() {
        qrModal.classList.add("hidden");
        qrModalContainer.innerHTML = "";
    }

    qrModalOverlay.addEventListener("click", closeQrModal);
    closeQrModalBtn.addEventListener("click", closeQrModal);

    const eventId = window.EVENT_PAGE_DATA.eventId;

    const participantModal = document.getElementById('participantModal');
    const participantModalOverlay = document.getElementById('participantModalOverlay');
    const participantModalTitle = document.getElementById('participantModalTitle');
    const participantForm = document.getElementById('participantForm');
    const participantIdInput = document.getElementById('participantId');
    const participantFullNameInput = document.getElementById('participantFullName');
    const participantExtraInfoInput = document.getElementById('participantExtraInfo');
    const participantMessage = document.getElementById('participantMessage');

    const openAddParticipantBtn = document.getElementById('openAddParticipantBtn');
    const closeParticipantModalBtn = document.getElementById('closeParticipantModalBtn');
    const cancelParticipantBtn = document.getElementById('cancelParticipantBtn');
    const saveParticipantBtn = document.getElementById('saveParticipantBtn');

    const participantFullNameError = document.createElement('div');
    participantFullNameError.className = 'field-error';
    participantFullNameInput.parentElement.appendChild(participantFullNameError);

    const participantExtraInfoError = document.createElement('div');
    participantExtraInfoError.className = 'field-error';
    participantExtraInfoInput.parentElement.appendChild(participantExtraInfoError);

    const infoModal = document.getElementById('infoModal');
    const infoModalOverlay = document.getElementById('infoModalOverlay');
    const closeInfoModalBtn = document.getElementById('closeInfoModalBtn');
    const infoModalContent = document.getElementById('infoModalContent');

    const participantPhoneInput = document.getElementById('participantPhone');
    const participantPhoneError = document.getElementById('participantPhoneError');
    const participantPhoneField = document.getElementById('participantPhoneField');

    participantPhoneInput.addEventListener('keydown', (e) => {
        const cursor = e.target.selectionStart;

        if (
            (e.key === "Backspace" && cursor <= 3) ||
            (e.key === "Delete" && cursor <= 2)
        ) {
            e.preventDefault();
        }
    });

    participantPhoneInput.addEventListener('input', (e) => {
        const formatted = formatPhone(e.target.value);
        e.target.value = formatted;

        if (!isValidPhone(formatted)) {
            setValidationError(
                participantPhoneInput,
                participantPhoneError,
                'Введите корректный номер телефона'
            );
        } else {
            clearValidation(participantPhoneInput, participantPhoneError);
        }
    });

    function openInfoModal(fullName, phone, extraInfo) {
        infoModalContent.innerHTML = `
            <div style="display:flex; flex-direction:column; gap:12px;">
                <div><strong>ФИО:</strong> ${fullName || '-'}</div>
                <div><strong>Телефон:</strong> ${phone || '—'}</div>
                <div><strong>Доп. информация:</strong><br>${extraInfo || '—'}</div>
            </div>
        `;

        infoModal.classList.remove('hidden');
    }

    function closeInfoModal() {
        infoModal.classList.add('hidden');
        infoModalContent.textContent = '';
    }

    infoModalOverlay.addEventListener('click', closeInfoModal);
    closeInfoModalBtn.addEventListener('click', closeInfoModal);

    document.querySelectorAll('.participant-card').forEach(card => {
        card.addEventListener('click', (e) => {
            // чтобы кнопки не триггерили модалку
            if (e.target.closest('button')) return;

            const fullName = card.dataset.fullName;
            const phone = card.dataset.phone;
            const extraInfo = card.dataset.extraInfo;

            openInfoModal(
                fullName,
                phone ? formatPhone(phone) : '—',
                extraInfo
            );
        });
    });

    document.querySelectorAll('.participant-card button, .participant-qr')
        .forEach(el => {
            el.addEventListener('click', e => e.stopPropagation());
        });

    function openModal() {
        participantModal.classList.remove('hidden');
        participantMessage.innerHTML = '';
        clearValidation(participantPhoneInput, participantPhoneError);
    }

    function closeModal() {
        participantModal.classList.add('hidden');

        participantForm.reset();
        participantIdInput.value = '';

        participantModalTitle.textContent = 'Добавить участника';
        saveParticipantBtn.textContent = 'Сохранить';

        clearValidation(participantFullNameInput, participantFullNameError);
        clearValidation(participantExtraInfoInput, participantExtraInfoError);

        participantMessage.innerHTML = '';
        participantPhoneInput.value = '';
        clearValidation(participantPhoneInput, participantPhoneError);
    }

    participantFullNameInput.addEventListener('input', () => {
        if (participantFullNameInput.value.trim()) {
            clearValidation(participantFullNameInput, participantFullNameError);
        }
    });

    openAddParticipantBtn.addEventListener('click', () => {
        participantIdInput.value = '';
        participantFullNameInput.value = '';
        participantExtraInfoInput.value = '';
        participantPhoneInput.value = '';

        participantPhoneField.style.display = 'block';

        participantModalTitle.textContent = 'Добавить участника';
        saveParticipantBtn.textContent = 'Создать';

        openModal();
    });

    closeParticipantModalBtn.addEventListener('click', closeModal);
    cancelParticipantBtn.addEventListener('click', closeModal);
    participantModalOverlay.addEventListener('click', closeModal);

    document.querySelectorAll('.edit-participant-btn').forEach((btn) => {
        btn.addEventListener('click', () => {

            participantIdInput.value = btn.dataset.participantId;
            participantFullNameInput.value = btn.dataset.fullName;
            participantExtraInfoInput.value = btn.dataset.extraInfo || '';

            participantPhoneField.style.display = 'none';

            participantModalTitle.textContent = 'Изменить участника';
            saveParticipantBtn.textContent = 'Сохранить';

            openModal();
        });
    });

    document.querySelectorAll('.delete-participant-btn').forEach((btn) => {
        btn.addEventListener('click', async () => {

            const participantId = btn.dataset.participantId;

            if (!confirm('Удалить участника?')) return;

            try {
                const response = await apiRequest(
                    `/api/v1/event/${eventId}/participant/${participantId}`,
                    {
                        method: 'DELETE'
                    }
                );

                if (!response.ok) throw new Error();

                location.reload();

            } catch {
                alert('Не удалось удалить участника');
            }
        });
    });

    participantForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const fullName = participantFullNameInput.value.trim();
        const extraInfo = participantExtraInfoInput.value.trim();
        const participantId = participantIdInput.value.trim();

        let hasError = false;

        clearValidation(participantFullNameInput, participantFullNameError);

        if (!fullName) {
            hasError = true;
            setValidationError(
                participantFullNameInput,
                participantFullNameError,
                'Введите ФИО'
            );
        }

        const phone = participantPhoneInput.value.trim();

        if (!participantId) {
            clearValidation(participantPhoneInput, participantPhoneError);

            if (!isValidPhone(phone)) {
                hasError = true;

                setValidationError(
                    participantPhoneInput,
                    participantPhoneError,
                    'Введите корректный номер телефона'
                );
            }
        }

        if (hasError) {
            showMessage('Исправьте ошибки формы', 'error');
            return;
        }

        try {
            saveParticipantBtn.disabled = true;

            const isEdit = Boolean(participantId);

            const response = await apiRequest(
                isEdit
                    ? `/api/v1/event/${eventId}/participant/${participantId}`
                    : `/api/v1/event/${eventId}/participant`,
                {
                    method: isEdit ? 'PATCH' : 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(
                        isEdit
                            ? {
                                full_name: fullName,
                                extra_info: extraInfo
                            }
                            : {
                                full_name: fullName,
                                phone: phone,
                                extra_info: extraInfo
                            }
                    )
                }
            );

            if (!response.ok) throw new Error();

            location.reload();

        } catch {
            showMessage('Не удалось сохранить участника', 'error');

        } finally {
            saveParticipantBtn.disabled = false;
        }
    });
});