from django.shortcuts import render, redirect
from .models import *
from .userFunctions.customfunctions import *
from django.core.mail import send_mail
from django.contrib import messages
from web.settings import EMAIL_HOST_USER, BASE_DIR
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect
# Create your views here.


def index(request):
    return redirect('login')


@csrf_protect
def login(request):
    # check If already logged in
    try:
        if not request.session['verified']:
            return redirect(f'../verify/{request.session["username"]}')

        elif request.session['verified']:
            return redirect('dashboard')

    except KeyError:
        if request.method == 'POST':
            # Geathering User Inputs
            username = request.POST["username"]
            password = request.POST["password"]

            # Authenticate user
            if userAccounts.objects.filter(username=username, password=password).exists():
                request.session['login'] = True
                request.session['username'] = username
                request.session['userid'] = userAccounts.objects.get(
                    username=username).id  # returns user id from DB table
                request.session['verified'] = False
                if userAccounts.objects.filter(username=username, password=password, is_active=False).exists():
                    return redirect(f"../verify/{username}")
                else:
                    request.session['verified'] = True
                    return redirect('dashboard')
            else:
                messages.info(request, "username and password don't match")
                return redirect('login')

        else:
            context = {}
            return render(request, "./pages/samples/login.html", context)


@csrf_protect
def logout(request):
    try:
        if request.session['login']:
            del request.session['login']
            del request.session['userid']
            del request.session['username']
            del request.session['verified']
            messages.success(request, "You Have Successfully logged out")
            return redirect('login')

    except KeyError:
        return redirect('login')


@csrf_protect
def register(request):
    try:
        if not request.session['verified']:
            return redirect('verify')

        elif request.session['verified']:
            return redirect('dashboard')

    except KeyError:
        if request.method == 'POST':
            # Geathering user input
            firstname = request.POST['firstname']
            lastname = request.POST['lastname']
            username = request.POST['username']
            email = request.POST['email']
            password = request.POST['password']
            code = verification_code(10)

            # verify userInput
            if firstname and lastname and username and email and password:
                # check if your name valid
                status = isValidateUsername(username)
                if status == "specialchar":
                    messages.info(request, "Special charaters not allowed")
                    messages.info(
                        request, "only a-z (lower) and 0-9 are allowed")
                    return redirect('register')
                elif status == "lesschar":
                    messages.info(request, "Username too short")
                    return redirect('register')
                elif status == "allgood":
                    # Check if userexits
                    if userAccounts.objects.filter(username=username).exists():
                        messages.info(request, "Username Already Taken")
                        return redirect('register')
                    elif userAccounts.objects.filter(email=email).exists():
                        messages.info(request, "Email Already exists")
                        return redirect('register')
                    else:
                        # Add user Details to DB
                        user = userAccounts(fname=firstname, lname=lastname, username=username,
                                            email=email, password=password, verify_code=code)

                        # send email to user with verfication code
                        send_mail(
                            "Account Verification",
                            f"""Hey, {username}
                            Your Verification Code is {code}.
                            Login to verify your account.
                            """,
                            EMAIL_HOST_USER,  # from email set in settings.py
                            recipient_list=[email],
                            fail_silently=False,
                            html_message=f"<h1>Hey {username} </h1><h2> Your Verification Code to Activate Your Account is ' {code} ' <br> Login to verify your account.</h2>",
                        )

                        messages.success(
                            request, "Please Check Your Email. An Email Has Been Sent With Verification Code.")
                        user.save()  # save user data only after email sent
                        return redirect('login')
            else:
                messages.info(request, "All Fields Must Be Filled!!!")
                return redirect('register')
        else:
            context = {}
            return render(request, "./pages/samples/register.html", context)


