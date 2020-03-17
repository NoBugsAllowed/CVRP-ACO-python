import cvrpcases as cvrp
import random
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np


class Ant:
    def __init__(self, node, capacity):
        self.node = node  # wierzchołek, w którym znajduje się mrówka
        self.capacity = capacity  # ładowność
        self.weight_sum = 0  # suma wag krawędzi, po których mrówka przeszła
        self.path = []  # lista kolejnych odwiedzanych wierzchołków

    def get_weight_sum(self):
        return self.weight_sum


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
        self.solution = None  # suma wag krawędzi najlepszego rozwiązania
        self.solution_path = None  # lista wierzchołków najlepszego rozwiązania
        random.seed(seed)  # inicjalizacja generatora liczb pseudolosowych
        np.random.seed(seed)

    def get_p_distribution(self, v, capacity, nodes):
        """Oblicza rozkład prawdopodobieństwa wyboru kolejnego wierzchołka

        Arguments:
            v {int} -- wierzchołek, w którym znajduje się mrówka
            capacity {int} -- ilość towaru posiadana przez mrówkę
            nodes {list(int)} -- lista nieodwiedzonych wierzchołków

        Returns:
            dict(int,float) -- rozkład prawdopodobieństwa
        """
        sum = 0
        weight_sum = 0
        p = {}
        for node in nodes:
            edge = self.case.graph[v][node]
            distance = edge['weight']
            if distance > 0:
                sum += ((1/distance)**self.alpha) * \
                    (edge['pheromone']**self.beta)
                weight_sum += 1/distance
        # zerowa suma wynika z braku feromonu na wszystkich krawędziach wychodzących z danego wierzchołka
        if sum == 0:
            # rozważane są tylko wierzchołki, dla których można spełnić zapotrzebowanie
            for node in [x for x in nodes if self.case.demands[x] <= capacity]:
                distance = self.case.graph[v][node]['weight']
                # prawdopodobieństwo wybrania wierzchołka zależy wtedy tylko od wagi krawędzi
                p[node] = 1 / (distance * weight_sum)
        else:
            for node in [x for x in nodes if self.case.demands[x] <= capacity]:
                edge = self.case.graph[v][node]
                if edge['weight'] > 0:
                    p[node] = (((1/edge['weight'])**self.alpha) *
                               (edge['pheromone']**self.beta)) / sum
        return p

    def pheromone_evaporation(self):
        """Procedura odpowiedzialna za odparowanie feromonu
        """
        for v1, v2 in self.case.graph.edges:
            self.case.graph[v1][v2]['pheromone'] *= 1 - self.rho

    def pheromone_deposition(self, ants):
        """Procedura odpowiedzialna za uwalnianie feromonu

        Arguments:
            ants {list(Ant)} -- lista mrówek
        """
        for ant in ants:
            t = self.pheromone_amount/ant.weight_sum
            v1 = ant.path[0]
            for v2 in ant.path[1:]:
                self.case.graph[v1][v2]['pheromone'] += t
                v1 = v2

    def select_next_node(self, v, capacity, nodes):
        """Wybiera najlepszy wierzchołek dla danej mrówki

        Arguments:
            v {int} -- wierzchołek, w którym znajduje się mrówka
            capacity {int} -- ilość towaru posiadana przez mrówkę
            nodes {list(int)} -- lista nieodwiedzonych wierzchołków

        Returns:
            int, int, int -- krotka zawierająca kolejno: wybrany wierzchołek, wagę krawędzi po której należy przejść oraz ilość rozładowanego towaru
        """
        p = self.get_p_distribution(v, capacity, nodes)

        # wróć do bazy jeśli dla żadnego wierzchołka nie można spełnić zapotrzebowania
        if len(p) == 0:
            return self.case.depot, self.case.graph[v][self.case.depot]['weight'], capacity
        # przeskaluj wartości rozkładu p tak, aby sumowały się do 1
        p_values = list(p.values())
        p_sum = 0
        for val in p_values:
            p_sum += val
        # przypadek gdy sum != 0, zastosowanie rozkładu jednostajnego
        if p_sum == 0:
            size = len(p_values)
            p_values = [1/size for x in range(0, size)]
        else:
            p_values = [x / p_sum for x in p_values]
        # wylosuj następny wierzchołek na podstawie rozkładu p
        next = np.random.choice(list(p.keys()), p=p_values)
        return next, self.case.graph[v][next]['weight'], self.case.demands[next]

    def on_solution_create(self, ant):
        pass

    def compute(self, log_level=0):
        """Przeprowadza obliczenie algorytmu

        Keyword Arguments:
            log_level {int} -- poziom logowania (default: {0})

        Returns:
            int, list(int) -- suma wag krawędzi najlepszego rozwiązania oraz lista kolejnych wierzchołków rozwiązania
        """
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
                # ewentualna logika po utworzenia pełnego rozwiązania przez jedną mrówkę
                self.on_solution_create(ant)
                ants.append(ant)
                if log_level > 2:
                    print(" ant " + str(k) + ": " + str(ant.path) +
                          " summary cost=" + str(ant.weight_sum))
                # zapisz rozwiązanie jeśli jest lepsze od aktualnego
                if self.solution is None or ant.weight_sum < self.solution:
                    self.solution = ant.weight_sum
                    self.solution_path = ant.path
            # odparowanie feromonu
            self.pheromone_evaporation()
            # wydzielanie feromonów przez każdą mrówkę
            self.pheromone_deposition(ants)
            if log_level > 0:
                print("i=" + str(i) + ": " + str(self.solution))
                if log_level > 1:
                    print(self.solution_path)

        return self.solution, self.solution_path

    def draw(self):
        elarge = [(u, v) for (u, v, d) in self.case.graph.edges(data=True)]
        pos = nx.spring_layout(self.case.graph)  # positions for all nodes
        nx.draw_networkx_nodes(self.case.graph, pos, node_size=700)
        nx.draw_networkx_edges(self.case.graph, pos, edgelist=elarge, width=1)
        edge_labels = dict([((u, v,), round(d['weight'], 2))
                            for u, v, d in self.case.graph.edges(data=True)])
        nx.draw_networkx_labels(self.case.graph, pos,
                                font_size=20, font_family='sans-serif')
        nx.draw_networkx_edge_labels(
            self.case.graph, pos, edge_labels=edge_labels)
        plt.axis('off')
        plt.show()

    def print_pheromones(self):
        for v1, v2 in self.case.graph.edges:
            print("v1= ", str(v1) + " v2= " + str(v2) + " pheromone=" +
                  str(self.case.graph[v1][v2]['pheromone']))


