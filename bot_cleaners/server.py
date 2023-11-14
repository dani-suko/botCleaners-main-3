import random

import mesa

from .model import Habitacion, RobotLimpieza, Celda, Mueble, Cargador

MAX_NUMBER_ROBOTS = 4


def agent_portrayal(agent):
    if isinstance(agent, RobotLimpieza):
        return {"Shape": "circle", "Filled": "false", "Color": "black", "Layer": 1, "r": 1.0,
                "text": f"{agent.carga}", "text_color": "yellow"}
    elif isinstance(agent, Mueble):
        return {"Shape": "rect", "Filled": "true", "Color": "white", "Layer": 0,
                "w": 0.9, "h": 0.9, "text_color": "Black", "text": "🪑"}
    elif isinstance(agent, Celda):
        portrayal = {"Shape": "rect", "Filled": "true", "Layer": 0, "w": 0.9, "h": 0.9, "text_color": "Black"}
        if agent.sucia:
            portrayal["Color"] = "white"
            portrayal["text"] = "🦠"
        else:
            portrayal["Color"] = "white"
            portrayal["text"] = ""
        return portrayal
    elif isinstance(agent, Cargador):
        return {"Shape": "rect", "Filled": "true", "Color": "white", "Layer": 0,
                "w": 0.9, "h": 0.9, "text_color": "Black", "text": "🔋"}


grid = mesa.visualization.CanvasGrid(
    agent_portrayal, 20, 20, 400, 400)

chart_celdas = mesa.visualization.ChartModule(
    [{"Label": "CeldasSucias", "Color": '#36A2EB', "label": "Celdas Sucias"}],
    50, 200,
    data_collector_name="datacollector"
)

chart_cargas = mesa.visualization.ChartModule(
    [{"Label": "Cargas0", "Color": '#f44336', "label" : "Carga Robot 1"},
     {"Label": "Cargas1", "Color": '#36A2EB', "label" : "Carga Robot 2"},
     {"Label": "Cargas2", "Color": '#6aa84f', "label" : "Carga Robot 3"},
     {"Label": "Cargas3", "Color": '#f1c232', "label" : "Carga Robot 4"}],
    50, 200,
    data_collector_name="datacollector"
)



model_params = {
    "porc_celdas_sucias": mesa.visualization.Slider(
        "Porcentaje de Celdas Sucias",
        0.3,
        0.0,
        0.75,
        0.05,
        description="Selecciona el porcentaje de celdas sucias",
    ),
    "porc_muebles": mesa.visualization.Slider(
        "Porcentaje de Muebles",
        0.1,
        0.0,
        0.25,
        0.01,
        description="Selecciona el porcentaje de muebles",
    ),
    "modo_pos_inicial": mesa.visualization.Choice(
        "Posición Inicial de los Robots",
        "Aleatoria",
        ["Fija", "Aleatoria"],
        "Selecciona la forma se posicionan los robots"
    ),
    "M": 20,
    "N": 20,
}

server = mesa.visualization.ModularServer(
    Habitacion, [grid, chart_cargas],
    "botCleaner", model_params, 8521
)
