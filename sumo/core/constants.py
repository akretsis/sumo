EC2_REGIONS = [
	"us-east-1", 
	"us-west-1", 
	"us-west-2", 
	"eu-west-1", 
	"ap-southeast-1", 
	"ap-northeast-1", 
	"sa-east-1"
]

EC2_INSTANCE_TYPES = [
	"t1.micro",
	"m1.small",
	"m1.medium",
	"m1.large",
	"m1.xlarge",
	"m2.xlarge",
	"m2.2xlarge",
	"m2.4xlarge",
	"c1.medium",
	"c1.xlarge"
	#"cc1.4xlarge"
	#"cc2.8xlarge",
	#"cg1.4xlarge",
	#"hi1.4xlarge"
]

EC2_INSTANCE_STATES=[

	{'code':0,'name':"pending"},
	{'code':16,'name':"running"},
	{'code':32,'name':"shutting-down"},
	{'code':48,'name':"terminated"},
	{'code':64,'name':"stopping"},
	{'code':80,'name':"stopped"}

]

EC2_OS_TYPES = [
	"linux",
	"mswin"
]

EC2_UTILIZATION_TYPES = [
	"light",
	"medium",
	"heavy"
]

EC2_TERM_TYPES = [
	"1year",
	"3year"
]

JSON_NAME_TO_EC2_REGIONS_API = {
	"us-east" : "us-east-1",
	"us-east-1" : "us-east-1", 
	"us-west" : "us-west-1", 
	"us-west-1" : "us-west-1", 
	"us-west-2" : "us-west-2", 
	"eu-ireland" : "eu-west-1", 
	"eu-west-1" : "eu-west-1",
	"apac-sin" : "ap-southeast-1", 
	"ap-southeast-1" : "ap-southeast-1",
	"apac-tokyo" : "ap-northeast-1", 
	"ap-northeast-1" : "ap-northeast-1",
	"sa-east-1" : "sa-east-1"
}

EC2_REGIONS_API_TO_JSON_NAME = {
	"us-east-1" : "us-east", 
	"us-west-1" : "us-west", 
	"us-west-2" : "us-west-2", 
	"eu-west-1" : "eu-ireland", 
	"ap-southeast-1" : "apac-sin", 
	"ap-northeast-1" : "apac-tokyo", 
	"sa-east-1" : "sa-east-1"	
}

INSTANCES_ON_DEMAND_URL = "http://aws.amazon.com/ec2/pricing/pricing-on-demand-instances.json"
INSTANCES_RESERVED_LIGHT_UTILIZATION_LINUX_URL = "http://aws.amazon.com/ec2/pricing/ri-light-linux.json"
INSTANCES_RESERVED_LIGHT_UTILIZATION_WINDOWS_URL = "http://aws.amazon.com/ec2/pricing/ri-light-mswin.json"
INSTNACES_RESERVED_MEDIUM_UTILIZATION_LINUX_URL = "http://aws.amazon.com/ec2/pricing/ri-medium-linux.json"
INSTANCES_RESERVED_MEDIUM_UTILIZATION_WINDOWS_URL = "http://aws.amazon.com/ec2/pricing/ri-medium-mswin.json"
INSTANCES_RESERVED_HEAVY_UTILIZATION_LINUX_URL = "http://aws.amazon.com/ec2/pricing/ri-heavy-linux.json"
INSTANCES_RESERVED_HEAVY_UTILIZATION_WINDOWS_URL = "http://aws.amazon.com/ec2/pricing/ri-heavy-mswin.json"

INSTANCES_ON_DEMAND_FILENAME = "data/json/pricing-on-demand-instances.json"
INSTANCES_RESERVED_LIGHT_UTILIZATION_LINUX_FILENAME = "data/json/ri-light-linux.json"
INSTANCES_RESERVED_LIGHT_UTILIZATION_WINDOWS_FILENAME = "data/json/ri-light-mswin.json"
INSTNACES_RESERVED_MEDIUM_UTILIZATION_LINUX_FILENAME = "data/json/ri-medium-linux.json"
INSTANCES_RESERVED_MEDIUM_UTILIZATION_WINDOWS_FILENAME = "data/json/ri-medium-mswin.json"
INSTANCES_RESERVED_HEAVY_UTILIZATION_LINUX_FILENAME = "data/json/ri-heavy-linux.json"
INSTANCES_RESERVED_HEAVY_UTILIZATION_WINDOWS_FILENAME = "data/json/ri-heavy-mswin.json"
INSTANCES_CAPACITY_FILENAME = "data/json/ec2-instances-capacity.json"

INSTANCES_RESERVED_OS_TYPE_BY_URL = {
	INSTANCES_RESERVED_LIGHT_UTILIZATION_LINUX_URL : "linux",
	INSTANCES_RESERVED_LIGHT_UTILIZATION_WINDOWS_URL : "mswin", 
	INSTNACES_RESERVED_MEDIUM_UTILIZATION_LINUX_URL : "linux",
	INSTANCES_RESERVED_MEDIUM_UTILIZATION_WINDOWS_URL : "mswin",
	INSTANCES_RESERVED_HEAVY_UTILIZATION_LINUX_URL : "linux",
	INSTANCES_RESERVED_HEAVY_UTILIZATION_WINDOWS_URL  : "mswin"
}

INSTANCES_RESERVED_UTILIZATION_TYPE_BY_URL = {
	INSTANCES_RESERVED_LIGHT_UTILIZATION_LINUX_URL : "light",
	INSTANCES_RESERVED_LIGHT_UTILIZATION_WINDOWS_URL : "light", 
	INSTNACES_RESERVED_MEDIUM_UTILIZATION_LINUX_URL : "medium",
	INSTANCES_RESERVED_MEDIUM_UTILIZATION_WINDOWS_URL : "medium",
	INSTANCES_RESERVED_HEAVY_UTILIZATION_LINUX_URL : "heavy",
	INSTANCES_RESERVED_HEAVY_UTILIZATION_WINDOWS_URL  : "heavy"	
}

DEFAULT_CURRENCY = "USD"

INSTANCE_TYPE_MAPPING = {
	"stdODI" : "m1",
	"uODI" : "t1",
	"hiMemODI" : "m2",
	"hiCPUODI" : "c1",
	"clusterComputeI" : "cc1",
	"clusterGPUI" : "cc2",
	"hiIoODI" : "hi1",

	"secgenstdODI":"m2",

	# Reserved Instance Types
	"stdResI" : "m1",
	"uResI" : "t1",
	"hiMemResI" : "m2",
	"hiCPUResI" : "c1",
	"clusterCompResI" : "cc1",
	"clusterGPUResI" : "cc2",
	"hiIoResI" : "hi1"
}

INSTANCE_SIZE_MAPPING = {
	"u" : "micro",
	"sm" : "small",
	"med" : "medium",
	"lg" : "large",
	"xl" : "xlarge",
	"xxl" : "2xlarge",
	"xxxxl" : "4xlarge",
	"xxxxxxxxl" : "8xlarge"
}

# The unit of the metric.
UNIT_OF_METRIC = {
	"CPUUtilization": "Percent",
	"NetworkIn": "Bytes",
	"NetworkOut": "Bytes"
}


# The namespace of the metric.
NAMESPACE_OF_METRIC = {
	"CPUUtilization": "AWS/EC2",
	"NetworkIn": "AWS/EC2",
	"NetworkOut": "AWS/EC2"	
}

# DB & table name
DB_NAME = "computeforce.db"
TABLE_NAME_SIGNALS = "statistic_signals"
