import json
from prettytable import PrettyTable
from sumo.core.constants import *

#######################
# Print instances data in a table
#######################
def print_instances_basic_data(instances):

	instances_table = PrettyTable()

	try:			
		instances_table.set_field_names(["id", "type", "os", "region", "state"])
	except AttributeError:
		instances_table.field_names = ["id", "type", "os", "region", "state"]

	try:
		instances_table.aligns[-1] = "l"
	except AttributeError:
		instances_table.align["state"] = "l"
	
	for i in instances:
		instances_table.add_row([i['id'], i['type'], i['os'], i['region'], i['state']])

	print instances_table


#######################
#
#######################
def date_handler(obj):
	return obj.isoformat() if hasattr(obj,'isoformat') else obj


#######################
# Returns input data in json format
#######################
def parse_json(data):

	try:
		data = json.dumps(data, default=date_handler)		
		json_data = json.loads(data)

		return json_data

	except ValueError,err:
		print "Decode JSON:",err


#######################
# Get all the ids of the input instances
#######################
def get_instance_id(instances):

	ids = []
	instances_json = parse_json(instances)
	
	for inst in instances_json:
		ids.append(inst["id"])
	
	return ids
