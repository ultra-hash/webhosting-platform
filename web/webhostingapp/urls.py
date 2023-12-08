from django.urls import path
from . import views

urlpatterns = [
    # Home Page
    path('', views.index, name='index'),
    
    # Forms
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('verify/', views.verify, name="verify"), # for skipping manual triggers with None
    path('verify/<str:username>', views.verify, name="verify"),
    path('logout/', views.logout, name="logout"),
    path('forgetpassword/', views.forgetpassword, name="forgetpassword"), #for Get Request
    path('forgetpassword/<str:verification_code>', views.forgetpassword, name="forgetpassword"), # For Post Request
    

    # accessibility
    path('dashboard/', views.dashboard, name='dashboard'),
    path('domains/', views.domains, name='domains'),
    path('filemanager/', views.filemanager, name='filemanager'),
    path('settings/', views.settings, name='settings'),
    
    
    # subDomain API
    path('subdomain/delete/', views.subdomaindelete, name='subDomainDelete'), # for get request
    path('subdomain/delete/<str:FQDN>/', views.subdomaindelete, name='subDomainDelete'), # for POST request
    path('subdomain/add/', views.subdomainadd, name='subDomainADD'),
]
