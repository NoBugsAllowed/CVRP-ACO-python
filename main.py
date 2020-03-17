from cvrp_algorithms import SimpleAco, AcoSigmaBestAnts, AcoImprovedPheromoneUpdate, Aco2opt, Greedy
import cvrpcases as cvrp

case_path = r'datasets\A\A-n32-k5.vrp'
case = cvrp.load_case(case_path)

# algorithm = Greedy(case)
# algorithm = SimpleAco(case, ants_count=50, max_iterations=200, alpha=2, beta=5, evaporation_rate=0.6, pheromone_amount=20, seed = 78)
# algorithm = AcoSigmaBestAnts(case, ants_count=50, max_iterations=200, alpha=2, beta=5, evaporation_rate=0.6, pheromone_amount=20, sigma=10, seed = 78)
# algorithm = AcoImprovedPheromoneUpdate(case, ants_count=50, max_iterations=200, alpha=2, beta=5, evaporation_rate=0.6, pheromone_amount=20, sigma=10, seed = 78)
algorithm = Aco2opt(case, ants_count=50, max_iterations=200, alpha=2, beta=5, evaporation_rate=0.6, pheromone_amount=20, seed = 78)

solution, path = algorithm.compute(log_level=1)
print("Solution: " + str(solution))
print("Path: " + str(path))

# sprawdzenie czy poprawnie obliczono koszt rozwiązania
# sum = 0
# v1 = path[0]
# for v2 in path[1:]:
#     sum += case.graph[v1][v2]['weight']
#     v1 = v2
# print("Suma wag: "+str(sum))