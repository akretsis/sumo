# Copyright (c) 2012 Eran Sandler (eran@sandler.co.il),  http://eran.sandler.co.il,  http://forecastcloudy.net
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

import urllib2
import argparse
import os.path

from sumo.core.constants import *

try:
	import simplejson as json
except ImportError:
	import json


def _load_data(url):
	
	#try:
	
	#	f = urllib2.urlopen(url)
	#	return json.loads(f.read())
	
	#except IOError, error:

		path=os.path.dirname(__file__)

		if url == INSTANCES_RESERVED_LIGHT_UTILIZATION_LINUX_URL:
					if len(path)>0:
						f = open("%s/%s"%(path,INSTANCES_RESERVED_LIGHT_UTILIZATION_LINUX_FILENAME), "r")
					else:
						f = open(INSTANCES_RESERVED_LIGHT_UTILIZATION_LINUX_FILENAME, "r")
						
		elif url == INSTANCES_RESERVED_LIGHT_UTILIZATION_WINDOWS_URL:
					if len(path)>0:
						f = open("%s/%s"%(path,INSTANCES_RESERVED_LIGHT_UTILIZATION_WINDOWS_FILENAME), "r") 
					else:
						f = open(INSTANCES_RESERVED_LIGHT_UTILIZATION_WINDOWS_FILENAME, "r") 
						
		elif url == INSTNACES_RESERVED_MEDIUM_UTILIZATION_LINUX_URL:
					if len(path)>0:
						f = open("%s/%s"%(path,INSTNACES_RESERVED_MEDIUM_UTILIZATION_LINUX_FILENAME), "r") 
					else:
						f = open(INSTNACES_RESERVED_MEDIUM_UTILIZATION_LINUX_FILENAME, "r") 
						
		elif url == INSTANCES_RESERVED_MEDIUM_UTILIZATION_WINDOWS_URL:
					if len(path)>0:	
						f = open("%s/%s"%(path,INSTANCES_RESERVED_MEDIUM_UTILIZATION_WINDOWS_FILENAME), "r") 
					else:
						f = open(INSTANCES_RESERVED_MEDIUM_UTILIZATION_WINDOWS_FILENAME, "r") 
						
		elif url == INSTANCES_RESERVED_HEAVY_UTILIZATION_LINUX_URL:
					if len(path)>0:	
						f = open("%s/%s"%(path,INSTANCES_RESERVED_HEAVY_UTILIZATION_LINUX_FILENAME), "r") 
					else:
						f = open(INSTANCES_RESERVED_HEAVY_UTILIZATION_LINUX_FILENAME, "r") 
						
		elif url == INSTANCES_RESERVED_HEAVY_UTILIZATION_WINDOWS_URL:
					if len(path)>0:	
						f = open("%s/%s"%(path,INSTANCES_RESERVED_HEAVY_UTILIZATION_WINDOWS_FILENAME), "r") 
					else:
						f = open(INSTANCES_RESERVED_HEAVY_UTILIZATION_WINDOWS_FILENAME, "r") 
						
		elif url == INSTANCES_ON_DEMAND_URL:
					if len(path)>0:	
						f = open("%s/%s"%(path,INSTANCES_ON_DEMAND_FILENAME), "r") 
					else:
						f = open(INSTANCES_ON_DEMAND_FILENAME, "r") 
						
		return json.loads(f.read())

		
