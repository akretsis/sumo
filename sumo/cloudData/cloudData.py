
"""
.. module:: cloudData
  :synopsis: Collecting Monitoring Data

.. moduleauthor:: Panagiotis Kokkinos <kokkinop@ceid.upatras.gr> , Aristotelis Kretsis <akretsis@ceid.upatras.gr>


"""

import boto
import datetime
import isodate
import time
import random
import math
import pprint
import boto.ec2
import boto.s3
import sumo.cloudData.ec2_instances_pricing as ec2_pricing
import sumo.cloudData.ec2_instances_capacity as ec2_capacity
import sumo.cloudData.s3_pricing as s3_pricing
from boto.ec2.connection import EC2Connection
from boto.s3.connection import S3Connection
from boto.s3.connection import Location
from boto.ec2.cloudwatch import *
from sumo.core import db
from sumo.core import utils
from sumo.core.constants import *
from sumo.core.keys import *



def connect_to_aws_ec2(region = None):
	"""Connect to AWS EC2

		:param region: The region to use.
		:type region: str.
		:returns:  int -- the return code.
		:returns: EC2Connection -- a connection to the given region or to any region if no region is specified.	

	"""

	if region != None:
		conn = EC2Connection(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, region=region)
	else:
		conn = EC2Connection(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
	
	return conn



def get_ec2connection_instances(ec2_conn,defined_filters=None):

	"""Get running instances based on the input EC2 connection
	
		:param ec2_conn: A EC2 connection to AWS object.
		:type ec2_conn: EC2Connection.
		:param defined_filters: Optional filters that can be used to limit the results returned (provided by boto). 
		:type defined_filters: dict.
		:returns: list -- a list of instances.		
		
	"""		

	reservations = ec2_conn.get_all_instances(filters=defined_filters)
	
	instances = [i for r in reservations for i in r.instances]

	instances_list = list() 

	for i in instances:
		
		inst = {}
		
		inst['id'] = i.id
		inst['state'] = i.state
		inst['state_code'] = i.state_code
		inst['type'] = i.instance_type	
		inst['key_name'] = i.key_name
		inst['region'] = i.region.name
		inst['launch_time'] = i.launch_time
		inst['image_id'] = i.image_id
		inst['monitored'] = i.monitored	
		inst['platform'] = i.platform
		inst['root_device_type'] = i.root_device_type
		inst['spot_instance_request_id'] = i.spot_instance_request_id
		inst['ip_address'] = i.ip_address
		inst['interfaces'] = i.interfaces
		inst['lifecycle'] = i.interfaces
		inst['interfaces'] = i.interfaces

		groups = list()

		for sec_group in i.groups:
			groups.append(sec_group.name)

		inst['groups'] = groups	

		image_info = ec2_conn.get_image(i.image_id)
	
		if "Linux" in image_info.description or i.platform ==None :
			inst['os'] = EC2_OS_TYPES[0]
		else:
			inst['os'] = EC2_OS_TYPES[1]

		instances_list.append(inst)

	return instances_list
	


def get_regional_instances(region_name = ""):

	"""Get instances from a specific region or else the default will be used.
	
		:param region: The region to use.
		:type region: str.
		:returns: list -- a list of instances for a specific (or the default) region.		
		
	"""
	
	if len(region_name) > 0:
		region = boto.ec2.get_region(region_name,aws_access_key_id=AWS_ACCESS_KEY_ID,aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
	else:
		region = None
		
	conn = connec_to_awd_ec2(region)	
	instances = get_ec2connection_instances(conn)

	return instances
	


def get_all_instances():

	"""Get all user's instances (from all regions).
	
		:returns: list -- a list of instances.		
		
	"""

	all_instances = []
	
	# get all regions
	regions = boto.ec2.regions(aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

	# get instances per region
	for region in regions:
	
		conn = connect_to_aws_ec2(region)	
		instances = get_ec2connection_instances(conn)

		all_instances.extend(instances)

	return all_instances

	

def get_instance_metric(start, end, step_size, metric_name, instance_id, region_name="us-west-1"):

	"""A wrapper function for getting the values of a metric for an instance over a time period.
	
		:param start: start time of observation.
		:type start: datetime.
		:param end: end time of observation.
		:type end: datetime.
		:param step_size: the length of each period
		:type step_size: int.
		:param metric_name: the metric's name.
		:type metric_name: str
		:param instance_id: the instance observerd id.
		:type instance_id: int
		:param region_name: the region's name.
		:type region_name: str
		:returns: datapoints -- datapoints of the metric values.		
		
	"""
	
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



def get_all_instances_metric(start, end, step_size, metric_name, instances):

	"""A wrapper function for getting the values of a metric for a set of instances instance over a time period.
	
		:param start: start time of observation.
		:type start: datetime.
		:param end: end time of observation.
		:type end: datetime.
		:param step_size: the length of each period
		:type step_size: int.
		:param metric_name: the metric's name.
		:type metric_name: str
		:param instance_id: list of instances.
		:type instance_id: list.
		:returns: datapoints -- datapoints of the metric values.		
		
	"""

	metric_datapoints_array = list()
	
	for instance in instances:
		stats = get_instance_metric(start, end, step_size, metric_name, instance["id"], instance["region"])
		metric_datapoints_array.append(stats)
	
	return metric_datapoints_array



def datapoints_to_signal(metric_datapoints):

	"""Converts statistics datapoints to more easier handled signal.
	
		:param metric_datapoints: datapoints of the metric values.
		:type metric_datapoints: datapoints.
		:returns: list -- a list containing all datapoint's data.
		
	"""
	
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

	

def aggregate_metric(metric_datapoints, operation='Average'):

	"""Calculates an aggregated value of received signal.
	
		:param metric_datapoints: datapoints of the metric values.
		:type metric_datapoints: datapoints.
		:param operation: type of aggregation operation to performed.
		:type operation: str.
		:returns: float -- aggregated value.		
		
	"""

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



def get_instances_workload(instances, workload_datapoints_array, param = 'Average'):

	"""Calculates the workload percentage of the given instances, assuming that the given array contains the EC2 utilization of these instance 
		for a particular time period and that an aggregator parameter is used.
		
		:param instances: a list of instances.
		:type instances: list.
		:param workload_datapoints_array: a list of EC2 utilization datapoints for all input instances.
		:type workload_datapoints_array: list.
		:param param: type of aggregation operation to performed.
		:type param: str.
		:returns: list -- aggregated value.		
		
	"""
	
	workload = []
	workload_percentage = []
        
	for workload_datapoints in workload_datapoints_array:
		workload.append(aggregate_metric(workload_datapoints, param))

	capacity = get_instances_capacity(instances)

	for i in range(len(workload)):
		workload_percentage.append((workload[i]/100)*capacity[i])
	
	return workload_percentage
	


def get_capacity_per_machine_type():

	"""Gets the capacity of each machine type (in EC2).
	
		:returns: dict -- the capacity of each machine type (in EC2).		
		
	"""

	data = ec2_capacity.get_ec2_instances_capacity()

	capacity = {}
	for c in data:
		capacity[c['type']] = c['compute_units']*c['virtual_cores']

	return capacity



def get_instances_cost(instances):

	"""Gets input instances' cost.
	
		:param instances: a list of instance types.
		:type instances: list.
		:returns: list -- list of cost for each instance type.
				
	"""

	cost = []
	
	for instance in instances:	
		price = ec2_pricing.get_ec2_ondemand_instances_prices(filter_region=instance['region'],filter_instance_type=instance['type'],filter_os_type=instance['os'])
		cost.append(price['regions'][0]['instanceTypes'][0]['price'])

	return cost



def get_instances_capacity(instances,filter=None):

	"""Gets the capacity of each instance (and the corresponding machine type) (in EC2).
	
		:param instances: a list of instance types.
		:type instances: list.
		:returns: list -- list of cost for each instance type.		
		
	"""

	capacity = []

	c = get_capacity_per_machine_type()
	
	for instance in instances:
		if filter==None or instance[filter['param_name']] == filter['param_value']:
			capacity.append(c[instance['type']])

	return capacity



def get_instance_types_count():

	"""Gets the number of different instance types, considering type, os and region.
	
		:returns: int -- number of different instance types.
		 	
	"""

	return len(EC2_INSTANCE_TYPES)*len(EC2_REGIONS)*len(EC2_OS_TYPES)



def get_all_instance_types():

	"""Gets information for all different instance types, including type, os and region.
	
		:returns: list -- list of all different instance types.
		
	"""

	all_instance_type = []

        for ins_type in EC2_INSTANCE_TYPES:
                for region in EC2_REGIONS:
                        for os in EC2_OS_TYPES:
                                all_instance_type.append({"type":str(ins_type),"region":str(region),"os":str(os)})

	return all_instance_type



def get_instance_types_costs():

	"""Get all instance types costs.
	
		:returns: list -- list of all different instance types's costs.
	"""

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



def get_instance_types_capacities():

	"""Get all instance types computational capacities.
	
		:returns: list -- list of all different instance types's capacities.
		
	"""

	capacity = []
	
	cap = get_capacity_per_machine_type()

	for ins_type in EC2_INSTANCE_TYPES:
		for region in EC2_REGIONS:
			for os in EC2_OS_TYPES:
				capacity.append(cap[ins_type])

	return capacity	



def get_all_amis(defined_filters=None):
	
	"""Get all AMIs and their related information.
	
		:param defined_filters: Optional filters that can be used to limit the results returned (provided by boto). 
		:type defined_filters: dict.
		:returns: list -- list of dictionaries, where each dictionary contains info for each AMI.
		
	"""
	
	all_amis = []
	
	# get all regions
	regions = boto.ec2.regions(aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

	for region in regions:
	
		conn = connect_to_aws_ec2(region)	
		
		amis = conn.get_all_images(owners=['self'],filters=defined_filters)

		for ami in amis:
			
			ami_details= {}
															
			ami_details['id'] = ami.id
			ami_details['region']=region.name
			ami_details['location'] = ami.location
			ami_details['state'] = ami.state
			ami_details['ownerId'] = ami.ownerId
			ami_details['owner_alias'] = ami.owner_alias
			ami_details['is_public'] = ami.is_public
			ami_details['architecture'] = ami.architecture
			ami_details['platform'] = ami.platform
			ami_details['type'] = ami.type
			ami_details['kernel_id'] = ami.kernel_id
			ami_details['ramdisk_id'] = ami.ramdisk_id
			ami_details['name'] = ami.name
			ami_details['description'] = ami.description 
			ami_details['product_codes'] = ami.product_codes
			ami_details['block_device_mapping'] = ami.block_device_mapping
			ami_details['root_device_type'] = ami.root_device_type	
			ami_details['root_device_name'] = ami.root_device_name
			ami_details['virtualization_type'] = ami.virtualization_type
			ami_details['hypervisor'] = ami.hypervisor
			ami_details['instance_lifecycle'] = ami.instance_lifecycle
			
			all_amis.append(ami_details)
				
	return all_amis

	

def get_all_elastic_ips(defined_filters=None):
	
	"""Get all Elastic IP's (EC2 or VPC).
	 
		:param defined_filters: Optional filters that can be used to limit the results returned (provided by boto). 
		:type defined_filters: dict.
		:returns: list -- list of dictionaries, where each dictionary contains info for each elastic IP.
		
	"""	
	
	all_elastic_ips = []
	
	# get all regions
	regions = boto.ec2.regions(aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

	for region in regions:
	
		conn = connect_to_aws_ec2(region)	
		
		elastic_ips = conn.get_all_addresses(filters=defined_filters)

		for ip in elastic_ips:
			
			ip_details = {}												

			ip_details['region']=region.name
			ip_details['public_ip'] = ip.public_ip
			ip_details['instance_id'] = ip.instance_id
			ip_details['domain'] = ip.domain
			ip_details['allocation_id'] = ip.allocation_id
			ip_details['association_id'] = ip.association_id 
			
			#The next attributes are valid only for VPC address , for EC2 address ( domain=standard) they are not defined
			if ip.domain=="standard": 
				ip_details['network_interface_id'] = None
				ip_details['network_interface_owner_id'] = None
				ip_details['private_ip_address'] = None
			else: #valid only for VPC 
				ip_details['network_interface_id'] = ip.network_interface_id
				ip_details['network_interface_owner_id'] = ip.network_interface_owner_id
				ip_details['private_ip_address'] = ip.private_ip_address

			all_elastic_ips.append(ip_details)
			
				
	return all_elastic_ips



def get_all_security_groups(defined_filters=None):
	
	"""Get all Security Groups.
	 
		:param defined_filters: Optional filters that can be used to limit the results returned (provided by boto). 
		:type defined_filters: dict.
		:returns: list -- list of dictionaries, where each dictionary contains info for each security group.
		
	"""
	
	all_security_groups = []
	
	# get all regions
	regions = boto.ec2.regions(aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

	for region in regions:
	
		conn = connect_to_aws_ec2(region)	
		
		security_groups = conn.get_all_security_groups(filters=defined_filters)

        
		for group in security_groups:
						
			security_group = {}												
				
			security_group['ip'] = group.id
			security_group['owner_id'] = group.owner_id
			security_group['name'] = group.name
			security_group['description'] = group.description
			security_group['vpc_id'] = group.vpc_id
			security_group['rules'] = group.rules 
			security_group['rules_egress'] = group.rules_egress 
			security_group['region']=region.name
	
			all_security_groups.append(security_group)
		
				
	return all_security_groups

	

def get_all_key_pairs(defined_filters=None):

	"""Get all Key Pairs.
	 
		:param defined_filters: Optional filters that can be used to limit the results returned (provided by boto). 
		:type defined_filters: dict.
		:returns: list -- list of dictionaries, where each dictionary contains info for each key pair.
		
	"""
		
	all_key_pairs = []
	
	# get all regions
	regions = boto.ec2.regions(aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

	for region in regions:
	
		conn = connect_to_aws_ec2(region)	
		
		key_pairs = conn.get_all_key_pairs(filters=defined_filters)

		for key in key_pairs:
		
			key_pair = {}
		
			key_pair['name'] = key.name
			key_pair['fingerprint'] = key.fingerprint
			key_pair['material'] = key.material
			key_pair['region']=region.name
	
			all_key_pairs.append(key_pair)
		
				
	return all_key_pairs



def get_all_bundle_tasks(defined_filters=None):
	
	"""Get all Bundle Tasks. 
	
		:param defined_filters: Optional filters that can be used to limit the results returned (provided by boto). 
		:type defined_filters: dict.
		:returns: list -- list of dictionaries, where each dictionary contains info for each bundle task.
		
	"""
	
	all_bundle_tasks = []
	
	# get all regions
	regions = boto.ec2.regions(aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

	for region in regions:
	
		conn = connect_to_aws_ec2(region)	
		
		tasks = conn.get_all_bundle_tasks(filters=defined_filters)
 	 		
		for task in tasks:
		
			bundle_task = {}
		
			bundle_task['id'] = task.id
			bundle_task['instance_id'] = task.instance_id
			bundle_task['progress'] = task.progress
			bundle_task['start_time'] = task.start_time
			bundle_task['state'] = task.state
			bundle_task['bucket'] = task.bucket
			bundle_task['prefix'] = task.prefix
			bundle_task['upload_policy'] = task.upload_policy
			bundle_task['upload_policy_signature'] = task.upload_policy_signature
			bundle_task['update_time'] = task.update_time
			bundle_task['code'] = task.code
			bundle_task['message'] = task.message
			bundle_task['region'] = region.name
		
			all_bundle_tasks.append(bundle_task)
		
				
	return all_bundle_tasks



def get_all_volumes(defined_filters=None):

	"""Get volumes
		:param defined_filters: Optional filters that can be used to limit the results returned (provided by boto). 
		:type defined_filters: dict.
		:returns: list -- list of dictionaries, where each dictionary contains info for each volume
	"""

	all_volumes = []
	
	# get all regions
	regions = boto.ec2.regions(aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

	for region in regions:
	
		conn = connect_to_aws_ec2(region)	
		
		volumes = conn.get_all_volumes(filters=defined_filters)
 	 	
 	 	
		for volume in volumes:
		
			vol = {}
		
			vol['id'] = volume.id
			vol['create_time'] = volume.create_time
			vol['status'] = volume.status
			vol['size'] = volume.size
			vol['snapshot_id'] = volume.snapshot_id
			vpl['type'] = volume.type
			vol['region'] = region.name
		    
			all_volumes.append(vol)
		    
		    	
	return all_volumes



def get_all_snapshots(defined_filters=None):

	"""Get Snapshots.
	
		:param defined_filters: Optional filters that can be used to limit the results returned (provided by boto). 
		:type defined_filters: dict.
		:returns: list -- list of dictionaries, where each dictionary contains info for each snapshot.
		
	"""

	all_snapshots = []
	
	# get all regions
	regions = boto.ec2.regions(aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

	for region in regions:
	
		conn = connect_to_aws_ec2(region)	
		
		snapshots = conn.get_all_snapshots(owner='self',filters=defined_filters)
 	 	 	 	 	
		for snapshot in snapshots:
		
			snap = {}
        
			snap['id'] = snapshot.id
			snap['volume_id'] = snapshot.volume_id 
			snap['status'] = snapshot.status
			snap['progress'] = snapshot.progress
			snap['start_time'] = snapshot.start_time 
			snap['owner_id'] = snapshot.owner_id
			snap['owner_alias'] = snapshot.owner_alias
			snap['volume_size'] = snapshot.volume_size
			snap['description'] = snapshot.description			
			snap['region'] = region.name
		   
			all_snapshots.append(snap)
		    
	return all_snapshots



def get_all_tags(defined_filters=None):

	"""Retrieve all the metadata tags from all regions.
	
		:param defined_filters: Optional filters that can be used to limit the results returned (provided by boto). 
		:type defined_filters: dict.
		:returns: list -- list of dictionaries, where each dictionary contains info for the metadata tags for each region.
		
	"""
	
	all_tags = []
	
	# get all regions
	regions = boto.ec2.regions(aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

	for region in regions:
	
		conn = connect_to_aws_ec2(region)	
		
		tags = conn.get_all_tags(filters=defined_filters)
 	 	 	 	 	
		for tag in tags:
		
			tag_data = {}
        		 
			tag_data['res_id'] = tag.res_id
			tag_data['res_type'] = tag.res_type 
			tag_data['name'] = tag.name
			tag_data['value'] = tag.value
			tag_data['region'] = region.name
		    
			all_tags.append(tag_data)
		    
	return all_tags

		

def get_all_spot_instance_requests(defined_filters=None):

	"""Get all spot requests.
	
		:param defined_filters: Optional filters that can be used to limit the results returned (provided by boto). 
		:type defined_filters: dict.
		:returns: list -- list of dictionaries, where each dictionary contains info for each spot request.
		
	"""
	
	all_spot_requests = []
	
	# get all regions
	regions = boto.ec2.regions(aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

	for region in regions:
	
		conn = connect_to_aws_ec2(region)	
				
		spot_requests = conn.get_all_spot_instance_requests(filters=defined_filters)
 	 	 	
		for spot_request in spot_requests:
		
			request = {}
       		
			request['id'] = spot_request.id
			request['price'] = spot_request.price 
			request['type'] = spot_request.type
			request['state'] = spot_request.state
			request['fault'] = spot_request.fault
			request['valid_from'] = spot_request.valid_from
			request['valid_until'] = spot_request.valid_until 
			request['launch_group'] = spot_request.launch_group
			request['launched_availability_zone'] = spot_request.launched_availability_zone
			request['product_description'] = spot_request.product_description
			request['availability_zone_group'] = spot_request.availability_zone_group
			request['create_time'] = spot_request.create_time
			request['launch_specification'] = spot_request.launch_specification
			request['instance_id'] = spot_request.instance_id
			request['status'] = spot_request.status
			request['region'] = region.name
						
			all_spot_requests.append(request)
		    
	return all_spot_requests



def get_all_spot_instances(defined_filters=None):

	"""Get all spot instances.
	
		:param defined_filters: Optional filters that can be used to limit the results returned (provided by boto). 
		:type defined_filters: dict.
		:returns: list -- list of all spot instances.
		
	"""

	all_spot_instances = []
	
	# get all regions
	regions = boto.ec2.regions(aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

	# get spot instances per region
	for region in regions:
	
		conn = connect_to_aws_ec2(region)	
		
		spot_instances = get_ec2connection_instances(conn,{'instance-lifecycle':'spot'})

		all_spot_instances.extend(spot_instances)

	return all_spot_instances



def get_all_reserved_instances(defined_filters=None):

	"""Get all reserved instances.
	
		:param defined_filters: Optional filters that can be used to limit the results returned (provided by boto). 
		:type defined_filters: dict.
		:returns: list -- list of dictionaries, where each dictionary contains info for each reserved instance.
		
	"""

	all_reserved_instances = []
	
	# get all regions
	regions = boto.ec2.regions(aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

	for region in regions:
	
		conn = connect_to_aws_ec2(region)	

		reserved_instances = conn.get_all_reserved_instances(filters=defined_filters)
				 	 	 	
		for reserved_instance in reserved_instances:
		
			request = {}
       		
			instance['id'] = reserved_instance.id 
			instance['instance_type'] = reserved_instance.instance_type 
			instance['availability_zone'] = reserved_instance.availability_zone
			instance['duration'] = reserved_instance.duration
			instance['fixed_price'] = reserved_instance.fixed_price
			instance['usage_price'] = reserved_instance.usage_price
			instance['description'] = reserved_instance.description
			instance['instance_tenancy'] = reserved_instance.instance_tenancy
			instance['currency_code'] = reserved_instance.currency_code
			instance['offering_type'] = reserved_instance.offering_type
			instance['recurring_charges'] = reserved_instance.recurring_charges
			instance['pricing_details'] = reserved_instance.pricing_details
			instance['region'] = region.name
			
			all_reserved_instances.append(instance)
		    
	return all_reserved_instances



def get_all_buckets():

	"""Get all S3 buckets.
	
		:returns: list -- list of dictionaries, where each dictionary contains info for each S3 bucket.
		
	"""

	all_s3_buckets = []	
		
	conn = S3Connection(aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
	
	s3_buckets = conn.get_all_buckets()
				 	 			 	 
	for s3_bucket in s3_buckets:
        	
		bucket = {}
		tag_keys = []
		tag_values = []
		counter = 0
		bucket_size_MB = 0

	
		##    	
		tags = s3_bucket.get_tags()
		
		for tag_set in tags:
			for tag in tag_set:
				tag_keys.append(tag.key)
				tag_values.append(tag.value)
		
		###
		contents = s3_bucket.list() 
		
		last_modified_datetime = None
		last_modified = None
	
		
		for content in contents:

			bucket_size_MB = bucket_size_MB + ( content.size/(1024*1024) )
			counter = counter +1
		
			if last_modified_datetime == None:
				last_modified_datetime = isodate.parse_datetime(content.last_modified)
				last_modified = content.last_modified
			else:
				
				if isodate.parse_datetime(content.last_modified) > last_modified_datetime :
					last_modified_datetime = isodate.parse_datetime(content.last_modified)
					last_modified = content.last_modified
	
		bucket['name'] = s3_bucket.name				
		bucket['keys'] = tag_keys
		bucket['values'] = tag_values
		bucket['bucket_size_MB'] = bucket_size_MB
		bucket['number_of_files'] = counter
		bucket['create_date'] = s3_bucket.creation_date
		bucket['last_modified'] = last_modified
		
		## If region is empty string then it is interpreted as the US Classic Region
		bucket['region'] = s3_bucket.get_location()
			
		all_s3_buckets.append(bucket)
		    
	return all_s3_buckets



def get_buckets_storage_pricing_info():

	"""Returns for for each S3 bucket its name, its size (in MB) for each storage class and its region
	
		:returns: list -- list of dictionaries, where each dictionary contains pricing info for each S3 bucket
	"""

	all_s3_buckets = []    
		     
	conn = S3Connection(aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
		 
	s3_buckets = conn.get_all_buckets()
                                        
	for s3_bucket in s3_buckets:
            
		bucket = {}
        
		storage_class_size_MB = { "STANDARD":0,"REDUCED_REDUNDANCY":0,"GLACIER":0 }
        
		contents = s3_bucket.list() 
                
		for content in contents:
			storage_class_size_MB[content.storage_class] = storage_class_size_MB[content.storage_class] + content.size/(1024*1024) 
            
		bucket['name'] = s3_bucket.name                
		bucket['size_per_storage_class'] = storage_class_size_MB
		bucket['region'] = s3_bucket.get_location()
            
		all_s3_buckets.append(bucket)
            
	return all_s3_buckets
    
    
    
