import networkx as nx
#import matplotlib.pyplot as plt
import math

INITIAL_PHEROMONE_AMOUNT = 0

class CVRPCase:
    def __init__(self, name, comment, graph, capacity, depot):
        self.name = name
        self.comment = comment
        # graf reprezentujący klientów z kosztami przemieszczenia się między nimi
        self.graph = graph
        self.capacity = capacity  # maksymalna ładowność pojazdu
        self.depot = depot  # numer wierzchołka reprezentującego magazyn
        # zapotrzebowanie na towar w poszczególnych wierzchołkach
        self.demands = nx.get_node_attributes(graph, 'demand')

    def __str__(self):
        return "Case name: " + self.name + "\nDescription: " + self.comment + "\nCapacity: " + str(self.capacity)


class Node:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y


def load_case(path):
    name = ""
    comment = ""
    graph = nx.Graph()
    capacity = -1
    depot = -1
    nodes = []
    node_section = False
    demand_section = False
    depot_section = False
    with open(path, "r") as file:
        for line in file:
            line = line.strip()
            if node_section:
                if line.startswith("DEMAND_SECTION"):
                    node_section = False
                    demand_section = True
                else:
                    node = line.split()
                    # node[0] - id
                    # node[1] - współrzędna x
                    # node[2] - współrzędna y
                    nodes.append(
                        Node(int(node[0]), int(node[1]), int(node[2])))
            elif demand_section:
                if line.startswith("DEPOT_SECTION"):
                    demand_section = False
                    depot_section = True
                else:
                    node = line.split()
                    # node[0] - id
                    # node[1] - zapotrzebowanie
                    # dodanie wierzchołka z zapotrzebowaniem do grafu
                    graph.add_node(int(node[0]), demand=int(node[1]))
            elif depot_section:
                if line.startswith("-1"):
                    depot_section = False
                else:
                    depot = int(line)
            elif line.startswith("NODE_COORD_SECTION"):
                node_section = True
            elif line.startswith("CAPACITY :"):
                capacity = int(line[line.find(":")+2:])
            elif line.startswith("EDGE_WEIGHT_TYPE :"):
                weight_type = line[line.find(":")+2:]
                if not weight_type.endswith("EUC_2D"):
                    raise Exception("Not supported edge weight type")
            elif line.startswith("COMMENT :"):
                comment = line[line.find(":")+2:]
            elif line.startswith("NAME :"):
                name = line[line.find(":")+2:]
 
    for i, v1 in enumerate(nodes):
        global INITIAL_PHEROMONE_AMOUNT
        for v2 in nodes[i+1:]:
            dist = math.sqrt((v1.x-v2.x)**2+(v1.y-v2.y)**2)
            # TODO jaka wartosc feromonu na poczatku?
            graph.add_edge(v1.id, v2.id, weight=dist, pheromone=INITIAL_PHEROMONE_AMOUNT)
            #print(str(v1.id) + " " + str(v2.id)+ " " + str(dist))

    return CVRPCase(name, comment, graph, capacity, depot)
