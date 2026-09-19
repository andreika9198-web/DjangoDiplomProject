// =====================================================
// sensors.js — автообновление показаний датчиков
// =====================================================

function updateSensors() {
    fetch('/analytics/api/sensors/')
        .then(response => response.json())
        .then(data => {
            data.plants.forEach(plant => {
                const row = document.querySelector(`[data-plant-id="${plant.plant_id}"]`);
                if (!row) return;

                // Влажность
                const humidityEl = row.querySelector('.humidity-value');
                humidityEl.textContent = plant.humidity.toFixed(1) + '%';

                // Цвет влажности
                humidityEl.classList.remove('text-danger', 'text-primary', 'text-success');
                if (plant.humidity < 30) {
                    humidityEl.classList.add('text-danger');
                } else if (plant.humidity > 70) {
                    humidityEl.classList.add('text-primary');
                } else {
                    humidityEl.classList.add('text-success');
                }

                // Температура
                const tempEl = row.querySelector('.temperature-value');
                tempEl.textContent = plant.temperature ? plant.temperature.toFixed(1) + '°C' : '—';

                // Время обновления
                const timeEl = row.querySelector('.updated-at');
                timeEl.textContent = 'Обновлено: ' + plant.created_at;
            });
        })
        .catch(error => console.error('Ошибка обновления:', error));
}

// Обновляем каждые 10 секунд
setInterval(updateSensors, 10000);