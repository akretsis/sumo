import json
import ast
from sumo.cloudData import cloudData
from sumo.core.constants import *
from sumo.cloudData import s3_pricing


"""
.. module:: cloudKeeping
  :synopsis: Contains a set of key performance indicators

.. moduleauthor:: Panagiotis Kokkinos <kokkinop@ceid.upatras.gr> , Aristotelis Kretsis <akretsis@ceid.upatras.gr>


"""


def get_instances_per_region(format="raw"):

	"""Computes the number of instances per region.

		:param format: "raw" numbers or in "percentage".
		:type format: string.
		:returns: dict -- number or percentage of instances per region.		

	"""
	
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
				

def get_instances_per_type(format="raw"):

	"""Computes the number of instances per type.

		:param format: "raw" numbers or in "percentage".
		:type format: string.
		:returns: dict -- number or percentage of instances per type.
		
	"""

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


def get_instances_per_os(format="raw"):

	"""Computes the number of instances per Operating System.

		:param format: "raw" numbers or in "percentage".
		:type format: string.
		:returns: dict -- number or percentage of instances per Operating System.	

	"""

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
	

def get_instances_per_state(format="raw"):

	"""Computes the number of instances per instance state.

		:param format: "raw" numbers or in "percentage".
		:type format: string.
		:returns: dict -- number or percentage of instances per instance state.		

	"""

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


def calculate_capacity_per_os(instances=None):

	"""Computes the total instances' capacity per Operating System.

		:param instances: list of instances or "None" if all the user's instances will be considered.
		:type instances: list.
		:returns: dict -- total capacity of instances per operating system.

	"""

	capacity={}

	if instances == None:
		instances = cloudData.get_all_instances()
		
	for os in EC2_OS_TYPES: 	
		capacity[os]=sum(cloudData.get_instances_capacity(instances,{'param_name':'os','param_value':os}))	
		
	return capacity


def calculate_capacity_per_region(instances=None):

	"""Computes the total instances' capacity per region.

		:param instances: list of instances or "None" if all the user's instances will be considered.
		:type instances: list.
		:returns: dict -- total capacity of instances per region.

	"""

	capacity={}

	if instances == None:
		instances = cloudData.get_all_instances()
		
	for region in EC2_REGIONS: 	
		capacity[region]=sum(cloudData.get_instances_capacity(instances,{'param_name':'region','param_value':region}))	
		
	return capacity
	
	
def calculate_capacity_per_machine_type(instances=None):

	"""Computes the total instances' capacity per machine type.

		:param instances: list of instances or "None" if all the user's instances will be considered.
		:type instances: list.
		:returns: dict -- total capacity of instances per machine type.

	"""

	capacity={}

	if instances == None:
		instances = cloudData.get_all_instances()
	
	for machine in EC2_INSTANCE_TYPES:
		capacity[machine]=sum(cloudData.get_instances_capacity(instances,{'param_name':'type','param_value':machine}))	
		
	return capacity


def calculate_capacity_per_instance_state(instances=None):

	"""Computes the total instances' capacity per instance state.

		:param instances: list of instances or "None" if all the user's instances will be considered.
		:type instances: list.
		:returns: dict -- total capacity of instances per instance state.

	"""

	capacity={}

	if instances == None:
		instances = cloudData.get_all_instances()
	
	for state in EC2_INSTANCE_STATES:
		capacity[state['name']]=sum(cloudData.get_instances_capacity(instances,{'param_name':'state','param_value':state['name']}))	
		
	return capacity
		

def calculate_capacity_per_instance(instances=None):

	"""Computes the total instances' capacity per instance.

		:param instances: list of instances or "None" if all the user's instances will be considered.
		:type instances: list.
		:returns: dict -- total capacity of instances per instance.

	"""

	capacity=[]

	if instances == None:
		instances = cloudData.get_all_instances()
	
	#for instance in instances:
	instances_capacity = cloudData.get_instances_capacity(instances)	
	
	i=0
	for instance in instances:
		capacity.append({"id":instance['id'],"capacity":instances_capacity[i]})		
		i=i+1
	
	return capacity
		
						

def calculate_s3_storage_monthly_cost():

	"""Calculates S3 storage montly cost.

		:returns: int, int -- total montly cost and size of S3 storage.

	"""

	total_storage_size_GB = 0.0
	total_cost = 0.0
	
	storage_details = cloudData.get_buckets_storage_pricing_info()

	for storage in storage_details:
		
		region = storage['region'] if len(storage['region'])>0 else 'us-east'
		
		for storage_class in ["STANDARD","REDUCED_REDUNDANCY","GLACIER"]: 
			
			storage_size_GB = float(storage['size_per_storage_class'][storage_class])/1024
			
			total_storage_size_GB += storage_size_GB 		
				
			cost = s3_pricing.compute_s3_storage_price(region,storage_class,storage_size_GB)
			
			total_cost += cost
			
		
	return { 'cost': total_cost , 'storage_size_GB': total_storage_size_GB }


"""
def calculate_ec2_monthly_cost():
	
	return { 'cost': 0 }
	
"""