@csrf_protect
def dashboard(request):
    # check If already logged in
    try:
        if not request.session['verified']:
            return redirect('verify')

        # Getting Context from Databases for Dashboard

        user = userAccounts.objects.filter(
            username=request.session["username"])[0]
        subdomainlist = subDomainList.objects.filter(owner=user.id)
        database = mysqlUserDatabase.objects.filter(owner=user.id)
        dbcount = database.count()

        if dbcount == 0:
            database = {}
        else:
            database = database[0]

        context = {
            'user': user,
            'subdomainlist': subdomainlist,
            'database': database,
            'dbcount': dbcount,
        }
        return render(request, "dashboard.html", context)

    except KeyError:
        return redirect('login')


@csrf_protect
def verify(request, username=None):
    if username != None:
        try:
            if not request.session['verified']:
                if request.method == 'POST':
                    code = request.POST["code"].strip()
                    user = userAccounts.objects.get(username=username)

                    if code == user.verify_code:
                        user.is_active = True
                        user.save()
                        request.session["verified"] = True
                        messages.success(
                            request, "You account has been successfully Verified!")

                        # verification code as password :-) hahah
                        db_password = verification_code(16)

                        # running jenkins job
                        status = createDatabase(
                            username=user.username, password=db_password)

                        status = round(status/100)
                        if status == 2:
                            # storing in database
                            store = mysqlUserDatabase(db_name=(
                                user.username+'_db'), db_username=user.username, db_password=db_password, owner=user)
                            store.save()
                            messages.success(
                                request, f"MySql Database has successfull created for {user.username}")
                        else:
                            send_mail(
                                "Seens like Jenkins Down",
                                f"""Event: Database Not Created,
                            User : {user.username},
                            Time : {timezone.now()},
                            """,
                                EMAIL_HOST_USER,  # from email set in settings.py
                                recipient_list=[EMAIL_HOST_USER],
                                fail_silently=False,
                                html_message=f"Event: Database Not Created <br> user : {user.username} <br> Time : {timezone.now()}",)
                            messages.info(
                                request, f"Admins have been notified, issue with creating database for {user.username}")
                        return redirect('dashboard')

                    else:
                        messages.info(request, "Incorrect Verification Code")
                        return redirect('verify')
                else:
                    return render(request, "verify.html", {'username': request.session['username']})

            else:
                return redirect('login')

        except KeyError:
            return redirect('login')
    else:
        return redirect('login')


@csrf_protect
def domains(request):
    try:
        if not request.session['verified']:
            return redirect('verify')

        # Getting Context from Databases for Dashboard
        user = userAccounts.objects.get(username=request.session["username"])
        subdomainlist = subDomainList.objects.filter(owner=user.id)
        domainlist = domainList.objects.filter(is_public=True, is_active=True)

        context = {
            'user': user,
            'subdomainlist': subdomainlist,
            'domainList': domainlist
        }
        return render(request, "domains.html", context)
    except KeyError:
        return redirect('login')


