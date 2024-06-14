import re
import uuid
import time
import mysql.connector
import configparser
from cm_api.api_client import ApiResource
import jks
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class XogtaTechBDRTrigger:
    def __init__(self, database_name, policy_number, priority):
        logging.info('Initializing XogtaTechBDRTrigger')

        self.database_name = database_name.strip()
        self.policy_number = policy_number.strip()
        self.priority = priority
        self.job_id = str(uuid.uuid4())
        self.ReceivedTime = time.time()

        logging.info('Validating inputs')
        self.validate_inputs()

        logging.info('Reading configuration')
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.mysql_config = config['mysql']
        self.cloudera_config = config['cloudera']

        logging.info('Loading JCEKS file for MySQL password')
        mysqlkeystore = jks.load_keystore(self.mysql_config['keystore_file'], self.mysql_config['keystore_password'])

        logging.info('Getting MySQL password')
        mysqlpassword = mysqlkeystore.get_secret_key(self.mysql_config['password_alias']).get_clear_key()

        logging.info('Loading JCEKS file for Cloudera Manager password')
        cmkeystore = jks.load_keystore(self.cloudera_config['keystore_file'], self.cloudera_config['keystore_password'])

        logging.info('Getting Cloudera Manager password')
        cmpassword = cmkeystore.get_secret_key(self.cloudera_config['password_alias']).get_clear_key()

        logging.info('Setting MySQL and Cloudera Manager passwords')
        self.mysql_config['password'] = mysqlpassword
        self.cloudera_config['password'] = cmpassword

        logging.info('XogtaTechBDRTrigger initialized')

    def validate_inputs(self):
        logging.info('Validating inputs')
        if not re.match("^[a-zA-Z0-9_]+$", self.database_name):
            logging.error('Invalid database name')
            raise ValueError("Invalid database name. It should contain only alphanumeric characters and underscores, no spaces.")

        if not re.match("^\\d+$", self.policy_number):
            logging.error('Invalid policy number')
            raise ValueError("Invalid policy number. It should be numeric.")

        if self.priority < 1 or self.priority > 5:
            logging.error('Invalid priority')
            raise ValueError("Invalid priority. It should be between 1 and 5.")
        logging.info('Inputs validated')
    def stop_schedule(self, policy_id):
        logging.info(f'Stopping schedule for policy ID: {policy_id}')

        # Create a new API resource
        api = ApiResource(self.cloudera_config['host'], username=self.cloudera_config['user'], password=self.cloudera_config['password'])

        # Get the Cloudera Manager instance
        cm = api.get_cloudera_manager()

        # Get all the replication schedules
        schedules = cm.get_all_replication_schedules()

        # Find the schedule with the matching policy ID and stop it
        for schedule in schedules:
            if schedule.policyId == policy_id:
                schedule.stop()
                logging.info(f'Stopped schedule for policy ID: {policy_id}')
                break
        else:
            logging.warning(f'No schedule found with policy ID: {policy_id}')

    def start(self):
        logging.info('Starting job')
        cnx = mysql.connector.connect(user=self.mysql_config['user'], password=self.mysql_config['password'], host=self.mysql_config['host'], database=self.mysql_config['database'])
        cursor = cnx.cursor()

        add_job = ("INSERT INTO Jobs "
                   "(JobID, DatabaseName, ReceivedTime, PolicyNumber, Status, Priority) "
                   "VALUES (%s, %s, %s, %s, 'not started', %s)")
        data_job = (self.job_id, self.database_name, self.ReceivedTime, self.policy_number, self.priority)
        cursor.execute(add_job, data_job)
        cnx.commit()

        query = ("SELECT * FROM Jobs WHERE DatabaseName = %s AND ((Status = 'running') OR (ReceivedTime<%s AND Priority = %s) OR (Priority>%s)) ORDER BY Priority DESC, ReceivedTime ASC LIMIT 1")
        data_query = (self.database_name, self.ReceivedTime, self.priority, self.priority)
        cursor.execute(query, data_query)

        if cursor.fetchone() is None:
            update_job = ("UPDATE Jobs SET Status = 'running' WHERE JobID = %s")
            data_update_job = (self.job_id,)
            cursor.execute(update_job, data_update_job)
            cnx.commit()

            api = ApiResource(self.cloudera_config['host'], username=self.cloudera_config['user'], password=self.cloudera_config['password'])
            logging.info('Starting replication')
            api.start_replication(self.policy_number)

            # Poll replication status
            while True:
                logging.info('Checking replication status')
                status = api.get_replication_status(self.policy_number)
                status = 'completed successfully'  
                if status == 'completed successfully':
                    logging.info('Replication completed successfully')
                    update_job = ("UPDATE Jobs SET Status = 'completed successfully' WHERE JobID = %s")
                    data_update_job = (self.job_id,)
                    cursor.execute(update_job, data_update_job)
                    cnx.commit()
                    break
                elif status == 'replication failed':
                    logging.error('Replication failed')
                    update_job = ("UPDATE Jobs SET Status = 'replication failed' WHERE JobID = %s")
                    data_update_job = (self.job_id,)
                    cursor.execute(update_job, data_update_job)
                    cnx.commit()
                    break

                logging.info('Sleeping for 600 seconds before checking status again')
                time.sleep(600)
        else:
            logging.info('Sleeping for 900 seconds before starting again')
            time.sleep(900)
            self.start()
            self.stop_schedule()
            cursor.close()
            cnx.close()
        logging.info('Closing cursor and connection')


if __name__ == "__main__":
    trigger = XogtaTechBDRTrigger('databasename', 'policy_number', 'priority')
    trigger.start()
