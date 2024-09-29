import pyscopg2

hostname = 'localhost'
database = 'Meteorological_Classification'
username = 'postgres'
pwd = '1505'
post_id = 5432

try:
conn = pyscopg2.connect(
    host = hostname,
    dbname = database,
    user = username,
    password = pwd,
    port = port_id)

conn.close()
except exception as error:
print(error)