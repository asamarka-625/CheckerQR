document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.btn-delete').forEach((btn) => {
        btn.addEventListener('click', async (e) => {
            e.preventDefault();
            e.stopPropagation();   // не даём сработать переходу по карточке

            const eventId = btn.dataset.eventId;

            if (!confirm('Удалить мероприятие?')) return;

            try {
                const response = await apiRequest(
                    `/api/v1/event/${eventId}`,
                    { method: 'DELETE' }
                );

                if (!response.ok) throw new Error();

                // удаляем карточку без перезагрузки
                btn.closest('.event-card')?.remove();

            } catch {
                alert('Ошибка удаления мероприятия');
            }
        });
    });
});