@csrf_protect
def filemanager(request):
    try:
        if not request.session['verified']:
            return redirect('verify')

        elif request.session['verified']:

            if request.method == 'POST':

                FQDN = request.POST['domain_name']
                uploadedfile = request.FILES['file']
                subdomain = ".".join(FQDN.split(".")[0:-2])
                domainname = ".".join(FQDN.split(".")[-2:])

                # Model instances
                USER = userAccounts.objects.get(
                    username=request.session['username'])
                DOMAIN = domainList.objects.get(domainName=domainname)

                # check if user owns the domain or not
                if not subDomainList.objects.filter(subDomainName=subdomain, domainName=DOMAIN.id, owner=USER.id).exists():
                    messages.info(
                        request, f"Access Denined!!! {FQDN} don't exits or You don't own this domain")
                    return redirect('dashboard')

                if request.FILES['file']:
                    x = deleteUploadFiles(
                        BASE_DIR, request.session['username'])
                    if not x:
                        messages.info(request, "Folder Not Deleted")
                        return redirect('dashboard')

                    x = writeFileToStaticUploadFolder(
                        request.FILES['file'], BASE_DIR, request.session['username'])
                    if not x:
                        messages.info(
                            request, "Oo! O! Error , File may be corrupted")
                    else:

                        status = uploadfiletoFolder(
                            FQDN=FQDN, username=USER.username, filename=uploadedfile.name)
                        status = round(status/100)
                        if status != 2:
                            messages.info(
                                request, "Internal error. Admins have been notified. Try after some time")
                            send_mail(
                                "Seens like Jenkins Down",
                                f"""Event: Uploading File To Domain,
                            User : {USER.username},
                            Domain Name: {FQDN},
                            File: {uploadedfile.name}
                            Time : {timezone.now()},
                            """,
                                EMAIL_HOST_USER,  # from email set in settings.py
                                recipient_list=[EMAIL_HOST_USER],
                                fail_silently=False,
                                html_message=f"Event: Uploading File To Domain <br> user : {USER.username} <br> Domain Name: {FQDN} <br> File: {uploadedfile.name}  <br> Time : {timezone.now()}",)

                        messages.success(
                            request, "File Have Been Uploaded Successfully")
                    return redirect('dashboard')
                else:
                    messages.info(request, "No files Detected. Contact admin.")
                return redirect('filemanager')

            else:
                USER = userAccounts.objects.get(
                    username=request.session["username"])
                domains = subDomainList.objects.filter(owner=USER)
                context = {
                    'username': USER.username,
                    'domains': domains,
                }
                return render(request, "filemanager.html", context)

    except KeyError:
        return redirect('login')


@csrf_protect
def settings(request):
    try:
        if not request.session['verified']:
            return redirect(f'verify')

        elif request.session['verified']:
            if request.method == "POST":
                currentpass = request.POST["currentpassword"]
                pass1 = request.POST["password1"]
                pass2 = request.POST["password2"]
                username = request.session["username"]
                if userAccounts.objects.filter(username=username).exists():
                    USER = userAccounts.objects.get(username=username)
                    if currentpass == USER.password:
                        if pass1 == pass2:
                            USER.password = request.POST["password1"]
                            send_mail(
                                "Password Change",
                                f"Hey {USER.username} Your account password has successfully changed.",
                                EMAIL_HOST_USER,
                                [USER.email],
                                fail_silently=False,
                                html_message=f"Hey {USER.username} Your account password has successfully changed.",
                            )
                            USER.save()
                            messages.success(
                                request, "Password successfully changed")
                            return redirect('settings')
                        else:
                            messages.info(
                                request, f"Both password don't mactch.")
                            return redirect('settings')
                    else:
                        messages.info(request, f"incorrect current password")
                        return redirect('settings')
                else:
                    messages.info(request, "Access Denined")
                    return redirect('logout')

            else:
                USER = userAccounts.objects.get(
                    username=request.session['username'])
                context = {
                    'user': USER
                }
                return render(request, "settings.html", context)
    except KeyError:
        return redirect('login')


