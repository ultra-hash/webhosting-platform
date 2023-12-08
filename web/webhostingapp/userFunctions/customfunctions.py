import os
from random import sample
import requests


def verification_code(lenght: int) -> str:
    alphanumaric = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
    return "".join(sample(alphanumaric, lenght))


def isValidSubDomain(domain: str) -> bool:
    valid_chars = 'abcdefghijklmnopqrstuvwxyz1234567890'
    # specialChars = '-.'
    if len(domain) > 30 or len(domain) < 5:
        return False

    if domain.startswith('-') or domain.endswith('-') or domain.startswith('.') or domain.endswith('.'):
        return False

    for i in domain:
        if i not in valid_chars:
            return False
    return True


def isValidateUsername(username: str) -> str:
    valid_chars = 'abcdefghijklmnopqrstuvwxyz1234567890'
    # specialChars = '-.'

    if len(username) > 30 or len(username) < 5:
        return "lesschar"

    if username.startswith('-') or username.endswith('-') or username.startswith('.') or username.endswith('.'):
        return "specialchar"

    for i in username:
        if i not in valid_chars:
            return "specialchar"

    return "allgood"


def writeFileToStaticUploadFolder(uploadedfile, BASE_DIR, username):
    try:
        UPLOADS_FOLDER = f"{str(BASE_DIR)}/static/uploads/{username}/"
        if not os.path.exists(UPLOADS_FOLDER):
            os.mkdir(UPLOADS_FOLDER)

        with open(str(UPLOADS_FOLDER) + uploadedfile.name, "wb+") as file:
            for chunk in uploadedfile.chunks():
                file.write(chunk)
        return True
    except:
        return False


def deleteUploadFiles(BASE_DIR, username):
    try:
        UPLOADS_FOLDER = f"{str(BASE_DIR)}/static/uploads/{username}/"

        # if path exists delete files in the folder
        # else all good return back
        if os.path.exists(UPLOADS_FOLDER):
            for i in os.listdir(UPLOADS_FOLDER):
                os.remove(UPLOADS_FOLDER+i)

        return True
    except:
        return False


def createDatabase(username, password):
    baseurl = f"https://{os.environ.get('JENKINS_USERNAME')}:{os.environ.get('JENKINS_PASSWORD')}@{os.environ.get('JENKINS_FQDN')}/job/createMysql/buildWithParameters?token={os.environ.get('JENKINS_SECRET_TOKEN')}&username={username}&password={password}&delay=0sec"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0"
    }
    try:
        page = requests.get(baseurl, headers=headers)
        return page.status_code
    except requests.exceptions.ConnectionError:
        return 500


def deletaDatabase(username):
    baseurl = f"https://{os.environ.get('JENKINS_USERNAME')}:{os.environ.get('JENKINS_PASSWORD')}@{os.environ.get('JENKINS_FQDN')}/job/deleteMySQL/buildWithParameters?token={os.environ.get('JENKINS_SECRET_TOKEN')}&username={username}&delay=0sec"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0"
    }
    page = requests.get(baseurl, headers=headers)
    return page.status_code


def createVirtualHost(FQDN: str, CreateDNS: bool):
    baseurl = f"https://{os.environ.get('JENKINS_USERNAME')}:{os.environ.get('JENKINS_PASSWORD')}@{os.environ.get('JENKINS_FQDN')}/job/Create VirtualHost/buildWithParameters?token={os.environ.get('JENKINS_SECRET_TOKEN')}&FQDN={(FQDN).strip()}&createDNS={str(CreateDNS).lower()}&delay=0sec"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0"
    }
    page = requests.get(baseurl, headers=headers)
    return page.status_code


def deleteVirtualHost(FQDN: str):
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0"
    }
    baseurl = f"https://{os.environ.get('JENKINS_USERNAME')}:{os.environ.get('JENKINS_PASSWORD')}@{os.environ.get('JENKINS_FQDN')}/job/Delete Virtual Host/buildWithParameters?token={os.environ.get('JENKINS_SECRET_TOKEN')}&FQDN={FQDN}&delay=0sec"
    page = requests.get(baseurl, headers=header)
    return page.status_code


def uploadfiletoFolder(FQDN, username, filename):
    # fileurl = f"192.168.0.105:8000/static/uploads/{username}/{filename}"
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0"
    }
    baseurl = f"https://{os.environ.get('JENKINS_USERNAME')}:{os.environ.get('JENKINS_PASSWORD')}@{os.environ.get('JENKINS_FQDN')}/job/upload zip to folder/buildWithParameters?token={os.environ.get('JENKINS_SECRET_TOKEN')}&domain={FQDN}&zip_name={filename}&username={username}&delay=0sec"
    page = requests.get(baseurl, headers=header)
    return page.status_code


def passwordResetURL(lenght: int) -> str:
    return verification_code(lenght)


def storageCheck():
    pass