class AcoSigmaBestAnts(SimpleAco):
    """
    Modyfikacja algorytmu mrówkowego, w której feromon uwalnia tylko sigma mrówek, które znalazły najlepsze rozwiązania
    """

    def __init__(self, case, ants_count, max_iterations, alpha, beta, evaporation_rate, pheromone_amount, sigma, seed):
        SimpleAco.__init__(self, case, ants_count, max_iterations,
                           alpha, beta, evaporation_rate, pheromone_amount, seed)
        self.sigma = sigma

    def pheromone_deposition(self, ants):
        """Procedura odpowiedzialna za uwalnianie feromonu

        Arguments:
            ants {list(Ant)} -- lista mrówek
        """
        sorted_ants = sorted(ants, key=Ant.get_weight_sum)
        for ant in sorted_ants[:self.sigma]:
            t = self.pheromone_amount/ant.weight_sum
            v1 = ant.path[0]
            for v2 in ant.path[1:]:
                self.case.graph[v1][v2]['pheromone'] += t
                v1 = v2


class AcoImprovedPheromoneUpdate(SimpleAco):
    """
    Modyfikacja algorytmu mrówkowego, w której ilość uwalnianego feromonu zależy także od pozycji mrówki w rankingu.
    Ponadto wzmacniany jest feromon wchodzący w skład aktualnie najlepszego rozwiązania.
    """

    def __init__(self, case, ants_count, max_iterations, alpha, beta, evaporation_rate, pheromone_amount, sigma, seed):
        SimpleAco.__init__(self, case, ants_count, max_iterations,
                           alpha, beta, evaporation_rate, pheromone_amount, seed)
        self.sigma = sigma

    def pheromone_deposition(self, ants):
        """Procedura odpowiedzialna za uwalnianie feromonu

        Arguments:
            ants {list(Ant)} -- lista mrówek
        """
        sorted_ants = sorted(ants, key=Ant.get_weight_sum)
        for i, ant in enumerate(sorted_ants[:self.sigma]):
            t = (self.sigma-i)/ant.weight_sum
            v1 = ant.path[0]
            for v2 in ant.path[1:]:
                self.case.graph[v1][v2]['pheromone'] += t
                v1 = v2
        if self.solution_path is not None:
            t = self.sigma/self.solution
            v1 = self.solution_path[0]
            for v2 in self.solution_path[1:]:
                self.case.graph[v1][v2]['pheromone'] += t
                v1 = v2


