document.addEventListener('DOMContentLoaded', function() {
    document.addEventListener('click', async (e) => {
        const btn = e.target.closest('.btn-delete');
        if (!btn) return;

        e.preventDefault();

        const eventId = btn.dataset.eventId;
        if (!confirm('Удалить мероприятие?')) {
            return;
        }

        try {
            const response = await apiRequest(
                `/api/v1/event/${eventId}`,
                {
                    method: 'DELETE'
                }
            );

            if (!response.ok) {
                throw new Error();
            }

            // удаляем карточку без перезагрузки
            btn.closest('.event-card')?.remove();

        } catch {
            alert('Ошибка удаления мероприятия');
        }
    });
});