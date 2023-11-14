from mesa.model import Model
from mesa.agent import Agent
from mesa.space import MultiGrid
from mesa.time import SimultaneousActivation
from mesa.datacollection import DataCollector

import numpy as np


class Celda(Agent):
    def __init__(self, unique_id, model, suciedad: bool = False):
        super().__init__(unique_id, model)
        self.sucia = suciedad


class Mueble(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

class Cargador(Agent):
    def __init__(self, unique_id, model, agente: Agent = None):
        super().__init__(unique_id, model)
        self.cargado = 0
        self.ocupado = False

    def step(self):
        # Check for the presence of RobotLimpieza on the same position
        agents_in_cell = self.model.grid.get_cell_list_contents([self.pos])

        if self.ocupado == False:
            for agent in agents_in_cell:
                if isinstance(agent, RobotLimpieza):
                    self.ocupado = True  # Set ocupado to True if a RobotLimpieza is present
                    break
        elif self.ocupado == True:
            for agent in agents_in_cell:
                if not isinstance(agent, RobotLimpieza):
                    self.ocupado = False
                else:
                    self.ocupado = True
        
        


class RobotLimpieza(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.sig_pos = None
        self.movimientos = 0
        self.carga = 100
        self.limpiado = 0
        self.cargando = False

    def limpiar_una_celda(self, lista_de_celdas_sucias):
        celda_a_limpiar = self.random.choice(lista_de_celdas_sucias)
        celda_a_limpiar.sucia = False
        self.sig_pos = celda_a_limpiar.pos
        self.limpiado += 1

    
    def set_cargador_ocupado(self):
        # Get all agents in the current cell
        agents_in_cell = self.model.grid.get_cell_list_contents([self.pos])

        # Find the Cargador agent in the cell
        for agent in agents_in_cell:
            print(str(agent))
            if isinstance(agent, Cargador):
                agent.ocupado = True
                break

            
    def set_cargador_desocupado(self):
        # Get all agents in the current cell
        agents_in_cell = self.model.grid.get_cell_list_contents([self.pos])

        # Find the Cargador agent in the cell
        for agent in agents_in_cell:
            if isinstance(agent, Cargador):
                agent.ocupado = False
                break

    
    def seleccionar_nueva_pos(self, lista_de_vecinos):
        self.sig_pos = self.random.choice(lista_de_vecinos).pos

    def iracargador(self, lista_de_vecinos):
        robots = get_sig_position(self.model)
        
        celdas_no_disponibles = list()
        for robot in robots:
            if self.sig_pos == robot["sig_pos"] and self.unique_id != robot["unique_id"]:
                celdas_no_disponibles.append(robot["sig_pos"])
        
        vecinos = self.model.grid.get_neighbors(
                        self.pos, moore=True, include_center=False)
        vecinos_disponibles = list()
        
        for vecino in vecinos:
            if not isinstance(vecino, Mueble) or (isinstance(vecino, RobotLimpieza) and vecino.sig_pos not in celdas_no_disponibles):
                vecinos_disponibles.append(vecino)
        
        lista_de_vecinos = vecinos_disponibles

        if self.pos[0] >= 4 and self.pos[1] >= 1:
            print("Esta bajando")
            for celda in lista_de_vecinos:
                
                if celda.pos[0] <= self.pos[0] and celda.pos[0] >= 3:
                    if celda.pos[1] <= self.pos[1] or celda.pos[1] >= 0:
                        self.sig_pos = celda.pos
                        return
                elif celda.pos[1] <= self.pos[1] and celda.pos[1] >= 0:
                    if celda.pos[0] <= self.pos[0] or celda.pos[0] >= 3:
                        self.sig_pos = celda.pos
                        return
                else:
                    self.sig_pos = self.pos
                
        elif self.pos[0] < 4 and self.pos[1] > 1:
            print("Esta a la izquierda")
            for celda in lista_de_vecinos:
                if celda.pos[1] < self.pos[1]:
                    self.sig_pos = celda.pos
                    return
                elif celda.pos[1] <= self.pos[1]:
                    self.sig_pos = celda.pos
                    return
                else:
                    self.sig_pos = self.pos
                
        elif self.pos[1] < 1 and self.pos[0] > 4:
            print("Esta abajo")
            for celda in lista_de_vecinos:
                if celda.pos[0] < self.pos[0]:
                    self.sig_pos = celda.pos
                    return
                elif celda.pos[0] <= self.pos[0]:
                    self.sig_pos = celda.pos
                    return
                else:
                    self.sig_pos = self.pos
        else:
            print("Encontro un cargador")
            for celda in lista_de_vecinos:
                if isinstance(self.model.grid.__getitem__((celda.pos[0], celda.pos[1]))[0], Cargador):
                    if self.model.grid.__getitem__((celda.pos[0], celda.pos[1]))[0].ocupado == False:
                        self.set_cargador_ocupado()
                        print("Encontro Cargador Libre")
                        self.sig_pos = celda.pos
                        return
                    else:
                        print("Encontro Cargador ocupado")

                        self.sig_pos = self.pos
                else:
                    self.sig_pos = self.pos
                
                    
    
    @staticmethod
    def buscar_celdas_sucia(lista_de_vecinos):

        celdas_sucias = list()
        for vecino in lista_de_vecinos:
            if isinstance(vecino, Celda) and vecino.sucia:
                celdas_sucias.append(vecino)
        return celdas_sucias

   
    
    def step(self):

        
        vecinos = self.model.grid.get_neighbors(
            self.pos, moore=True, include_center=False)

        vecinos_disponibles = list()
        for vecino in vecinos:
            if not isinstance(vecino, (Mueble, RobotLimpieza)):
                vecinos_disponibles.append(vecino)

        celdas_sucias = self.buscar_celdas_sucia(vecinos_disponibles)


        if len(celdas_sucias) == 0 and self.carga >= 40 and self.cargando == False:

            self.seleccionar_nueva_pos(vecinos_disponibles)
        elif self.carga < 40:
            self.cargando = True

            self.iracargador(vecinos_disponibles)
        elif self.cargando == False:
            self.limpiar_una_celda(celdas_sucias)




        if isinstance(self.model.grid.__getitem__((self.pos[0], self.pos[1]))[0], Cargador) and self.cargando == True:
            if self.carga < 90:
                self.set_cargador_ocupado()

                self.carga += 25
                if self.carga > 100:
                    self.carga = 100
                self.sig_pos = self.pos
                return
            else: 
                self.set_cargador_desocupado()
                self.cargando = False
            return

    def advance(self):
        robots = get_sig_position(self.model)
        
        celdas_no_disponibles = list()
        cambio = False
        for robot in robots:
            if self.sig_pos == robot["sig_pos"] and self.unique_id != robot["unique_id"]:
                celdas_no_disponibles.append(robot["sig_pos"])
                cambio = True
        
        print(str(self.unique_id))

        vecinos = self.model.grid.get_neighbors(
                        self.pos, moore=True, include_center=False)
        vecinos_disponibles = list()
        
        for vecino in vecinos:
            if not isinstance(vecino, Mueble) or (isinstance(vecino, RobotLimpieza) and vecino.sig_pos not in celdas_no_disponibles):
                vecinos_disponibles.append(vecino)
        

        if cambio and self.carga < 40:
            self.iracargador(vecinos_disponibles)
            self.cargando = True

        if cambio and self.cargando == False:
            self.seleccionar_nueva_pos(vecinos_disponibles)
        
        

        if isinstance(self.model.grid.__getitem__((self.pos[0], self.pos[1]))[0], Cargador) and self.cargando == True:
            if self.carga < 90:
                self.set_cargador_ocupado()
                self.carga += 25
                if self.carga > 100:
                    self.carga = 100
                self.model.grid.move_agent(self, self.pos)
                return
            else: 
                self.set_cargador_desocupado
                self.cargando = False
            return

        if self.pos != self.sig_pos:
            self.movimientos += 1

        if self.carga > 0:
            self.carga -= 1
            self.model.grid.move_agent(self, self.sig_pos)



            


class Habitacion(Model):
    def __init__(self, M: int, N: int,
                 num_agentes: int = 4,
                 porc_celdas_sucias: float = 0.6,
                 porc_muebles: float = 0.1,
                 modo_pos_inicial: str = 'Fija',

                 ):

        self.num_agentes = num_agentes
        self.porc_celdas_sucias = porc_celdas_sucias
        self.porc_muebles = porc_muebles
        self.lista_posiciones = []


        self.grid = MultiGrid(M, N, False)
        self.schedule = SimultaneousActivation(self)

        
        posiciones_disponibles = [pos for _, pos in self.grid.coord_iter()]

        # Posicionamiento de cargadores

        posiciones_cargadores = [(0,0),(1,0),(2,0),(3,0)]
        for id, pos in enumerate(posiciones_cargadores):
            cargador = Cargador(int(f"{num_agentes}0{id}") + 1, self)
            self.grid.place_agent(cargador, pos)
            self.schedule.add(cargador)
            posiciones_disponibles.remove(pos)

        # Posicionamiento de muebles
        num_muebles = int(M * N * porc_muebles)
        posiciones_muebles = self.random.sample(posiciones_disponibles, k=num_muebles)

        for id, pos in enumerate(posiciones_muebles):
            mueble = Mueble(int(f"{num_agentes}0{id}") + 1, self)
            self.grid.place_agent(mueble, pos)
            posiciones_disponibles.remove(pos)

       


        # Posicionamiento de celdas sucias
        self.num_celdas_sucias = int(M * N * porc_celdas_sucias)
        posiciones_celdas_sucias = self.random.sample(
            posiciones_disponibles, k=self.num_celdas_sucias)

        for id, pos in enumerate(posiciones_disponibles):
            suciedad = pos in posiciones_celdas_sucias
            celda = Celda(int(f"{num_agentes}{id}") + 1, self, suciedad)
            self.grid.place_agent(celda, pos)

        # Posicionamiento de agentes robot
        if modo_pos_inicial == 'Aleatoria':
            pos_inicial_robots = self.random.sample(posiciones_disponibles, k=num_agentes)
        else:  # 'Fija'
            pos_inicial_robots = [(1, 1)] * num_agentes


        for id in range(num_agentes):
            robot = RobotLimpieza(id, self)
            self.grid.place_agent(robot, pos_inicial_robots[id])
            self.lista_posiciones.append(robot)
            self.schedule.add(robot)

        self.datacollector = DataCollector(
            model_reporters={"Grid": get_grid, "Cargas0": get_cargas0, "Cargas1": get_cargas1, "Cargas2": get_cargas2, "Cargas3": get_cargas3,
                             "CeldasSucias": get_sucias, "Limpiados": get_limpiados},
        )

    def step(self):
        self.datacollector.collect(self)

        self.schedule.step()

    def todoLimpio(self):
        for (content, x, y) in self.grid.coord_iter():
            for obj in content:
                if isinstance(obj, Celda) and obj.sucia:
                    return False
        return True


def get_grid(model: Model) -> np.ndarray:
    """
    Método para la obtención de la grid y representarla en un notebook
    :param model: Modelo (entorno)
    :return: grid
    """
    grid = np.zeros((model.grid.width, model.grid.height))
    for cell in model.grid.coord_iter():
        cell_content, pos = cell
        x, y = pos
        for obj in cell_content:
            if isinstance(obj, RobotLimpieza):
                grid[x][y] = 2
            elif isinstance(obj, Celda):
                grid[x][y] = int(obj.sucia)
    return grid

def get_cargas0(model: Model):
    for agent in model.schedule.agents:
        if isinstance(agent, RobotLimpieza) and agent.unique_id == 0:
            return agent.carga
    
def get_cargas1(model: Model):
    for agent in model.schedule.agents:
        if isinstance(agent, RobotLimpieza) and agent.unique_id == 1:
            return agent.carga
    

def get_cargas2(model: Model):
    for agent in model.schedule.agents:
        if isinstance(agent, RobotLimpieza) and agent.unique_id == 2:
            return agent.carga    
    

def get_cargas3(model: Model):
    for agent in model.schedule.agents:
        if isinstance(agent, RobotLimpieza) and agent.unique_id == 3:
            return agent.carga
    


def get_limpiados(model: Model):
    limpiado = list()
    for agent in model.schedule.agents:
        if isinstance(agent, RobotLimpieza):
            limpiado.append({agent.unique_id, agent.limpiado})
    
    return limpiado


def get_sucias(model: Model) -> int:
    """
    Método para determinar el número total de celdas sucias
    :param model: Modelo Mesa
    :return: número de celdas sucias
    """
    sum_sucias = 0
    for cell in model.grid.coord_iter():
        cell_content, pos = cell
        for obj in cell_content:
            if isinstance(obj, Celda) and obj.sucia:
                sum_sucias += 1
    return sum_sucias / model.num_celdas_sucias


def get_movimientos(agent: Agent) -> dict:
    if isinstance(agent, RobotLimpieza):
        return {agent.unique_id: agent.movimientos}
    # else:
    #    return 0

def get_sig_position(model: Model):
    posiciones = list()
    for agent in model.schedule.agents:
        if isinstance(agent, RobotLimpieza):
            posiciones.append({"unique_id": agent.unique_id, "sig_pos" : agent.sig_pos})
    
    return posiciones


def get_positions(model: Model):
    posiciones = list()
    for agent in model.schedule.agents:
        if isinstance(agent, RobotLimpieza):
            posiciones.append({"unique_id": agent.unique_id, "pos" : agent.pos})
    
    return posiciones