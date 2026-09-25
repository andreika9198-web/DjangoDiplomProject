import ctypes

import cv2
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import StreamingHttpResponse, HttpResponse
from django.views.generic import UpdateView, ListView, CreateView, DeleteView
from django.urls import reverse_lazy
from pygrabber.dshow_graph import FilterGraph
from django.core.exceptions import PermissionDenied
from django.shortcuts import render


from .vk_service import vk_send_message
from .models import SensorData, DeviceState, CameraState, Plant
from .serializers import SensorDataSerializer, WateringLogSerializer
from devices.models import Device
from .forms import PlantForm

def index(request):
    """
    Главная страница сайта.
    Отображает приветственную страницу с заголовком.
    """
    return render(request, 'index.html', {'title': 'Главная'})


class SensorDataAPIView(APIView):
    """
    API для приёма данных от ESP32.
    Принимает POST-запросы с показаниями датчиков,
    сохраняет их в БД и проверяет критические значения.
    """
    def post(self, request):
        device_id = request.data.get('device')

        # Ищем устройство
        try:
            device = Device.objects.get(device_id=device_id, is_active=True)
        except Device.DoesNotExist:
            return Response({"error": f"Device {device_id} not found"}, status=404)

        if not device.plant:
            return Response({"error": "Device not linked to any plant"}, status=400)

        # Обновляем время последнего сигнала
        device.last_seen = timezone.now()
        device.save(update_fields=['last_seen'])

        # Сохраняем данные
        data = request.data.copy()
        data['plant'] = device.plant.id

        serializer = SensorDataSerializer(data=data)
        if serializer.is_valid():
            sensor_data = serializer.save()

            # ===== ПРОВЕРКА КРИТИЧЕСКИХ ЗНАЧЕНИЙ =====
            plant = device.plant
            humidity = sensor_data.humidity
            temperature = sensor_data.temperature

            vk_id = plant.owner.vk_id if plant.owner else None

            if vk_id:
                # 1. Влажность ниже минимальной
                if humidity < plant.min_humidity:
                    message = (
                        f"💧 ВНИМАНИЕ! Растение '{plant.name}'\n"
                        f"Влажность: {humidity}% (ниже порога {plant.min_humidity}%)\n"
                        f"Срочно нужен полив!"
                    )
                    vk_send_message(vk_id, message)

                # 2. Температура выше 30°C
                if temperature and temperature > 30:
                    message = (
                        f"🔥 ВНИМАНИЕ! Растение '{plant.name}'\n"
                        f"Температура: {temperature}°C (выше 30°C)\n"
                        f"Проверьте условия!"
                    )
                    vk_send_message(vk_id, message)

            return Response({"ok": True}, status=201)

        return Response({"error": serializer.errors}, status=400)

# Отправка уведомлении каждые 30 минут, что-бы не было спама
# from datetime import timedelta
# from django.utils import timezone
#
#
# class SensorDataAPIView(APIView):
#     def post(self, request):
#         device_id = request.data.get('device')
#
#         try:
#             device = Device.objects.get(device_id=device_id, is_active=True)
#         except Device.DoesNotExist:
#             return Response({"error": f"Device {device_id} not found"}, status=404)
#
#         if not device.plant:
#             return Response({"error": "Device not linked to any plant"}, status=400)
#
#         device.last_seen = timezone.now()
#         device.save(update_fields=['last_seen'])
#
#         data = request.data.copy()
#         data['plant'] = device.plant.id
#
#         serializer = SensorDataSerializer(data=data)
#         if serializer.is_valid():
#             sensor_data = serializer.save()
#
#             plant = device.plant
#             humidity = sensor_data.humidity
#             temperature = sensor_data.temperature
#             vk_id = plant.owner.vk_id if plant.owner else None
#
#             if vk_id:
#                 # ===== ПРОВЕРКА НА СПАМ (30 минут) =====
#                 now = timezone.now()
#                 spam_window = now - timedelta(minutes=30)
#
#                 # Последние критические уведомления
#                 recent_alerts = SensorData.objects.filter(
#                     plant=plant,
#                     created_at__gte=spam_window,
#                 ).exclude(id=sensor_data.id)
#
#                 # Проверяем, было ли уже уведомление о влажности
#                 humidity_alert_sent = any(
#                     d.humidity < plant.min_humidity for d in recent_alerts
#                 )
#
#                 # Проверяем, было ли уже уведомление о температуре
#                 temp_alert_sent = any(
#                     d.temperature and d.temperature > 30 for d in recent_alerts
#                 )
#
#                 # 1. Влажность ниже минимальной
#                 if humidity < plant.min_humidity and not humidity_alert_sent:
#                     message = (
#                         f"💧 ВНИМАНИЕ! Растение '{plant.name}'\n"
#                         f"Влажность: {humidity}% (ниже порога {plant.min_humidity}%)\n"
#                         f"Срочно нужен полив!"
#                     )
#                     vk_send_message(vk_id, message)
#
#                 # 2. Температура выше 30°C
#                 if temperature and temperature > 30 and not temp_alert_sent:
#                     message = (
#                         f"🔥 ВНИМАНИЕ! Растение '{plant.name}'\n"
#                         f"Температура: {temperature}°C (выше 30°C)\n"
#                         f"Проверьте условия!"
#                     )
#                     vk_send_message(vk_id, message)
#
#             return Response({"ok": True}, status=201)
#
#         return Response({"error": serializer.errors}, status=400)


