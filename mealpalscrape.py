from bs4 import BeautifulSoup as bs
import re
from requests import Session
import smtplib
import ssl
import sys
import base64

with Session() as s:
    url = s.get("https://restaurant.mealpal.com/login")
    content = str(bs(url.content, "html.parser"))
    try:
        token = re.search('%s(.*)%s' % ('<meta content=\"', '\" name=\"csrf-token\"/>'), content).group(1)
    except AttributeError:
        print("Could not locate token")
        sys.exit()

    f = open("mealpalcred.ini", "r")
    if f.mode == 'r':
        loginPass = str(base64.b64decode(f.readline()))[2:-1]
        username = str(base64.b64decode(f.readline()))[2:-1]
        serverAddress = str(base64.b64decode(f.readline()))[2:-1]
        sendFrom = str(base64.b64decode(f.readline()))[2:-1]
        sendTo = str(base64.b64decode(f.readline()))[2:-1]
        pwd = str(base64.b64decode(f.readline()))[2:-1]
    f.close()

    payload = {'utf8': '\u2713',
               "authenticity_token": token,
               "user[email]": username,
               "user[password]": loginPass,
               "commit": 'Log in'
               }

    s.post("https://restaurant.mealpal.com/login", payload)
    homepage = s.get("https://restaurant.mealpal.com/product_offerings/lunch/orders/")
    homepageContent = str(bs(homepage.content, "html.parser"))

    try:
        totalScanned = int(re.search('%s(.*)%s' % ('Total Scanned:</span>\n<span>', '</span>'), homepageContent).group(1))
    except AttributeError:
        print("Could not locate target data")
        sys.exit()

    message = "Subject: MealPal: " + str(totalScanned)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(serverAddress, 465, context=context) as server:
        server.login(sendFrom, pwd)
        server.sendmail(sendFrom, sendTo, message)


