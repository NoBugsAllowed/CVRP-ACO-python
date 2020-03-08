from aco_algorithms import SimpleAco
from aco_algorithms import Greedy
import cvrpcases as cvrp

#case_path = r'C:\Users\tomas\Desktop\CVRP-ACO-python-master\debug.vrp'
case_path = r'C:\Users\tomas\Desktop\CVRP-ACO-python-master\debug.vrp'
case = cvrp.load_case(case_path)
#print(case)

#algorithm = SimpleAco(case, ants_count=3, max_iterations=200, alpha=0.5, beta=0.1, evaporation_rate=0.5, pheromone_amount=20, seed = 77)
#algorithm.compute(log_level=1)

algorithm = Greedy(case)
algorithm.compute(log_level=1)



#algorithm.draw()