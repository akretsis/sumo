import boto
import datetime
import time
import random
import math
import boto.ec2
import sumo.cloudData.ec2_instances_pricing as ec2_pricing
import sumo.cloudData.ec2_instances_capacity as ec2_capacity
from boto.ec2.connection import EC2Connection
from boto.ec2.cloudwatch import *
from sumo.core import db
from sumo.core import utils
from sumo.core.constants import *
from sumo.core.keys import *


#######################
# Connect to AWS EC2
#######################
def connect_to_aws_ec2(region = None):

	if region != None:
		conn = EC2Connection(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, region=region)
	else:
		conn = EC2Connection(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
	
	return conn


#######################
# Get running instances	based on the input EC2 connection
#######################
def get_ec2connection_instances(ec2_conn):
		
	reservations = ec2_conn.get_all_instances()
	
	instances = [i for r in reservations for i in r.instances]

	instances_list = list() 

	for i in instances:
		inst = {}
		inst['id'] = i.id
		inst['state'] = i.state
		inst['type'] = i.instance_type
		inst['region'] = i.region.name
		image_info = ec2_conn.get_image(i.image_id)
	
		if "Linux" in image_info.description:
			inst['os'] = EC2_OS_TYPES[0]
		else:
			inst['os'] = EC2_OS_TYPES[1]

		instances_list.append(inst)

	return instances_list
	

#######################
# Get instances from a specific region or else the default will be used
#######################
def get_regional_instances(region_name = ""):

	if len(region_name) > 0:
		region = boto.ec2.get_region(region_name,aws_access_key_id=AWS_ACCESS_KEY_ID,aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
	else:
		region = None
		
	conn = connec_to_awd_ec2(region)	
	instances = get_ec2connection_instances(conn)

	return instances
	
	
#######################
# Get all user's instances (from all regions)
#######################
def get_all_instances():

	all_instances = []
	
	# get all regions
	regions = boto.ec2.regions(aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

	# get instances per region
	for region in regions:
	
		conn = connect_to_aws_ec2(region)	
		instances = get_ec2connection_instances(conn)

		all_instances.extend(instances)

	return all_instances

	
#######################
# A wrapper function for getting the values of a metric for an instance over a time period
#######################
def get_instance_metric(start, end, step_size, metric_name, instance_id, region_name="us-west-1"):

	#Get RegionInfo object from region name	
	cloudwatch_regions=boto.ec2.cloudwatch.regions()	
	
	for r in cloudwatch_regions:
		if r.name == region_name:
			region = r
			break

	# Connect to aws cloudwatch
	conn = boto.connect_cloudwatch(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, region=region)

	# The statistic to request i.e. Average, Sum, Maximum, Minimum or SampleCount
	operations_type = ['Average', 'Maximum', 'Minimum']

	# This is the dimensions to request from CloudWatch
	# To get data for a specific instance replace instanceId for the instance you're looking for
	# Detailed monitoring adds additional dimensions including AmiId, InstanceType
	dimensions = { 'InstanceId':instance_id }

	# Get unit based on metric_name
	unit = UNIT_OF_METRIC[metric_name]

	# Get namespace based on metric_name
	namespace = NAMESPACE_OF_METRIC[metric_name]

	# This wil request data for for the period, for the time of start to end, and 
	datapoints = conn.get_metric_statistics(step_size, start, end, metric_name, namespace, operations_type, dimensions, unit);
	
	return datapoints


#######################
# A wrapper function for getting the values of a metric for a set of instances instance over a time period
#######################
def get_all_instances_metric(start, end, step_size, metric_name, instances):

	metric_datapoints_array = list()
	
	for instance in instances:
		stats = get_instance_metric(start, end, step_size, metric_name, instance["id"], instance["region"])
		metric_datapoints_array.append(stats)
	
	return metric_datapoints_array


#######################
# Converts statistics datapoints to more easier handled signal
#######################
def datapoints_to_signal(metric_datapoints):
	
	metric_signal = list()

	for point in datapoints:
		p = {}
		p['Timestamp'] = point['Timestamp'].strftime('%s')
		p['Average'] = point['Average']
		p['Maximum'] = point['Maximum']
		p['Minimum'] = point['Minimum']
		p['Unit'] = point['Unit']
		metric_signal.append(p)	

	return metric_signal

	
#######################
# Calculates an aggregated value of received signal
#######################
def aggregate_metric(metric_datapoints, operation='Average'):

	valid_operations = ['Average','Minimum','Maximum']
	metric_values = []
	aggregated_value = 0;
	
	if operation not in valid_operations:
		print ""
		print "Error: Invalid operation parameters. Valid options: %s"%(valid_operations)
		print ""		
		return -1

	for data in metric_datapoints:
		metric_values.append(data[operation])

	if operation == "Average":
		aggregated_value = (math.fsum(metric_values))/len(metric_values)
	elif operation == "Minimum":
		aggregated_value = min(metric_values)
	elif operation == "Maximum":
		aggregated_value = max(metric_values)
    	else:
	    return -1

	return aggregated_value


#######################
# Calcuates the workload percentage of the given instances, assuming that the given array contains the EC2 utilization of these instance
# for a particular time period and that an aggregator parameter is used
#######################
def get_instances_workload_percentage(instances, workload_datapoints_array, param = 'Average'):

	workload = []
	workload_percentage = []
        
	for workload_datapoints in workload_datapoints_array:
		workload.append(aggregate_metric(workload_datapoints, param))

	capacity = get_instances_capacity(instances)

	for i in range(len(workload)):
		workload_percentage.append((workload[i]/100)*capacity[i])
	
	return workload_percentage
	
	
#######################
# Gets the capacity of each machine type (in EC2)
#######################
def get_capacity_per_machine_type():

	data = ec2_capacity.get_ec2_instances_capacity()

	capacity = {}
	for c in data:
		capacity[c['type']] = c['compute_units']*c['virtual_cores']

	return capacity


#######################
# Gets input instances' cost
#######################
def get_instances_cost(instances):

	cost = []
	for instance in instances:	
		price = ec2_pricing.get_ec2_ondemand_instances_prices(filter_region=instance['region'],filter_instance_type=instance['type'],filter_os_type=instance['os'])
		cost.append(price['regions'][0]['instanceTypes'][0]['price'])

	return cost


#######################
# Gets the capacity of each instance (and the corresponding machine type) (in EC2)
#######################
def get_instances_capacity(instances):

	c = get_capacity_per_machine_type()

	capacity = []
	for instance in instances:
		capacity.append(c[instance['type']])

	return capacity


#######################
# Gets the number of different instance types
#######################
def get_instance_types_count():

	return len(EC2_INSTANCE_TYPES)*len(EC2_REGIONS)*len(EC2_OS_TYPES)


#######################
# Gets all instance types
#######################
def get_all_instance_types():

	all_instance_type = []

        for ins_type in EC2_INSTANCE_TYPES:
                for region in EC2_REGIONS:
                        for os in EC2_OS_TYPES:
                                all_instance_type.append({"type":str(ins_type),"region":str(region),"os":str(os)})

	return all_instance_type


#######################
# Get all instance types costs
#######################
def get_instance_types_costs():

	all_combinations = []
	cost = []

	for ins_type in EC2_INSTANCE_TYPES:
		for region in EC2_REGIONS:
			for os in EC2_OS_TYPES:
				all_combinations.append({"type":str(ins_type),"region":str(region),"os":str(os)})

	for combination in all_combinations:	
		price = ec2_pricing.get_ec2_ondemand_instances_prices(filter_region=combination['region'],filter_instance_type=combination['type'],filter_os_type = combination['os'])

		cost.append(price['regions'][0]['instanceTypes'][0]['price'])
	
	return cost	


#######################
# Get all instance types computational capacities
#######################
def get_instance_types_capacities():

	capacity = []
	cap = get_capacity_per_machine_type()

	for ins_type in EC2_INSTANCE_TYPES:
		for region in EC2_REGIONS:
			for os in EC2_OS_TYPES:
				capacity.append(cap[ins_type])

	return capacity	
