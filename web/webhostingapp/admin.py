from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(userAccounts)
admin.site.register(domainList)
admin.site.register(subDomainList)
admin.site.register(mysqlUserDatabase)
admin.site.register(resetPassword)