class DeviceStateAPIView(APIView):
    """
    API для управления состоянием устройства.
    GET: возвращает текущее состояние (automatic, pump, light).
    POST: обновляет состояние, сбрасывает pump/light при смене режима.
    """
    def get(self, request):
        # Берём самую свежую запись
        state = DeviceState.objects.order_by('-updated_at').first()

        # Если записей нет — создаём
        if state is None:
            state = DeviceState.objects.create(
                automatic=True, pump=False, light=False
            )

        return Response({
            "automatic": state.automatic,
            "pump": state.pump,
            "light": state.light,
        })

    def post(self, request):
        """Обновление состояния через кнопки"""
        state = DeviceState.objects.order_by('-updated_at').first()
        if state is None:
            state = DeviceState.objects.create(
                automatic=True, pump=False, light=False
            )

        # ===== ОБРАБОТКА ПЕРЕКЛЮЧЕНИЯ РЕЖИМА =====
        if 'automatic' in request.data:
            new_automatic = request.data['automatic']

            # Если режим изменился — сбросить pump и light
            if new_automatic != state.automatic:
                state.pump = False
                state.light = False
                print(f"Mode switched: {state.automatic} → {new_automatic}")
                print("Reset pump=False, light=False")

            state.automatic = new_automatic

        # ===== ОБНОВЛЕНИЕ ОСТАЛЬНЫХ ПОЛЕЙ =====
        if 'pump' in request.data:
            state.pump = request.data['pump']
        if 'light' in request.data:
            state.light = request.data['light']

        state.save()
        return Response({"ok": True})

def control(request):
    """
    Обновляет состояние устройства (кнопки на сайте).
    Если режим изменился — сбрасывает pump и light в False.
    Ожидает JSON:
        {"automatic": true, "pump": false, "light": false}
    Возвращает:
        200: {"ok": true}
    """
    state = DeviceState.objects.order_by('-updated_at').first()
    if state is None:
        state = DeviceState.objects.create(automatic=True, pump=False, light=False)

    camera_state, _ = CameraState.objects.get_or_create(id=1)

    return render(request, 'control.html', {
        'title': 'Управление',
        'state': state,
        'camera': camera_state,
    })



def get_camera_index(name="USB 2.0 Camera"):
    """Возвращает индекс камеры по имени"""
    ctypes.windll.ole32.CoInitialize(None)
    graph = FilterGraph()
    devices = graph.get_input_devices()
    ctypes.windll.ole32.CoUninitialize()

    if name in devices:
        return devices.index(name)
    return 0

def gen_frames():
    """Генератор кадров с камеры"""
    camera_index = get_camera_index("USB 2.0 Camera")
    print(f"DEBUG: camera_index = {camera_index}")

    camera = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)

    if not camera.isOpened():
        print("Не удалось открыть камеру")
        return

    while True:
        success, frame = camera.read()
        if not success:
            break
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


def video_feed(request):
    """Поток видео с USB-камеры (только если камера включена)"""
    camera_state, _ = CameraState.objects.get_or_create(id=1)

    if not camera_state.is_on:
        return HttpResponse("Camera is off", status=204)

    return StreamingHttpResponse(
        gen_frames(),
        content_type='multipart/x-mixed-replace; boundary=frame'
    )