@csrf_protect
def subdomainadd(request):
    try:
        if request.session["verified"]:
            if request.method == "POST":
                username = request.session["username"]
                # ".".join(FQDN.split(".")[0:-2])
                subdomain = request.POST["subdomain_name"]
                # ".".join(FQDN.split(".")[-2:])
                domainname = request.POST["domain_name"]
                FQDN = subdomain+"."+domainname

                # check if subdomain is not valid
                if not isValidSubDomain(subdomain):
                    messages.info(
                        request, "Please read the rules provided in the create section.")
                    return redirect('domains')

                USER = userAccounts.objects.get(username=username)

                # check if user reached domain per user limit
                if subDomainList.objects.filter(owner=USER.id).count() >= 5:
                    messages.info(request, "You Reached Your Free Domain Limt")
                    return redirect('domains')

                # check if DomainName is register and valid.
                if not domainList.objects.filter(domainName=domainname).exists():
                    messages.info(request, f"Invalid domain {domainname}")
                    return redirect('domains')
                else:
                    DOMAIN = domainList.objects.get(domainName=domainname)

                # check if domain already exists and assigned to other user
                if subDomainList.objects.filter(subDomainName=subdomain, domainName=DOMAIN.id, is_active=True).exists():
                    messages.info(request, "Domain already taken")
                    return redirect('domains')

                else:
                    if subDomainList.objects.filter(subDomainName=subdomain, domainName=DOMAIN.id, is_active=False).exists():
                        domain = subDomainList.objects.get(
                            subDomainName=subdomain, domainName=DOMAIN.id, is_active=False)
                        status = createVirtualHost(FQDN, domain.is_active)
                        status = round(status/100)
                        if status == 2:
                            domain.owner = USER
                            domain.is_active = True
                            domain.date_created = timezone.now()

                        else:
                            messages.info(
                                request, "Internal error. Admins have been notified. Try after some time")
                            send_mail(
                                "Seens like Jenkins Down",
                                f"""Event: Creating Domain,
                            User : {USER.username},
                            Creating Domain: {FQDN},
                            Time : {timezone.now()},
                            """,
                                EMAIL_HOST_USER,  # from email set in settings.py
                                recipient_list=[EMAIL_HOST_USER],
                                fail_silently=False,
                                html_message=f"Event: Creating Domain <br> user : {USER.username} <br> Domain Name: {FQDN} <br> Time : {timezone.now()}",)
                            return redirect('domains')
                    else:
                        domain = subDomainList(
                            subDomainName=subdomain, domainName=DOMAIN, owner=USER, is_active=True)
                        status = createVirtualHost(FQDN, domain.is_active)
                        status = round(status/100)
                        if status != 2:
                            messages.info(
                                request, "Internal error. Admins have been notified. Try after some time")
                            send_mail(
                                "Seens like Jenkins Down",
                                f"""Event: Creating Domain,
                            User : {USER.username},
                            Domain Name: {FQDN},
                            Time : {timezone.now()},
                            """,
                                EMAIL_HOST_USER,  # from email set in settings.py
                                recipient_list=[EMAIL_HOST_USER],
                                fail_silently=False,
                                html_message=f"Event: Creating Domain <br> user : {USER.username} <br> Domain Name: {FQDN} <br> Time : {timezone.now()}",)
                            return redirect('domains')

                    send_mail(
                        f'{FQDN} Created Successfull',
                        f"""Hey {USER.username}
                        Your {FQDN} is Created Successfull and Ready to Host Your website.

                        Note: website should be compressed in to a zip file before uploading.

                        Hierarchy:

                        website.zip/
                            |--some folder
                            |    |__some files
                            |
                            |--seom folder
                            |    |__some files
                            |
                            |_index.php main file 
                        """,
                        EMAIL_HOST_USER,
                        [USER.email],
                        fail_silently=True,
                        html_message=f"""<h3>Hey! {USER.username} </h3> <br> <h4> Your {FQDN} is Created Successfull and Ready to Host Your site. <br> Note: website should be compressed in to a zip file before uploading.
    <pre> 
    Hierarchy:

    website.zip/
        |--some folder
        |    |__some files
        |
        |--some folder
        |    |__some files
        |
        |_index.html main file
    </pre>
                        </h4> """
                    )

                    domain.save()
                    messages.success(request, f"{FQDN} has been created.")
                    messages.success(
                        request, f"Setting UP DNS records may take at least 30 seconds to configure. ")
                    return redirect('domains')
            else:
                return redirect("domains")

        else:
            return redirect('verify')

    except KeyError:
        return redirect("login")


