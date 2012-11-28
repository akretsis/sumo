import sqlite3

from sumo.core.constants import *

#######################
# Init compute force db 
#######################
def init_computeforce_db():

	conn = sqlite3.connect("./" +DB_NAME)
 
	cursor = conn.cursor()
	 
	cursor.execute("CREATE TABLE IF NOT EXISTS " + TABLE_NAME_POINTS + " (epoch integer, instance_id text, metric text, average double, maximum double, minimum double)")

	cursor.execute("CREATE TABLE IF NOT EXISTS " + TABLE_NAME_SIGNALS + " (start_epoch integer, end_epoch integer, instance_id text, metric text, signal text)")

	conn.close()

	
#######################
# Add metric signal to db
#######################
def add_metric_signal_to_db(start, end, metric, instance_id, signal):

	conn = sqlite3.connect("./" +DB_NAME)
	cursor = conn.cursor()

	start_epoch = start.strftime("%s")
	end_epoch = end.strftime("%s")

	query = "INSERT INTO " + TABLE_NAME_SIGNALS + " (start_epoch, end_epoch, instance_id, metric, signal) VALUES(" +start_epoch+ ", "+ end_epoch+", '" +instance_id+ "', '" +metric+ "', \"" + str(signal) + "\")"

	cursor.execute(query)

	conn.commit()
	conn.close()
				

#######################
# Get a metric's signals from db
#######################
def get_metric_signals_from_db(start, end, metric, instance_id):

	conn = sqlite3.connect("./" +DB_NAME)
	cursor = conn.cursor()

	start_epoch = start.strftime("%s")
	end_epoch = end.strftime("%s")

	query = "SELECT * FROM " + TABLE_NAME_SIGNALS + " WHERE start_epoch > "+str(start_epoch)+ " AND end_epoch < "+str(end_epoch)+ " AND instance_id = '" +instance_id+ "' AND metric = '"+metric+"'"

	cursor.execute(query)
	data = cursor.fetchall()
	
	conn.close()

	metric_signals = eval(data)

	return metric_signals


#######################
# Add metric datapoints to db
#######################
def add_metric_datapoints_to_db(datapoints):

	signal = datapoints_to_signal(datapoints)

	db.init_computeforce_db()

	db.add_metric_signal_to_db(start, end, metric_name, instance_id, signal)