def get_ec2_reserved_instances_prices(filter_region=None, filter_instance_type=None, filter_os_type=None, filter_utilization_type=None, filter_term_type=None):
	""" Get EC2 reserved instances prices. Results can be filtered by region """

	get_specific_region = (filter_region is not None)
	if get_specific_region:
		filter_region = EC2_REGIONS_API_TO_JSON_NAME[filter_region]
	get_specific_instance_type = (filter_instance_type is not None)
	get_specific_os_type = (filter_os_type is not None)
	get_specific_utilization_type = (filter_utilization_type is not None)
	get_specific_term_type = (filter_term_type is not None)

	currency = DEFAULT_CURRENCY

	urls = [
		INSTANCES_RESERVED_LIGHT_UTILIZATION_LINUX_URL,
		INSTANCES_RESERVED_LIGHT_UTILIZATION_WINDOWS_URL,
		INSTNACES_RESERVED_MEDIUM_UTILIZATION_LINUX_URL,
		INSTANCES_RESERVED_MEDIUM_UTILIZATION_WINDOWS_URL,
		INSTANCES_RESERVED_HEAVY_UTILIZATION_LINUX_URL,
		INSTANCES_RESERVED_HEAVY_UTILIZATION_WINDOWS_URL 
	]

	result_regions = []
	result_regions_index = {}
	result = {
		"config" : {
			"currency" : currency,
		},
		"regions" : result_regions
	}

	for u in urls:
		os_type = INSTANCES_RESERVED_OS_TYPE_BY_URL[u]
		utilization_type = INSTANCES_RESERVED_UTILIZATION_TYPE_BY_URL[u]
		data = _load_data(u)
		if "config" in data and data["config"] and "regions" in data["config"] and data["config"]["regions"]:
			for r in data["config"]["regions"]:
				if "region" in r and r["region"]:
					if get_specific_region and filter_region != r["region"]:
						continue

				region_name = JSON_NAME_TO_EC2_REGIONS_API[r["region"]]
				if region_name in result_regions_index:
					instance_types = result_regions_index[region_name]["instanceTypes"]
				else:
					instance_types = []
					result_regions.append({
						"region" : region_name,
						"instanceTypes" : instance_types
					})
					result_regions_index[region_name] = result_regions[-1]
					
				if "instanceTypes" in r:
					for it in r["instanceTypes"]:
						instance_type = INSTANCE_TYPE_MAPPING[it["type"]]
						if "sizes" in it:
							for s in it["sizes"]:
								instance_size = INSTANCE_SIZE_MAPPING[s["size"]]

								_type = "%s.%s" % (instance_type, instance_size)

								if get_specific_instance_type and _type != filter_instance_type:
									continue

								if get_specific_os_type and os_type != filter_os_type:
									continue

								if get_specific_utilization_type and utilization_type != filter_utilization_type:
									continue
						
								# for prices
								if get_specific_term_type:
									prices = {
										filter_term_type : {
											"hourly" : None,
											"upfront" : None
										}
									}
								else:
									prices = {
										"1year" : {
											"hourly" : None,
											"upfront" : None
										},
										"3year" : {
											"hourly" : None,
											"upfront" : None
										}
									}

								for price_data in s["valueColumns"]:
									price = None
									try:
										price = float(price_data["prices"][currency])
									except ValueError:
										price = None
									if price_data["name"] == "yrTerm1":
										term_type = "1year"
									elif price_data["name"] == "yrTerm1Hourly":
										term_type = "1year"
									elif price_data["name"] == "yrTerm3":
										term_type = "3year"
									elif price_data["name"] == "yrTerm3Hourly":
										term_type = "3year"
									if get_specific_term_type and term_type != filter_term_type:
										continue

									if price_data["name"] == "yrTerm1":
										prices["1year"]["upfront"] = price
									elif price_data["name"] == "yrTerm1Hourly":
										prices["1year"]["hourly"] = price
									elif price_data["name"] == "yrTerm3":
										prices["3year"]["upfront"] = price
									elif price_data["name"] == "yrTerm3Hourly":
										prices["3year"]["hourly"] = price			

								instance_types.append({
									"type" : _type,
									"os" : os_type,
									"utilization" : utilization_type,
									"prices" : prices
								})

	return result

