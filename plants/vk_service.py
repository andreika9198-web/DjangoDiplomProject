import os
import requests

VK_API_URL = "https://api.vk.com/method/messages.send"
VK_API_VERSION = "5.131"


def vk_send_message(user_vk_id, message):
    """Отправляет сообщение пользователю ВК."""
    token = os.getenv('VK_TOKEN')
    group_id = os.getenv('VK_GROUP_ID')  # опционально

    if not token:
        print("VK_TOKEN не задан в .env")
        return False

    if not user_vk_id:
        print("У пользователя нет vk_id")
        return False

    params = {
        'user_id': user_vk_id,
        'message': message,
        'access_token': token,
        'v': VK_API_VERSION,
        'random_id': 0,
    }

    try:
        response = requests.get(VK_API_URL, params=params, timeout=5)
        data = response.json()

        if 'error' in data:
            print(f"VK ошибка: {data['error']}")
            return False

        print(f"VK сообщение отправлено: {user_vk_id}")
        return True

    except Exception as e:
        print(f"VK ошибка: {e}")
        return False