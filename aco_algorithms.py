import cvrpcases as cvrp
import random
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np



class Ant:
    def __init__(self, node, capacity):
        self.node = node
        self.capacity = capacity
        self.weight_sum = 0  # suma wag krawędzi, po których mrówka przeszła
        self.path = []  # lista kolejnych odwiedzanych wierzchołków


class SimpleAco:
    def __init__(self, case, ants_count, max_iterations, alpha, beta, evaporation_rate, pheromone_amount, seed):
        self.case = case  # instancja problemu
        self.ants_count = ants_count  # liczba mrówek
        # liczba iteracji po jakiej zakończyć obliczenia
        self.max_iterations = max_iterations
        self.alpha = alpha  # współczynnik oznaczający chęć mrówek do podążania za feromonem
        self.beta = beta  # współczynnik oznaczający wpływ kosztu drogi na wybór kolejnego wierzchołka
        self.rho = evaporation_rate  # współczynnik odparowywania feromonu
        # parametr definiujący ile feromonu produkują mrówki
        self.pheromone_amount = pheromone_amount
        self.solution = None
        self.solution_path = None
        random.seed(seed) # inicjalizacja generatora liczb pseudolosowych

    def get_random_node(self):
        """Zwraca losowy indeks wierzchołka różny od indeksu bazy

        Returns:
            int -- indeks wybranego wierzchołka
        """
        v = random.randint(1, self.case.graph.number_of_nodes())
        while v == self.case.depot:
            v = random.randint(1, self.case.graph.number_of_nodes())
        return v

    def select_next_node(self, v, capacity, nodes):
        """Wybiera najlepszy wierzchołek dla danej mrówki

        Arguments:
            v {int} -- wierzchołek, w którym znajduje się mrówka
            capacity {int} -- ilość towaru posiadana przez mrówkę
            nodes {list(int)} -- list nieodwiedzonych wierzchołków

        Returns:
            integer, integer, integer -- krotka zawierająca kolejno: wybrany wierzchołek, wagę krawędzi po której należy przejść oraz ilość rozładowanego towaru
        """
        sum = 0
        p = {}
        for node in nodes:
            edge = self.case.graph[v][node]
            if edge['weight']>0:
                sum += ((1/edge['weight'])**self.alpha) * \
                    (edge['pheromone']**self.beta)
        for node in nodes:
            demand = self.case.demands[node]
            if demand > capacity:
                continue
            edge = self.case.graph[v][node]
            # TODO co jesli caly feromon odparuje?
            if edge['weight']>0:
                p[node] = (((1/edge['weight'])**self.alpha) *
                       (edge['pheromone']**self.beta)) / sum
        # z posortowanych według wartości p wierzchołków, wybierz pierwszy, dla którego mrówka może spełnić zapotrzebowanie
        # for node, _ in sorted(p.items(), key=lambda item: item[1], reverse=True):
        #     demand = self.case.demands[node]
        #     if demand <= capacity:
        #         return node, self.case.graph[v][node]['weight'], demand
        # # jeśli nie można spełnić zapotrzebowania żadnego wierzchołka, mrówka wraca do bazy
        # return self.case.depot, self.case.graph[v][self.case.depot]['weight'], capacity
        if len(p)==0:
            return self.case.depot, self.case.graph[v][self.case.depot]['weight'], capacity
        # wylosuj następny wierzchołek na podstawie rozkładu p
        
        pvalues = list(p.values())
        sump = 0
        for x in pvalues:
            sump = sump + x
        pvalues = [x/sump for x in pvalues]

        next = np.random.choice(list(p.keys()), p=pvalues)
        return next, self.case.graph[v][next]['weight'], demand

    def compute(self,log_level=0):
        for i in range(0, self.max_iterations):
            if log_level > 2:
                self.print_pheromones()
            ants = []
            for k in range(0, self.ants_count):
                # zainicjowanie w pełni załadowanej mrówki w bazie
                ant = Ant(self.case.depot, self.case.capacity)
                # pobranie listy wierzchołków i usunięcie z niej bazy
                nodes = list(self.case.graph.nodes())
                nodes.remove(self.case.depot)
                # losowy wybór pierwszgo wierzchołka
                idx = random.randint(0, len(nodes)-1)
                if log_level > 1:
                    print("first vertex index for " +str(k)+" Ant = " + str(nodes[idx]))

                v = nodes[idx]
                edge = self.case.graph[self.case.depot][v]
                ant.weight_sum += edge['weight']
                ant.capacity -= self.case.demands[v]
                ant.node = v
                ant.path = [self.case.depot, v]
                nodes.remove(v)
                # dopóki pozostały wierzchołki do odwiedzenia
                while len(nodes) > 0:
                    v, weight, demand = self.select_next_node(
                        ant.node, ant.capacity, nodes)
                    # podróż mrówki do kolejnego wierzchołka
                    ant.weight_sum += weight
                    ant.capacity -= demand
                    ant.node = v
                    ant.path.append(v)
                    if v == self.case.depot:
                        # powrócono do bazy - załaduj do pełna
                        ant.capacity = self.case.capacity
                    else:
                        nodes.remove(v)
                # powrót do bazy po odwiedzeniu wszystkich wierzchołków
                edge = self.case.graph[ant.node][self.case.depot]
                ant.weight_sum += edge['weight']
                ant.node = self.case.depot
                ant.path.append(self.case.depot)
                ants.append(ant)
                if log_level > 1:
                    print(" ant " + str(k) + ": " + str(ant.path) + " summary cost=" + str(ant.weight_sum))
                # zapisz rozwiązanie jeśli jest lepsze od aktualnego
                if self.solution is None or ant.weight_sum < self.solution:
                    self.solution = ant.weight_sum
                    self.solution_path = ant.path
            # odparowanie feromonu
            for v1, v2 in self.case.graph.edges:
                self.case.graph[v1][v2]['pheromone'] *= 1 - self.rho
            # wydzielanie feromonów przez każdą mrówkę
            for ant in ants:
                t = self.pheromone_amount/ant.weight_sum
                v1 = ant.path[0]
                for v2 in ant.path[1:]:
                    self.case.graph[v1][v2]['pheromone'] += t
                    v1 = v2
            if log_level > 0:
                print("i=" + str(i) + ": " + str(self.solution))

    def draw(self):
        elarge = [(u, v) for (u, v, d) in self.case.graph.edges(data=True)]
        pos = nx.spring_layout(self.case.graph)  # positions for all nodes
        nx.draw_networkx_nodes(self.case.graph, pos, node_size=700)
        nx.draw_networkx_edges(self.case.graph, pos, edgelist=elarge,width=1)
        edge_labels=dict([((u,v,),round(d['weight'],2))
                 for u,v,d in self.case.graph.edges(data=True)])
        nx.draw_networkx_labels(self.case.graph, pos, font_size=20, font_family='sans-serif')
        nx.draw_networkx_edge_labels(self.case.graph,pos,edge_labels=edge_labels)
        plt.axis('off')
        plt.show()

    def print_pheromones(self):
        for v1, v2 in self.case.graph.edges:
            print("v1= ", str(v1) + " v2= " + str(v2) + " pheromone=" + str(self.case.graph[v1][v2]['pheromone']))


