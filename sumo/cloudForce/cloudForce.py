import cplex
from cplex.exceptions import CplexError
import sys
import datetime
from sumo.cloudData import cloudData
from sumo.core import utils


#######################
# Algorithm for optimizing th cost and the utilization of a set of instances
#######################
def cost_utilization_optimization(instances, statistics, T, f=1, W=0.5):

	##
	wl = cloudData.get_instances_workload_percentage(instances,statistics)

	# running instances and available instances
	m = len(wl)
        
	capacity=cloudData.get_instance_types_capacities()
	
	cost = cloudData.get_instance_types_costs()
        
	all_available_types = cloudData.get_instance_types_count() 

	D = len(capacity)

	cost_f = []
	
	for i in range(len(cost)):
		cost_f.append(cost[i]*T)

	DU = sum(wl)*f
	
	# data common to all populate by functions,m*D zeros kai ta dio teleftaia eiani idia 
	my_obj = [0]*m*D
	my_obj.append(1-W)
	my_obj.append(W)

	my_colnames = []
	for i in range(m):
		for j in range(D):
			my_colnames.append("x"+str(i)+str(j))
	my_colnames.extend("U"+"C")

	# tosoi '1' oso to m, m fores ola ta pi pou exw sti dia8esi mou, 2 midenika kai ena DU
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

		# since lower bounds are all 0.0 (the default), lb is omitted here
		prob.variables.add(obj = my_obj, names = my_colnames, types = my_type)# ub = my_ub
				
		rows = []
		rows1 = []
		rows2 = []
		my_rows = []

		for i in range(m):
			rows1 = my_colnames[i*D:i*D+D]
			rows2 = [1.0]*D
			rows.append(rows1)
			rows.append(rows2)
			my_rows.append(rows)
			rows = []
			list2 = []

		for i in range(m):
			for j in range(D):
				list2 = [[my_colnames[i*D+j]],[wl[i]]]
				my_rows.append(list2)
				list2 = []

		list3 = []
		list4 = []
		list3 = [my_colnames[0:len(my_colnames)-1], capacity*m+[-1.0]]
		list4 = [my_colnames[0:len(my_colnames)-2] + [my_colnames[len(my_colnames)-1]],  cost_f*m+[-1.0] ]
		my_rows.append(list3)
		my_rows.append(list4)
		list5 = [["U"],[ 1.0]]
		my_rows.append(list5)

		prob.linear_constraints.add(lin_expr = my_rows, senses = my_sense,rhs = my_rhs, names = my_rownames)
		
	
	my_prob = cplex.Cplex()
	handle = populatebyrow(my_prob)
	my_prob.solve()

	numrows = my_prob.linear_constraints.get_num()
	numcols = my_prob.variables.get_num()

	print
	print "Solution status = " , my_prob.solution.get_status(), ":",
	# the following line prints the corresponding string
	print my_prob.solution.status[my_prob.solution.get_status()]
	print "Solution value  = ", my_prob.solution.get_objective_value()

	numcols = my_prob.variables.get_num()
	numrows = my_prob.linear_constraints.get_num()

	slack = my_prob.solution.get_linear_slacks()
	x = my_prob.solution.get_values()

	final_types_indices = []
	init_types_indices = []

	for j in range(numcols):
                if x[j] == 1:
                        final_types_indices.append(j%all_available_types)
                       
	all_types = cloudData.get_all_instance_types()

        for ins in instances:
                init_types_indices.append(all_types.index({"type":ins['type'],"region":ins['region'],"os":ins['os']}))

	return init_types_indices,final_types_indices
