
from collections import Counter, defaultdict
import json
from django.shortcuts import render, redirect
from networkx import draw_networkx
from .models import Movimiento
import uuid
import matplotlib.pyplot as plt
import networkx as nx
import io
import base64
from .models import Movimiento
import random 
import networkx as nx
from bokeh.embed import components
from bokeh.plotting import figure, from_networkx, show
from bokeh.models import GraphRenderer, StaticLayoutProvider
from bokeh.io import show


def index(request):
    estado_inicial = "1,2,3,4,5,0,6,7,8,9,10"
    estado_list = [int(x) for x in estado_inicial.split(',')]

    try:
        ultimo_movimiento = Movimiento.objects.latest('fecha_hora')
        estado_list = [int(x) for x in ultimo_movimiento.trayectoria.split(',')]
        movimientos = ultimo_movimiento.movimiento
    except Movimiento.DoesNotExist:
        movimientos = 0

    return render(request, 'game/index.html', {'state': estado_list, 'moves': movimientos})

def move(request, index):
    try:
        ultimo_movimiento = Movimiento.objects.latest('fecha_hora')
        estado_list = [int(x) for x in ultimo_movimiento.trayectoria.split(',')]
        movimientos = ultimo_movimiento.movimiento
        intento = ultimo_movimiento.intento
    except Movimiento.DoesNotExist:
        estado_list = [1, 2, 3, 4, 5, 0, 6, 7, 8, 9, 10]
        movimientos = 0
        intento = 1

    zero_index = estado_list.index(0)
    
    if abs(zero_index - index) == 1 or abs(zero_index - index) == 5:
        estado_list[zero_index], estado_list[index] = estado_list[index], estado_list[zero_index]
        movimientos += 1

        nuevo_movimiento = Movimiento(
            registro=random.randint(1, 1000000),  
            uid=str(uuid.uuid4())[:15],  
            intento=intento,
            movimiento=movimientos,
            trayectoria=','.join(map(str, estado_list))
        )
        nuevo_movimiento.save()

    
    context = grafo_movimientos(request)

    return render(request, 'game/index.html', context)

def grafo_movimientos(request):
    movimientos = Movimiento.objects.all().values('movimiento', 'trayectoria')
    print(movimientos)

    datos = {'nodes': [], 'links': []}
    seen_nodes = {}

    for item in movimientos:
        print(f"items del movimientos: {item}")
        tray = item['trayectoria']
        mov = item['movimiento']
        node_id = f"{tray}_{mov}"
        if node_id not in seen_nodes:
            datos['nodes'].append({'id': node_id, 'trayectoria': tray})
            seen_nodes[node_id] = tray 

        movimiento_anterior = mov - 1
        if movimiento_anterior > 0:
            tray_anterior = next((m['trayectoria'] for m in movimientos if m['movimiento'] == movimiento_anterior), None)
            if tray_anterior:
                node_id_anterior = f"{tray_anterior}_{movimiento_anterior}"
                if node_id_anterior in seen_nodes:
                    datos['links'].append({'source': node_id_anterior, 'target': node_id})

        if not any(m['movimiento'] == mov + 1 for m in movimientos):
            datos['links'].append({'source': node_id, 'target': node_id})

    print(datos)

    context = {
        'datos': json.dumps(datos)
    }
    return render(request, 'game/index.html', context)
    

