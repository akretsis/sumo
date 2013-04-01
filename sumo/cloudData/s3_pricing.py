
import urllib2
import argparse
import os.path

import sumo.core.constants as const 

try:
	import simplejson as json
except ImportError:
	import json


def _load_data(url):
	
	try:
	
		f = urllib2.urlopen(url)
		return json.loads(f.read())
	
	except IOError, error:

		path=os.path.dirname(__file__)

		if url == const.STORAGE_S3_URL:
					if len(path)>0:
						f = open("%s/%s"%(path,const.STORAGE_S3_FILENAME), "r")
					else:
						f = open(const.STORAGE_S3_FILENAME, "r")
						
			
		return json.loads(f.read())


#
#data_size should expresed in GB
#
def map_storage_size_to_tier(data_size):

	data_size_TB = float(data_size)/1024

	if data_size_TB <= 1:
		return "firstTBstorage"
	elif data_size_TB <= 50 :
		return "next49TBstorage"
	elif data_size_TB <= 500 :
		return "next450TBstorage"
	elif data_size_TB <= 1000 :	
		return "next500TBstorage"
	elif data_size_TB <= 5000 :	
		return "next4000TBstorage"
	elif data_size_TB > 5000 : 	
		return "over5000TBstorage"


#
# data_size sholud expressed in GB
#
def compute_s3_storage_price(region,storage_class,data_size):

	storage_price = 0.0

	storage_types = { "STANDARD":"storage", "REDUCED_REDUNDANCY":"reducedRedundancyStorage", "GLACIER":"glacierStorage" } 

	if data_size > 0:
		
		data = _load_data(const.STORAGE_S3_URL)

		for r in data["config"]["regions"]:
			
			if r["region"]==region:
				
				tier_name = map_storage_size_to_tier(data_size)
				
				for tier in r["tiers"]:
				
					if tier["name"]==tier_name:
						
						for storage in tier["storageTypes"]:
							if storage["type"] == storage_types[storage_class]:
								storage_price = float(storage["prices"]["USD"])
								
	
	return storage_price


#
#
#
def get_s3_storage_prices(filter_region=None):

	result_regions = []
	
	currency = "USD"
	rate = "perGB"
	
	result = {
		"config" : {
			"currency" : currency,
			"rate" : rate
		},
		"regions" : result_regions
	}

	data = _load_data(const.STORAGE_S3_URL)
	
	if "config" in data and data["config"] and "regions" in data["config"] and data["config"]["regions"]:

		for r in data["config"]["regions"]:
					
			if "region" in r and r["region"]:
				
				if filter_region!=None and filter_region != r["region"]:
					continue
				
				result_regions.append(r)
				
	return result