class Aco2opt(SimpleAco):
    """
    Modyfikacja algorytmu mrówkowego, w której dla każdego cyklu każdej mrówki stosowana jest heurystyka 2-opt
    """

    def on_solution_create(self, ant):
        new_path = ant.path
        # znajdź indeksy, pod którymi występuje baza, aby podzielić rozwiązanie na cykle (trasy)
        depot_indices = [i for i in range(
            len(ant.path)) if ant.path[i] == self.case.depot]
        # pętla po cyklach
        s = depot_indices[0]
        for e in depot_indices[1:]:
            solution_improved = False
            i = s
            # pierwsza krawędź v1-v2 do wymiany
            v1 = ant.path[i]
            for v2 in ant.path[s+1:e-2]:
                j = i + 2
                # druga krawędź v3-v4 do wymiany
                v3 = ant.path[j]
                for v4 in ant.path[i+3:e+1]:
                    # sprawdź czy zamiana krawędzi polepszy rozwiązanie
                    old_weight = self.case.graph[v1][v2]['weight'] + \
                        self.case.graph[v3][v4]['weight']
                    new_weight = self.case.graph[v1][v3]['weight'] + \
                        self.case.graph[v2][v4]['weight']
                    if old_weight > new_weight:
                        # odwróć część ścieżki
                        new_path[i+1:j+1] = new_path[i+1:j+1][::-1]
                        # zaktualizuj koszt rozwiązania
                        ant.weight_sum -= old_weight - new_weight
                        # przerwij wyszukiwanie ulepszenia dla tego cyklu
                        solution_improved = True
                        break
                    j += 1
                    v3 = v4
                if solution_improved:
                    break
                i += 1
                v1 = v2
            s = e
        ant.path = new_path


class Greedy:
    def __init__(self, case):
        self.case = case  # instancja problemu
        self.solution = None
        self.solution_path = None

    def compute(self, log_level=0):
        Vehicles = []
        for _ in range(self.case.graph.number_of_nodes()-1):
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
                    if(v.capacity >= self.case.demands[n] and self.case.graph[v.node][n]['weight'] < min):
                        min = self.case.graph[v.node][n]['weight']
                        vmin = v
                        nmin = n

            vmin.weight_sum += self.case.graph[vmin.node][nmin]['weight']
            vmin.path.append(nmin)
            vmin.capacity -= self.case.demands[nmin]
            vmin.node = nmin
            nodes.remove(nmin)

        sum = 0
        full_path = [self.case.depot]

        for v in Vehicles:
            if(v.node != self.case.depot):
                v.weight_sum += self.case.graph[v.node][self.case.depot]['weight']
                v.node = self.case.depot
                v.path.append(self.case.depot)
            sum += v.weight_sum
            full_path += v.path[1:]
            if log_level > 0:
                print("path = " + str(v.path) + " cost = " + str(v.weight_sum))

        return sum, full_path


class Vehicle:
    def __init__(self, capacity, node):
        self.node = node
        self.capacity = capacity
        self.weight_sum = 0
        self.path = [node]  # lista kolejnych odwiedzanych wierzchołków
