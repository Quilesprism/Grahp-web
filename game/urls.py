# game/urls.py
from django.urls import path
from .views import index, move, grafo_movimientos

urlpatterns = [
    path('', index, name='index'),
    path('move/<int:index>/', move, name='move'),
    path('grafo_movimientos/', grafo_movimientos, name='grafo_movimientos'),
]


