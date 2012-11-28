import json
import ast
from sumo.cloudData import cloudData
from sumo.core.constants import *


#######################
# Compute geographical instance statistics
#######################
def get_instances_per_region(format="raw"):

	# init main variable
	instances_in_regions = {}
	for region in EC2_REGIONS: 	
		instances_in_regions[region] = 0

	# find instances per region	
	instances = cloudData.get_all_instances()
	for inst in instances:
		instances_in_regions[inst['region']] = instances_in_regions[inst['region']] + 1

	if format == "raw":
		return instances_in_regions
	elif format == "percentage":
		for region in instances_in_regions:
			 instances_in_regions[region] =  instances_in_regions[region] * 100 / len(instances) 
		return instances_in_regions
				

#######################
# Compute instance type statistics
#######################
def get_instances_per_type(format="raw"):

	# init main variable
	instances_types = {}
	for type in EC2_INSTANCE_TYPES: 	
		instances_types[type] = 0

	# find instances per type 	
	instances = cloudData.get_all_instances()
	for inst in instances:
		instances_types[inst['type']] = instances_types[inst['type']] + 1

	if format == "raw":
		return instances_types
	elif format == "percentage":
		for type in instances_types:
			 instances_types[type] =  instances_types[type] * 100 / len(instances) 
		return instances_types


#######################
# Compute instance OS statistics
#######################
def get_instances_per_os(format="raw"):

	#init main variable
	instances_os = {}
	for os in EC2_OS_TYPES: 	
		instances_os[os] = 0
	
	# find instances per os
	instances = cloudData.get_all_instances()
	for inst in instances:
		instances_os[inst['os']] = instances_os[inst['os']] + 1

	if format == "raw":
		return instances_os
	elif format == "percentage":
		for os in instances_os:
			 instances_os[os] =  instances_os[os] * 100 / len(instances) 
		return instances_os
	

#######################
# Compute instance state statistics
#######################
def get_instances_per_state(format="raw"):

	#init main variable
        instances_state = {}
        for state in EC2_INSTANCE_STATES:
                instances_state[state['name']] = 0

        # find instances per status
        instances = cloudData.get_all_instances()
        for inst in instances:
                instances_state[inst['state']] = instances_state[inst['state']] + 1

        if format == "raw":
                return instances_state
        elif format == "percentage":
                for state in instances_state:
                         instances_state[state] =  instances_state[state] * 100 / len(instances)
                return instances_state
