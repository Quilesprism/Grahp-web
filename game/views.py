
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
    
    return redirect('index')

def grafo_movimientos(request):
    movimientos = Movimiento.objects.all()

    grafo = defaultdict(int)

    for mov in movimientos:
        trayecto = mov.trayectoria.split(',')
        for i in range(len(trayecto) - 1):
            origen = trayecto[i]
            destino = trayecto[i + 1]
            grafo[(origen, destino)] += 1

    # Preparar los nodos y enlaces para Bokeh
    G = nx.Graph()
    for (origen, destino), peso in grafo.items():
        G.add_edge(origen, destino, weight=peso)

    plot = figure(title="Grafo de Movimientos", x_range=(-1.1, 1.1), y_range=(-1.1, 1.1),
                  tools="", toolbar_location=None)

    graph_renderer = from_networkx(G, nx.spring_layout, scale=2, center=(0, 0))

    plot.renderers.append(graph_renderer)

    script, div = components(plot)
    
    return render(request, 'game/index.html', {'script': script, 'div': div})

def generar_grafo(request):
    # Obtener todos los movimientos desde la BD
    movimientos = Movimiento.objects.all()
    
    # Contar la frecuencia de cada trayectoria
    trayectorias = [mov.trayectoria for mov in movimientos]
    frecuencia_trayectorias = Counter(trayectorias)
    
    # Crear un grafo dirigido
    G = nx.DiGraph()

    for mov in movimientos:
        trayecto = mov.trayectoria.split(',')
        for i in range(len(trayecto) - 1):
            origen = trayecto[i]
            destino = trayecto[i + 1]
            if G.has_edge(origen, destino):
                G[origen][destino]['weight'] += 1
            else:
                G.add_edge(origen, destino, weight=1)
    
    # Ajustar los tamaños de los nodos y aristas en función de la frecuencia
    edge_widths = [G[u][v]['weight'] for u, v in G.edges()]
    
    plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_size=700, node_color='skyblue', 
            font_size=10, font_weight='bold', edge_color=edge_widths, 
            edge_cmap=plt.cm.Blues, width=edge_widths)

    # Guardar la imagen en un buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    
    # Convertir la imagen a base64 para enviar al template
    graph_image = base64.b64encode(image_png).decode('utf-8')
    
    return render(request, 'game/index.html', {'graph_image': graph_image})