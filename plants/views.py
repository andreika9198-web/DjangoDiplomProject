from django.shortcuts import render

from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import SensorData, DeviceState
from .serializers import SensorDataSerializer

def index(request):
    return HttpResponse("Привет, мир! Это умный полив.")

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