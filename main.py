from aco_algorithms import SimpleAco
from aco_algorithms import Greedy
import cvrpcases as cvrp

#case_path = r'C:\Users\tomas\Desktop\CVRP-ACO-python-master\debug.vrp'
case_path = r'/home/samba/szczerbinskip/Desktop/CVRP-ACO-python/n32.vrp'
case = cvrp.load_case(case_path)
#print(case)

algorithm = SimpleAco(case, ants_count=50, max_iterations=200, alpha=2, beta=5, evaporation_rate=0.8, pheromone_amount=20, seed = 78)
algorithm.compute(log_level=1)

# algorithm = Greedy(case)
# algorithm.compute(log_level=1)



#algorithm.draw()