class CameraStateAPIView(APIView):
    """API для управления камерой"""

    def get(self, request):
        state, _ = CameraState.objects.get_or_create(id=1)
        return Response({
            "is_on": state.is_on,
        })

    def post(self, request):
        state, _ = CameraState.objects.get_or_create(id=1)

        if 'is_on' in request.data:
            state.is_on = request.data['is_on']
            state.save()

        return Response({"ok": True, "is_on": state.is_on})


class WateringLogAPIView(APIView):
    """API для записи логов полива"""
    def post(self, request):
        device_id = request.data.get('device')  # ← принимаем device

        try:
            device = Device.objects.get(device_id=device_id, is_active=True)
        except Device.DoesNotExist:
            return Response({"error": f"Device {device_id} not found"}, status=404)

        if not device.plant:
            return Response({"error": "Device not linked to plant"}, status=400)

        # Подставляем plant_id из устройства
        data = request.data.copy()
        data['plant'] = device.plant.id

        serializer = WateringLogSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"ok": True}, status=201)
        return Response({"error": serializer.errors}, status=400)



class PlantListView(LoginRequiredMixin, ListView):
    """
    Список растений с последними показаниями датчиков.
    - Обычный пользователь видит только свои растения.
    - Администратор и модератор видят все растения.
    """
    model = Plant
    template_name = 'plants_list.html'
    context_object_name = 'plants_data'
    paginate_by = 3

    def get_queryset(self):
        queryset = super().get_queryset()

        # Админ и модератор видят все растения
        if self.request.user.role in ('admin', 'moderator'):
            return queryset

        # Обычный пользователь видит только свои
        return queryset.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        """Добавляем последние показания датчиков для каждого растения"""
        context = super().get_context_data(**kwargs)

        plants_data = []
        for plant in context['plants_data']:
            latest = SensorData.objects.filter(plant=plant).order_by('-created_at').first()
            plants_data.append({
                'plant': plant,
                'latest': latest,
            })

        context['plants_data'] = plants_data
        return context

def device_state_page(request):
    """Страница состояния устройства"""
    state = DeviceState.objects.order_by('-updated_at').first()
    if state is None:
        state = DeviceState.objects.create(automatic=True, pump=False, light=False, camera=False)

    camera_state, _ = CameraState.objects.get_or_create(id=1)

    return render(request, 'device_state.html', {
        'title': 'Состояние устройства',
        'state': state,
        'camera': camera_state,
    })




class PlantCreateView(LoginRequiredMixin, CreateView):
    """
    Создание растения.
    - Доступно только авторизованным пользователям.
    - Владелец назначается автоматически (текущий пользователь).
    """
    model = Plant
    form_class = PlantForm
    template_name = 'plant_add.html'
    success_url = reverse_lazy('plants:plants_list')

    def form_valid(self, form):
        # Назначаем владельца — текущего пользователя
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['title'] = 'Добавить растение'
        return context_data


class PlantUpdateView(LoginRequiredMixin, UpdateView):
    """
    Редактирование растения.
    Доступно только владельцу или администратору/модератору.
    """
    model = Plant
    form_class = PlantForm
    template_name = 'plant_edit.html'
    success_url = reverse_lazy('plants:plants_list')
    pk_url_kwarg = 'plant_id'

    def get_object(self, queryset=None):
        plant = super().get_object(queryset)

        # Проверяем права доступа
        if plant.owner != self.request.user and self.request.user.role not in ('admin', 'moderator'):
            raise PermissionDenied("Вы не можете редактировать это растение")

        return plant

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        plant = self.get_object()
        context_data['title'] = f'Редактировать: {plant.name}'
        return context_data


class PlantDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Удаление растения.
    Доступно только администратору и модератору.
    """
    model = Plant
    template_name = 'plant_delete.html'
    success_url = reverse_lazy('plants:plants_list')
    pk_url_kwarg = 'plant_id'

    def test_func(self):
        # Разрешаем удаление только админу и модератору
        return self.request.user.role in ('admin', 'moderator')

    def handle_no_permission(self):
        # Если нет прав — показываем 403
        raise PermissionDenied("У вас нет прав для удаления растения")

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        plant = self.get_object()
        context_data['title'] = f'Удалить: {plant.name}'
        return context_data