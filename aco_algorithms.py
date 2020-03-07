import cvrpcases as cvrp
import random

random.seed(420)  # inicjalizacja generatora liczb pseudolosowych


class Ant:
    def __init__(self, node, capacity):
        self.node = node
        self.capacity = capacity
        self.weight_sum = 0  # suma wag krawędzi, po których mrówka przeszła
        self.path = []  # lista kolejnych odwiedzanych wierzchołków


class SimpleAco:
    def __init__(self, case, ants_count, max_iterations, alpha, beta, evaporation_rate, pheromone_amount):
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
            sum += ((1/edge['weight'])**self.alpha) * \
                (edge['pheromone']**self.beta)
        for node in nodes:
            edge = self.case.graph[v][node]
            # TODO co jesli caly feromon odparuje?
            p[node] = (((1/edge['weight'])**self.alpha) *
                       (edge['pheromone']**self.beta)) / sum
        # z posortowanych według wartości p wierzchołków, wybierz pierwszy, dla którego mrówka może spełnić zapotrzebowanie
        for node, _ in sorted(p.items(), key=lambda item: item[1], reverse=True):
            demand = self.case.demands[node]
            if demand <= capacity:
                return node, self.case.graph[v][node]['weight'], demand
        # jeśli nie można spełnić zapotrzebowania żadnego wierzchołka, mrówka wraca do bazy
        return self.case.depot, self.case.graph[v][self.case.depot]['weight'], capacity

    def compute(self,log_level=0):
        for i in range(0, self.max_iterations):
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
                ants.append(ant)
                if log_level > 1:
                    print(" ant " + str(k) + ": " + str(ant.path))
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
