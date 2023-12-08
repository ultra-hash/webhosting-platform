import sys

# Takes Second Adhoc values as domain
# command should be python3 or python deleteSql.py [username] > deletesql.sql

username = sys.argv[1]
database = username + '_db'
delete = f"""DROP DATABASE IF EXISTS {database};
DROP USER IF EXISTS {username};
FLUSH PRIVILEGES;
exit"""

print(delete)