@csrf_protect
def subdomaindelete(request, FQDN=None):
    if FQDN != None:
        try:
            if request.session["verified"]:
                subdomain = ".".join(FQDN.split(".")[0:-2])
                domain = ".".join(FQDN.split(".")[-2:])
                username = request.session["username"]
                USER = userAccounts.objects.get(username=username)

                if not domainList.objects.filter(domainName=domain).exists():
                    messages.info(request, f"{FQDN} don't exits")
                    return redirect('domains')
                else:
                    DOMAIN = domainList.objects.get(domainName=domain)
                    if subDomainList.objects.filter(subDomainName=subdomain, domainName=DOMAIN.id, owner=USER.id).exists():
                        status = deleteVirtualHost(FQDN)
                        status = round(status/100)
                        if status == 2:
                            domain = subDomainList.objects.get(
                                subDomainName=subdomain)
                            domain.owner = None
                            domain.is_active = False
                            domain.save()
                            messages.info(
                                request, f" {FQDN} Deleted SuccessFully.")
                        else:
                            messages.info(
                                request, "Internal error. Admins have been notified. Try after some time")
                            send_mail(
                                "Seens like Jenkins Down",
                                f"""event: deleting domain
                            user : {USER.username}
                            deleting domain: {FQDN}
                            Time : {timezone.now()}
                            """,
                                EMAIL_HOST_USER,  # from email set in settings.py
                                recipient_list=[EMAIL_HOST_USER],
                                fail_silently=False,
                                html_message=f"event: deleting domain <br> user : {USER.username} <br> domain Name: {FQDN} <br> Time : {timezone.now()}",)
                    else:
                        messages.info(
                            request, f"{FQDN} don't exists or You are not the owner")

                    return redirect('domains')
            else:
                return redirect('verify')

        except KeyError:
            return redirect("login")
    else:
        return redirect("login")


@csrf_protect
def forgetpassword(request, verification_code=None):
    if verification_code != None:
        try:
            if request.session["login"]:
                return redirect('dashboard')
        except:
            if request.method == "POST":
                username = request.POST["username"]
                if request.POST["password1"] == request.POST["password2"]:
                    if userAccounts.objects.filter(username=username).exists():
                        user = userAccounts.objects.get(username=username)
                        if resetPassword.objects.filter(owner=user.id).exists():

                            user.password = request.POST["password1"]
                            send_mail(
                                "Password ReseT Successfull",
                                f"Hey {user.username} your account password has successfully changed.",
                                EMAIL_HOST_USER,
                                [user.email],
                                fail_silently=False,
                                html_message=f"<h3><p>Hey {user.username} your account password has successfully changed.</p></h3>",
                            )
                            user.save()
                            status = resetPassword.objects.get(owner=user.id)
                            status.delete()
                            messages.success(
                                request, "Password has successfully changed")
                            return redirect('login')

                    messages.info(request, f"username don't match")
                    return redirect(f'forgetpassword/{verification_code}')
                else:
                    messages.info(
                        request, "Retry again, Both passwords don't match")
                    return redirect(f'forgetpassword/{verification_code}')
            else:
                if resetPassword.objects.filter(verify_code=verification_code).exists():
                    show_form = "verification"
                else:
                    show_form = "access Denied"
            return render(request, "forgetpassword.html", {"show_form": show_form})
    else:
        if request.method == "POST":
            email = request.POST["email"]
            if userAccounts.objects.filter(email=email).exists():
                user = userAccounts.objects.get(email=email)
                code = passwordResetURL(40)

                resetPassword.objects.filter(owner=user.id).all().delete()

                status = resetPassword(owner=user, verify_code=code)
                send_mail(
                    "Password Reset Verification",
                    f"Hey {user.username}! Please visit the URL to reset the password. THe url = https://{os.environ.get('WEBSITE_FQDN')}/forgetpassword/{code}",
                    EMAIL_HOST_USER,
                    [user.email],
                    fail_silently=False,
                    html_message=f"Hey {user.username}! Please visit the URL to reset the password. THe url = https://{os.environ.get('WEBSITE_FQDN')}/forgetpassword/{code}",
                )
                status.save()
                messages.success(
                    request, "Password Reset Link Has Been Sent To Your Email.")
                return redirect('login')
            else:
                messages.info(
                    request, f"No user account found with the mentioned email.")
                return redirect('forgetpassword')
        else:
            return render(request, "forgetpassword.html", {"show_form": "generate"})
