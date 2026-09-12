function setState(field, value) {
    fetch('/api/state/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ [field]: value })
    })
    .then(response => response.json())
    .then(data => {
        console.log('OK:', data);
        location.reload();  // перезагружаем страницу, чтобы увидеть изменения
    })
    .catch(error => console.error('Ошибка:', error));
}

// ===== Загрузка текущего состояния =====
function loadState() {
    fetch('/api/state/')
        .then(response => response.json())
        .then(data => {
            const autoEl = document.getElementById('state-automatic');
            const pumpEl = document.getElementById('state-pump');
            const lightEl = document.getElementById('state-light');

            if (autoEl) autoEl.textContent = data.automatic ? '✅ ВКЛ' : '❌ ВЫКЛ';
            if (pumpEl) pumpEl.textContent = data.pump ? '✅ ВКЛ' : '❌ ВЫКЛ';
            if (lightEl) lightEl.textContent = data.light ? '✅ ВКЛ' : '❌ ВЫКЛ';
        })
        .catch(error => console.error('Ошибка загрузки:', error));
}

// ===== CSRF-токен для POST =====
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// ===== Автообновление статуса каждые 5 секунд =====
setInterval(loadState, 5000);

// ===== Загружаем состояние при открытии страницы =====
loadState();
