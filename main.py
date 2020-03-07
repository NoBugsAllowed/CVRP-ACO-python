from aco_algorithms import SimpleAco
import cvrpcases as cvrp

case_path = r'E:\Downloads\A-VRP\A-n32-k5.vrp'
case = cvrp.load_case(case_path)
print(case)

algorithm = SimpleAco(case, ants_count=50, max_iterations=100, alpha=2, beta=5, evaporation_rate=0.5, pheromone_amount=1)
algorithm.compute(log_level=1)