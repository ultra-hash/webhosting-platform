import sys

# Takes Second Adhoc values as domain
# command should be python3 or python createVirtualHostConf.py [full domain name with subdomain]

FQDN = sys.argv[1]
base_string = f"""<VirtualHost *:80>
    ServerName {FQDN}
    ServerAlias {FQDN}
    ServerAdmin webmaster@localhost
    DocumentRoot /var/www/{FQDN}
    ErrorLog ${"{APACHE_LOG_DIR}"}/error.log
    CustomLog ${"{APACHE_LOG_DIR}"}/access.log combined
</VirtualHost>"""

print(base_string)
