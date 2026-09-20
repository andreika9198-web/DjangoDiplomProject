from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response

from django.contrib.auth.mixins import LoginRequiredMixin
import cv2
from django.http import StreamingHttpResponse, HttpResponse
from django.views.generic import UpdateView, ListView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from .forms import PlantForm

from .models import SensorData, DeviceState, CameraState, Plant
from .serializers import SensorDataSerializer, CameraStateSerializer, WateringLogSerializer
from devices.models import Device

def index(request):
    return render(request, 'index.html', {'title': 'Главная'})


class SensorDataAPIView(APIView):
    def post(self, request):
        device_id = request.data.get('device')  # ESP32 присылает свой device_id

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
            serializer.save()
            return Response({"ok": True}, status=201)
        return Response({"error": serializer.errors}, status=400)


class DeviceStateAPIView(APIView):
    def get(self, request):
        # Берём самую свежую запись (любой ID)
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
            state = DeviceState.objects.create(automatic=True, pump=False, light=False)

        # Обновляем переданные поля
        if 'automatic' in request.data:
            state.automatic = request.data['automatic']
        if 'pump' in request.data:
            state.pump = request.data['pump']
        if 'light' in request.data:
            state.light = request.data['light']

        state.save()
        return Response({"ok": True})

def control(request):
    state = DeviceState.objects.order_by('-updated_at').first()
    if state is None:
        state = DeviceState.objects.create(automatic=True, pump=False, light=False)

    camera_state, _ = CameraState.objects.get_or_create(id=1)

    return render(request, 'control.html', {
        'title': 'Управление',
        'state': state,
        'camera': camera_state,
    })

def gen_frames():
    """Генератор кадров с камеры"""
    camera = cv2.VideoCapture(1)  # 0 — первая USB-камера
    if not camera.isOpened():
        print("Не удалось открыть камеру")
        return

    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            # Кодируем кадр в JPEG
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


# plants/views.py
class PlantListView(LoginRequiredMixin, ListView):
    """
    Список растений с последними показаниями датчиков.
    - Обычный пользователь видит только свои растения.
    - Администратор и модератор видят все растения.
    """
    model = Plant
    template_name = 'plants_list.html'
    context_object_name = 'plants_data'  # 👈 возвращаем имя как в шаблоне
    paginate_by = 6

    def get_queryset(self):
        queryset = super().get_queryset()

        # Админ и модератор видят все растения
        if self.request.user.role in ('admin', 'moderator'):
            return queryset

        # Обычный пользователь видит только свои
        return queryset.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Формируем plants_data с последними показаниями
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


from django.shortcuts import render, redirect
from .forms import PlantForm


def plant_add(request):
    """Страница добавления растения"""
    if request.method == 'POST':
        form = PlantForm(request.POST)
        if form.is_valid():
            plant = form.save(commit=False)
            plant.owner = request.user  # ← назначаем владельца
            plant.save()
            return redirect('plants:plants_list')
    else:
        form = PlantForm()

    return render(request, 'plant_add.html', {
        'title': 'Добавить растение',
        'form': form,
    })


class PlantUpdateView(LoginRequiredMixin, UpdateView):
    """
    Редактирование растения.
    - Доступно только владельцу или администратору/модератору.
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


def plant_delete(request, plant_id):
    """Удаление растения"""
    plant = get_object_or_404(Plant, id=plant_id)

    if request.method == 'POST':
        plant.delete()
        return redirect('plants:plants_list')

    return render(request, 'plant_delete.html', {
        'title': f'Удалить: {plant.name}',
        'plant': plant,
    })