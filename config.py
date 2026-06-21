##configs

GRAPH      = True  #whether to run the matplotlib grpahing and subquent experimental analysis - default on
DARK_MODE  = True
DEBUG_MODE = False #whether to include debugging messages in the log - default off


## step factors (more = slower, more accurate)

coarse_factor = 0.4  #factor for the step rate of the coarse calculations (suggest between 0.3 and 0.6)
fine_factor   = 20   #factor for the step rate of the fine calculations (suggest 20 at least)
graph_factor  = 0.4  #factor for the step rate of the graph (suggest between 0.1 and 0.5)

#shared paths
DEFAULT_ROCKETS_PATH = "../rockets/default_rockets.json"
CUSTOM_ROCKETS_PATH = "../rockets/custom_rockets.json"
TRAJECTORY_TARGETS_PATH = "scripts/trajectory_targets.json"