def get_ec2_ondemand_instances_prices(filter_region=None, filter_instance_type=None, filter_os_type=None):
	""" Get EC2 on-demand instances prices. Results can be filtered by region """

	get_specific_region = (filter_region is not None)
	if get_specific_region:
		filter_region = EC2_REGIONS_API_TO_JSON_NAME[filter_region]

	get_specific_instance_type = (filter_instance_type is not None)
	get_specific_os_type = (filter_os_type is not None)

	currency = DEFAULT_CURRENCY

	result_regions = []
	result = {
		"config" : {
			"currency" : currency,
			"unit" : "perhr"
		},
		"regions" : result_regions
	}

	data = _load_data(INSTANCES_ON_DEMAND_URL)
	

	if "config" in data and data["config"] and "regions" in data["config"] and data["config"]["regions"]:
		for r in data["config"]["regions"]:
			if "region" in r and r["region"]:
				if get_specific_region and filter_region != r["region"]:
					continue

				region_name = JSON_NAME_TO_EC2_REGIONS_API[r["region"]]
				instance_types = []

				if "instanceTypes" in r:
					for it in r["instanceTypes"]:
						
						instance_type = INSTANCE_TYPE_MAPPING[it["type"]]
						if "sizes" in it:
							for s in it["sizes"]:
								instance_size = INSTANCE_SIZE_MAPPING[s["size"]]

								for price_data in s["valueColumns"]:
									price = None
									try:
										price = float(price_data["prices"][currency])
									except ValueError:
										price = None

									_type = "%s.%s" % (instance_type, instance_size)

									if get_specific_instance_type and _type != filter_instance_type:
										continue

									if get_specific_os_type and price_data["name"] != filter_os_type:
										continue

									instance_types.append({
										"type" : _type,
										"os" : price_data["name"],
										"price" : price
									})

					result_regions.append({
						"region" : region_name,
						"instanceTypes" : instance_types
					})

		return result

	return None

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


	parser = argparse.ArgumentParser(add_help=True, description="Print out the current prices of EC2 instances")
	parser.add_argument("--type", "-t", help="Show ondemand or reserved instances", choices=["ondemand", "reserved"], required=True)
	parser.add_argument("--filter-region", "-fr", help="Filter results to a specific region", choices=EC2_REGIONS, default=None)
	parser.add_argument("--filter-type", "-ft", help="Filter results to a specific instance type", choices=EC2_INSTANCE_TYPES, default=None)
	parser.add_argument("--filter-os-type", "-fo", help="Filter results to a specific os type", choices=EC2_OS_TYPES, default=None)
	parser.add_argument("--filter-utilization-type", "-fu", help="Filter results to a specific utilization type (onle for reserved instances)", choices=EC2_UTILIZATION_TYPES, default=None)
	parser.add_argument("--filter-term-type", "-fte", help="Filter results to a specific term type (onle for reserved instances)", choices=EC2_TERM_TYPES, default=None)
	parser.add_argument("--format", "-f", choices=["json", "table", "csv"], help="Output format", default="table")

	args = parser.parse_args()

	if args.format == "table":
		try:
			from prettytable import PrettyTable
		except ImportError:
			print "ERROR: Please install 'prettytable' using pip:    pip install prettytable"

	data = None
	if args.type == "ondemand":
		data = get_ec2_ondemand_instances_prices(args.filter_region, args.filter_type, args.filter_os_type)
	elif args.type == "reserved":
		data = get_ec2_reserved_instances_prices(args.filter_region, args.filter_type, args.filter_os_type, args.filter_utilization_type, args.filter_term_type)

	if args.format == "json":
		print json.dumps(data)
	elif args.format == "table":
		x = PrettyTable()

		if args.type == "ondemand":
			try:			
				x.set_field_names(["region", "type", "os", "price"])
			except AttributeError:
				x.field_names = ["region", "type", "os", "price"]

			try:
				x.aligns[-1] = "l"
			except AttributeError:
				x.align["price"] = "l"

			for r in data["regions"]:
				region_name = r["region"]
				for it in r["instanceTypes"]:
					x.add_row([region_name, it["type"], it["os"], none_as_string(it["price"])])
		elif args.type == "reserved":
			try:
				x.set_field_names(["region", "type", "os", "utilization", "term", "price", "upfront"])
			except AttributeError:
				x.field_names = ["region", "type", "os", "utilization", "term", "price", "upfront"]

			try:
				x.aligns[-1] = "l"
				x.aligns[-2] = "l"
			except AttributeError:
				x.align["price"] = "l"
				x.align["upfront"] = "l"
			
			for r in data["regions"]:
				region_name = r["region"]
				for it in r["instanceTypes"]:
					for term in it["prices"]:
						x.add_row([region_name, it["type"], it["os"], it["utilization"], term, none_as_string(it["prices"][term]["hourly"]), none_as_string(it["prices"][term]["upfront"])])

		print x
	elif args.format == "csv":
		if args.type == "ondemand":
			print "region,type,os,price"
			for r in data["regions"]:
				region_name = r["region"]
				for it in r["instanceTypes"]:
					print "%s,%s,%s,%s" % (region_name, it["type"], it["os"], none_as_string(it["price"]))
		elif args.type == "reserved":
			print "region,type,os,utilization,term,price,upfront"
			for r in data["regions"]:
				region_name = r["region"]
				for it in r["instanceTypes"]:
					for term in it["prices"]:
						print "%s,%s,%s,%s,%s,%s,%s" % (region_name, it["type"], it["os"], it["utilization"], term, none_as_string(it["prices"][term]["hourly"]), none_as_string(it["prices"][term]["upfront"]))
