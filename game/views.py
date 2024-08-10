
from django.shortcuts import render, redirect
from .models import Movimiento
import uuid
import matplotlib.pyplot as plt
import networkx as nx
import io
import base64
from django.http import HttpResponse
from .models import Movimiento
import random 
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
    
    return redirect('index')

def grafo_movimientos(request):
    movimientos = Movimiento.objects.all()
    
   
    G = nx.DiGraph()
    
    
    for movimiento in movimientos:
        trayectoria = movimiento.trayectoria.split(',')
        G.add_node(tuple(trayectoria))
        
        if movimiento.movimiento > 1:
            anterior = Movimiento.objects.filter(movimiento=movimiento.movimiento - 1, intento=movimiento.intento).first()
            if anterior:
                trayectoria_anterior = anterior.trayectoria.split(',')
                G.add_edge(tuple(trayectoria_anterior), tuple(trayectoria), label=movimiento.movimiento)
    
 
    pos = nx.spring_layout(G)
    plt.figure(figsize=(10, 8))
    nx.draw(G, pos, with_labels=True, node_size=5000, node_color='lightblue', font_size=8, font_weight='bold')
    labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
    
 
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    
  
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    
    return render(request, 'game/index.html', {'image': image_base64})