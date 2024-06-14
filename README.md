# XOGTATECH-Cloudera-BDR-Trigger

# XogtaTechBDRTrigger

This Python script is used to trigger a BDR (Backup and Disaster Recovery) job in Cloudera Manager.

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
