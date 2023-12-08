import sys

# Takes Second Adhoc values as domain
# command should be python3 or python createSql.py [username] [password]

username = sys.argv[1]
password = sys.argv[2]
database = username + '_db'
create = f"""CREATE DATABASE IF NOT EXISTS {database} DEFAULT CHARACTER SET utf8 COLLATE utf8_unicode_ci;
CREATE USER IF NOT EXISTS {username}@'%' IDENTIFIED BY '{password}';
GRANT CREATE, ALTER, DROP, INSERT, UPDATE, DELETE, SELECT ON {database}.* TO {username}@'%';
FLUSH PRIVILEGES;
exit"""

print(create)
