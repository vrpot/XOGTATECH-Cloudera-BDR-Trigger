# XOGTATECH-Cloudera-BDR-Trigger

# XogtaTechBDRTrigger

Overview
This repository contains a trigger-based replication system designed to enhance Cloudera BDR (Backup and Disaster Recovery) capabilities. Unlike the default schedule-based replication, this system allows replication triggered by specific events or conditions. Here’s how it works:

Prerequisites:
Ensure you have Cloudera BDR set up and configured.
Create a replication policy with the desired frequency (you can have multiple policies per database).
Set up a MySQL database to store metadata related to replication.

System Components:
Trigger : When your trigger logic monitors events (e.g., data changes, external triggers) occur, initiate replication trigger code.
Metadata Table (MySQL): Stores information about databases, tables, and replication status.
Policy Management: Ensures that only one replication policy runs at a time for a given database.

The trigger logic checks if a replication policy is already running for the same database. If not, it starts replication. It is first in first out (except when encountering higher priority replication for the same database)
Metadata is updated in the MySQL table to track progress.
After successful replication, the policy is stopped.

Usage:
Clone this repository.
Configure your event monitoring system (e.g., specify events to monitor, conditions for replication) and call replication trigger
Set up the MySQL database and create the necessary tables.

## Requirements

- Python 3
- `mysql-connector-python`
- `cm_api`
- `jks`
- `configparser`

## Configuration

The script requires a configuration file named `config.ini` in the same directory. 
This file should contain the MySQL and Cloudera Manager configuration details.

Example:

```ini
[mysql]
user = your_mysql_user
host = your_mysql_host
database = your_mysql_database
keystore_file = path_to_your_mysql_jceks_file
keystore_password = your_mysql_keystore_password
password_alias = alias_of_the_mysql_password

[cloudera]
user = your_cloudera_user
host = your_cloudera_host
keystore_file = path_to_your_cloudera_jceks_file
keystore_password = your_cloudera_keystore_password
password_alias = alias_of_the_cloudera_password

Usage
To use the script, you need to create an instance of the XogtaTechBDRTrigger class with the database name, policy number, and priority as arguments.
Then, call the start method on the instance.

Example:

trigger = XogtaTechBDRTrigger('database_name', 'policy_number', 'priority')
trigger.start()

Logging
The script uses Python's built-in logging module to log events.
The log level is set to INFO, and the format is %(asctime)s - %(levelname)s - %(message)s.
