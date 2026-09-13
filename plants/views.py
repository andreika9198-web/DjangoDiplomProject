from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import cv2
from django.http import StreamingHttpResponse, HttpResponse

from .models import SensorData, DeviceState, CameraState
from .serializers import SensorDataSerializer, CameraStateSerializer

def index(request):
    return render(request, 'index.html', {'title': 'Главная'})

class SensorDataAPIView(APIView):
    def post(self, request):
        serializer = SensorDataSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            # Возвращаем КРОШЕЧНЫЙ ответ (всего 15 байт)
            return Response({"ok": True}, status=status.HTTP_201_CREATED)
        return Response({"error": "invalid"}, status=status.HTTP_400_BAD_REQUEST)


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