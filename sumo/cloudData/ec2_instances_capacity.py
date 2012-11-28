import urllib2
import argparse
import os.path

from sumo.core.constants import *

try:
	import simplejson as json
except ImportError:
	import json


def _load_data(filename):
	f = open(filename, "r") 
	return json.loads(f.read())

def get_ec2_instances_capacity(filter_instance_type=None):

	get_specific_instance_type = (filter_instance_type is not None)

	base_path=os.path.dirname(__file__)

	if len(base_path)>0:
		filename = "%s/%s"%(base_path,INSTANCES_CAPACITY_FILENAME)
	else:
		filename=INSTANCES_CAPACITY_FILENAME

	data = _load_data(filename)

	instances_capacity = []
	for t in data["capacity"]:
		_type = "%s" % (t["type"])

		if get_specific_instance_type and _type != filter_instance_type:
			continue

		instances_capacity.append(t)

	return instances_capacity

#	return result


if __name__ == "__main__":
	def none_as_string(v):
		if not v:
			return ""
		else:
			return v

	try:
		import argparse 
	except ImportError:
		print "ERROR: You are running Python < 2.7. Please use pip to install argparse:   pip install argparse"


	parser = argparse.ArgumentParser(add_help=True, description="Print out the characteristics of EC2 instances")
	parser.add_argument("--type", "-t", help="Show instance type", choices=["t1.micro",	"m1.small", "m1.medium", "m1.large",	"m1.xlarge",	"m2.xlarge",	"m2.2xlarge",	"m2.4xlarge",	"c1.medium",	"c1.xlarge",	"cc1.4xlarge",	"cc2.8xlarge",	"cg1.4xlarge",	"hi1.4xlarge"], required=False)
	parser.add_argument("--format", "-f", choices=["json", "table", "csv"], help="Output format", default="table")

	args = parser.parse_args()

	if args.format == "table":
		try:
			from prettytable import PrettyTable
		except ImportError:
			print "ERROR: Please install 'prettytable' using pip:    pip install prettytable"

	data = None
	data = get_ec2_instances_capacity(args.type)

	if args.format == "json":
		print json.dumps(data)
	elif args.format == "table":
		x = PrettyTable()

		try:			
			x.set_field_names(["instance type", "compute units", "virtual cores", "memory", "storage"])
		except AttributeError:
			x.field_names = ["instance type", "compute units", "virtual cores", "memory", "storage"]

		try:
			x.aligns[-1] = "l"
		except AttributeError:
			x.align["platform"] = "l"

		for r in data:
			x.add_row([r["type"], r["compute_units"], r["virtual_cores"], r["memory"], r["storage"]])
		print x

	elif args.format == "csv":
			print "instance type,compute virtual cores,memory,storage"
			for r in data:
					print "%s,%s,%s,%s,%s" % (r["type"], r["compute_units"], r["virtual_cores"], r["memory"], r["storage"])

