from sumo.core.constants import *

# 7 elements list, if empty DEFAULT_REGION value will be used
INSTANCE_REGIONS = []

# 6 elements list, if empty DEFAULT_STATE value will be used
INSTANCE_STATES = []

# 2 elements list, if empty DEFAULT_OS_TYPE value will be used
INSTANCE_OS_TYPES = []

# X elements list, if empty DEFAULT_TYPE value will be used
#INSTANCE_TYPES = [0,0,0,0,0,0,0,0.2,0.3,0.5]
INSTANCE_TYPES=[]

# Select random or default data
RANDOM_REGION = 1
RANDOM_STATE = 0
RANDOM_TYPE = 1
RANDOM_OS_TYPE = 1

# Default data
# eu-west-1
DEFAULT_REGION = EC2_REGIONS[3]
# running
DEFAULT_STATE = "running"
# linux
DEFAULT_OS_TYPE = EC2_OS_TYPES[0]
# m1.medium
DEFAULT_TYPE = EC2_INSTANCE_TYPES[2]

# Usage limits
USAGE_LIMITS = {
	"idle":[0,0],
	"low":[1,10],
	"normal":[11,35],
	"medium":[36,69],
	"high":[70,90],
	"very_high":[91,98],
	"exceedable":[99,100],
	"uniform":[0,100]
}

# Byte unit
BYTES_UNIT = 100
