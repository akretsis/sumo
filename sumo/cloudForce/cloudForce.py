import sys
import datetime
import math
from datetime import timedelta
from sumo.cloudData import cloudData
from sumo.core import utils
from sumo.core import Exceptions


try:
	import cplex
	from cplex.exceptions import CplexError	
except ImportError:
	tm = u"ERROR: cloudForce requires the CPLEX\u00AE Python API"
	print tm.encode("utf-8")
	sys.exit(1)

"""
.. module:: cloudForce
  :synopsis: Algorithm for optimizing the cost and the utilization of a set of instances

.. moduleauthor:: Kokkinos Panagiotis <kokkinop@gmail.com>, Kretsis Aristotelis <aakretsis@gmail.com> , Poluzois Soumplis <polibios@gmail.com>


"""

def get_instances_info(instances,statistics):

	"""Calculates various information required by the algorithm
		:param instances: instances.
		:type instances: list.
		:param statistics: statistical data for each instance,there is one by one mapping with first argument.
		:type statistics: list.
		:returns: 			
	"""

	T = []

	capacity = cloudData.get_instance_types_capacities()

	cost = cloudData.get_instance_types_costs()

	D = len(capacity)

	for i in range(len(instances)):

		timestamp = []

		for stat in statistics[i]:
			timestamp.append(stat['Timestamp'])	
		
		start = timestamp[0].split("datetime.datetime")[1].strip("()").split(",")
		index = len(timestamp)-1		
		end = timestamp[index].split("datetime.datetime")[1].strip("()").split(",")		
		diff = datetime.datetime(int(end[0]),int(end[1]),int(end[2]),int(end[3]),int(end[4]),0)-datetime.datetime(int(start[0]),int(start[1]),int(start[2]),int(start[3]),int(start[4]),0)

		T.append((diff.days*24) + (diff.seconds/3600)+1)
		
	return D,capacity,cost,T



def calculate_initial_state(instances,T):

	"""Calculates the initial values for the given instances about total cost, total capacity and instance types
		:param instances: instances.
		:type instances: list.
		:param statistics: running time in hours for each instance , there is one by one mapping with first argument.
		:type statistics: list.
		:returns: total cost,total capacity and instance types.			
	"""

	capacity = cloudData.get_instances_capacity(instances)	

	prices = cloudData.get_instances_cost(instances)

	cost = 0.0
	
	for i in range(len(instances)):
		cost = cost + T[i]*prices[i]

	types=[]

	for instance in instances:
		types.append({'os': instance['os'] , 'region': instance['region'] , 'type': instance['type'] })
		
	total_capacity = sum(capacity)

	return cost,total_capacity,types


def cost_utilization_optimization(instances, statistics, operation='Average', f=1, W=0.5):

	"""Algorithm for optimizing the cost and the utilization of a set of instances
		:param instances: Signal to use.
		:type instances: list.
		:param statistics: Signal to use.
		:type statistics: list.
		:param f: Signal to use.
		:type f: list.
		:param W: Signal to use.
		:type W: list.
		:returns:  something.
		:raises: ExecutionError	
	"""
	
	if len(instances) != len(statistics):
		raise Exceptions.ExecutionError("cost_utilization_optimization","Instances and statistics lists have different size")
		

	os_vectors = utils.create_os_vectors()

	wl = cloudData.get_instances_workload(instances,statistics,operation)

	m = len(wl)

	(D,capacity,cost,T) = get_instances_info(instances,statistics)

	cost_vector = []

	for i in range(len(T)):
		for cj in range(len(cost)):
			cost_vector.append(cost[cj]*T[i])

	initial_cost = 0

	instances_cost = cloudData.get_instances_cost(instances)

	for i in range(len(instances)):
		initial_cost = initial_cost+instances_cost[i]*T[i]

	DU = sum(wl)/f

	my_obj = [0]*m*D
	my_obj.append(1-W)
	my_obj.append(W)

	my_colnames = []
	for i in range(m):
		for j in range(D):
			my_colnames.append("x"+str(i)+"_"+str(j))
	my_colnames.extend("U"+"C")


	my_rhs = []
	my_rhs1 = [1]*m
	my_rhs2 = []

	for i in range(m):
		my_rhs2.extend(capacity)

	my_rhs3 = [0,0,DU]
	my_rhs = my_rhs1+my_rhs2+my_rhs3

	my_type = []

	for i in range(m*D):
		my_type.extend("I")

	my_type.extend("C"*2)
 
	num_c = m+m*D+2+1
	my_rownames = []
	for i in range(num_c):
		my_rownames.append("c"+str(i+1))

	my_sense = []
	my_sense.extend("E"*m)
	my_sense.extend("L"*(m*D))
	my_sense.extend("E"*2)
	my_sense.extend("G")

	def populatebyrow(prob):
		
		prob.objective.set_sense(prob.objective.sense.minimize)

		prob.variables.add(obj = my_obj, names = my_colnames, types = my_type)

		rows = []
		rows1 = []
		rows2 = []
		my_rows = []

		for i in range(m):

			rows1 = my_colnames[i*D:i*D+D]
			
			if instances[i]['os'] == 'linux':
				rows2 = os_vectors[1]
			else:
				rows2 = os_vectors[0]
			
			rows.append(rows1)
			rows.append(rows2)
			my_rows.append(rows)
			rows = []

		list2=[]
		
		for i in range(m):
			for j in range(D):
				list2 = [[my_colnames[i*D+j]],[wl[i]]]
				my_rows.append(list2)
				list2 = []

		list3 = []
		list4 = []
		list3 = [my_colnames[0:len(my_colnames)-1], capacity*m+[-1.0]]
		list4 = [my_colnames[0:len(my_colnames)-2] + [my_colnames[len(my_colnames)-1]],  cost_vector+[-1.0] ]
	
		my_rows.append(list3)
		my_rows.append(list4)
		list5 = [["U"],[ 1.0]]
		my_rows.append(list5)
		
		prob.linear_constraints.add(lin_expr = my_rows, senses = my_sense,rhs = my_rhs, names = my_rownames)

		
	my_prob = cplex.Cplex()
	my_prob.parameters.read.datacheck.set(1)
	handle = populatebyrow(my_prob)
	my_prob.set_results_stream(None) 
	my_prob.solve()

	numrows = my_prob.linear_constraints.get_num()
	numcols = my_prob.variables.get_num()

	cplex_solution = { "code":  my_prob.solution.get_status() , "status": str(my_prob.solution.status[my_prob.solution.get_status()]) , "value": my_prob.solution.get_objective_value() }

	numcols = my_prob.variables.get_num()
	numrows = my_prob.linear_constraints.get_num()

	slack = my_prob.solution.get_linear_slacks()
	x = my_prob.solution.get_values()

	cuo_instance_types = []

	all_types = cloudData.get_all_instance_types()

	for j in range(numcols):
		if x[j]==1:
			cuo_instance_types.append(all_types[j%D])
			

	(initial_cost,initial_capacity,initial_instance_types) = calculate_initial_state(instances,T)
	

        return { "initial_cost": initial_cost , "cuo_cost": x[numcols-1] , "initial_total_capacity":initial_capacity , "cuo_total_capacity":x[numcols-2] , "total_workload": sum(wl) , "initial_instance_types": initial_instance_types , "cuo_instance_types": cuo_instance_types }

        
