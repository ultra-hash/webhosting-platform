from django.db import models

# Create your models here.


class userAccounts(models.Model):
    fname = models.CharField(max_length=40)
    lname = models.CharField(max_length=40)
    username = models.CharField(max_length=15)
    email = models.EmailField(max_length=256)
    password = models.CharField(max_length=256)
    verify_code = models.CharField(max_length=10)
    is_active = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self) -> str:
        return self.username


class domainList(models.Model):
    domainName = models.CharField(max_length=1024)
    owner = models.ForeignKey(
        userAccounts, on_delete=models.SET_NULL, null=True)
    is_public = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self) -> str:
        return self.domainName


class subDomainList(models.Model):
    subDomainName = models.CharField(max_length=30)
    domainName = models.ForeignKey(
        domainList, on_delete=models.SET_NULL, null=True)
    owner = models.ForeignKey(
        userAccounts, on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self) -> str:
        return self.subDomainName+'.'+self.domainName.domainName


class resetPassword(models.Model):
    owner = models.ForeignKey(
        userAccounts, on_delete=models.SET_NULL, null=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    verify_code = models.CharField(max_length=100, null=True)

    def __str__(self) -> str:
        return self.owner.username


class mysqlUserDatabase(models.Model):
    db_host = models.CharField(max_length=70, default="mysql.st-site.tk")
    db_port = models.IntegerField(default=3306)
    db_name = models.CharField(max_length=50)
    db_username = models.CharField(max_length=15)
    db_password = models.CharField(max_length=256)
    owner = models.ForeignKey(
        userAccounts, on_delete=models.SET_NULL, null=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self) -> str:
        return self.db_name
