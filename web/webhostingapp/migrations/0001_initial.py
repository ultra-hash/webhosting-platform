# Generated by Django 4.1 on 2022-09-03 17:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='domainList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('domainName', models.CharField(max_length=1024)),
                ('is_public', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=False)),
                ('date_created', models.DateTimeField(auto_now_add=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='userAccounts',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fname', models.CharField(max_length=40)),
                ('lname', models.CharField(max_length=40)),
                ('username', models.TextField(max_length=15)),
                ('email', models.EmailField(max_length=256)),
                ('password', models.CharField(max_length=256)),
                ('verify_code', models.CharField(max_length=10)),
                ('is_active', models.BooleanField(default=False)),
                ('date_created', models.DateTimeField(auto_now_add=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='subDomainList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subDomainName', models.CharField(max_length=30)),
                ('is_active', models.BooleanField(default=False)),
                ('date_created', models.DateTimeField(auto_now_add=True, null=True)),
                ('domainName', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='webhostingapp.domainlist')),
                ('owner', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='webhostingapp.useraccounts')),
            ],
        ),
        migrations.AddField(
            model_name='domainlist',
            name='owner',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='webhostingapp.useraccounts'),
        ),
    ]