class Greedy:
    def __init__(self, case):
        self.case = case  # instancja problemu
        self.solution = None
        self.solution_path = None

    def get_random_node(self):
        """Zwraca losowy indeks wierzchołka różny od indeksu bazy

        Returns:
            int -- indeks wybranego wierzchołka
        """
        v = random.randint(1, self.case.graph.number_of_nodes())
        while v == self.case.depot:
            v = random.randint(1, self.case.graph.number_of_nodes())
        return v

    def compute(self,log_level=0):
        Vehicles = []
        for dd in range(self.case.graph.number_of_nodes()-1):
            v = Vehicle(self.case.capacity, self.case.depot)
            Vehicles.append(v)

        
        nodes = list(self.case.graph.nodes())
        nodes.remove(self.case.depot)
        

        while len(nodes) > 0:

            min = float('inf')
            vmin = -1
            nmin = -1

            for v in Vehicles:
                for n in nodes:
                    if(v.capacity>= self.case.demands[n] and self.case.graph[v.node][n]['weight']<min): 
                        min = self.case.graph[v.node][n]['weight']
                        vmin = v
                        nmin = n

            vmin.weight_sum += self.case.graph[vmin.node][nmin]['weight']
            vmin.path.append(nmin)
            vmin.capacity-=self.case.demands[nmin]
            vmin.node = nmin
            nodes.remove(nmin)
        
        sum = 0

        for v in Vehicles:
            if(v.node!=self.case.depot):
                v.weight_sum += self.case.graph[v.node][self.case.depot]['weight']
                v.node = self.case.depot
                v.path.append(self.case.depot)
            sum += v.weight_sum
            print("path = " + str(v.path) + " cost = " + str(v.weight_sum))

        print("result = " + str(sum))


class Vehicle:
    def __init__(self, capacity, node):
        self.node = node
        self.capacity = capacity
        self.weight_sum = 0  
        self.path = [node]  # lista kolejnych odwiedzanych wierzchołków