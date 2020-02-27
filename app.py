from ConfigParser import SafeConfigParser
import os
from twitter_rest import TwitterAPI,TwitterResponse
import uuid
import logging
from datetime import datetime,timedelta,date

def LBMethodList():
    print "Functii Twitter de testat"
    print "0  - Exit"
    print "1  - Test credentials"
    print "2  - Get user information"

if __name__ == '__main__':

    if os.path.isfile('config.ini') is not True:
        exit("Lipseste fisierul de configurare!")

    configParser = SafeConfigParser()
    configParser.read('config.ini')

    try:
        consumer_key = configParser.get('config', 'consumer_key')
    except:
        exit("Cheia de consumator lipseste din fisierul de configurare!")

    try:
        consumer_secret = configParser.get('config', 'consumer_secret')
    except:
        exit("Cheia secreta de consumator lipseste din fisierul de configurare!")

    try:
        access_token_key = configParser.get('config', 'access_token_key')
    except:
        exit("Token-ul de acces lipseste din fisierul de configurare!")

    try:
        access_token_secret = configParser.get('config', 'access_token_secret')
    except:
        exit("Token-ul secret  lipseste din fisierul de configurare!")

    try:
        protocol = configParser.get('config', 'protocol')
    except:
        exit("Protocol is missing from configuration file!")

    try:
        domain = configParser.get('config', 'domain')
    except:
        exit("Domain is missing from configuration file!")

    try:
        version = configParser.get('config', 'version')
    except:
        exit("Version  is missing from configuration file!")

    try:
        version = configParser.get('config', 'version')
    except:
        exit("Version  is missing from configuration file!")

    """Configurare obiectul pentru logging"""
    log_filename = datetime.now().strftime('%Y-%m-%d') + '.log'
    logger = logging.getLogger("Twitter")
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s - %(message)s')
    file_handler = logging.FileHandler("logs/" + log_filename)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    uniqueID = str(uuid.uuid4())
    logger.debug(uniqueID + " Start checking the calling arguments")

    uniqueID = str(uuid.uuid4())##generam un nr unic pentru cautare usoara prin loguri

    twitter=TwitterAPI(consumer_key,consumer_secret,access_token_key,access_token_secret,uniqueID,logger)##initilizare obiect conexiune twitter

    """ 
         Verificare credentiale
    """

     ##endpoint account/verify_credentials
    response = twitter.request(uniqueID, 'GET', 'api', 'account/verify_credentials')
    if response.status_code == 200:##verificam http response code sa fie 200,adica OK
        json=response.json()
        print("Autentificare reusita pentru utilizatorul %s" % json["screen_name"])
    else:
        print("Eroare la autentificare")

    """ 
         Afisare date utilizator 
    """
    response = twitter.request(uniqueID, 'GET', 'api', 'users/show','screen_name=CZ_2020')
    if response.status_code == 200:  ##verificam http response code sa fie 200,adica OK
        json = response.json()
        print("ID-ul intern al user-ului %s" % json["id"])
        print("Followers %s" % json["followers_count"])
        print("Lista prieteni: ")
    else:
        print("Nu se poate apela endpoint-ul. Codul de raspuns este %s" %response.status_code)

    """ 
           Afisare my tweets

    """
    print("Afisare my tweeets inaitne de o noua postare")
    response = twitter.request(uniqueID, 'GET', 'api', 'statuses/home_timeline')
    if response.status_code == 200:  ##verificam http response code sa fie 200,adica OK
        public_tweets = response.json()
        for tweet in public_tweets:
            print("Id-ul intern al tweeet-ului %s" % tweet["id"])
            print("Text tweet %s" % tweet["text"])
    else:
        print("Nu se poate apela endpoint-ul. Codul de raspuns este %s" % response.status_code)

    """ 
                Postare new tweet
     """
    response = twitter.request(uniqueID, 'POST', 'api', 'statuses/update',{"status":"Tweet nou"})
    if response.status_code == 200:  ##verificam http response code sa fie 200,adica OK
        print("Tweet now!")
    else:
        print("Nu se poate apela endpoint-ul. Codul de raspuns este %s" % response.status_code)

    """ 
                   Stergere tweet
    """
    response = twitter.request(uniqueID, 'POST', 'api', 'statuses/destroy/1232669203724984320')
    if response.status_code == 200:  ##verificam http response code sa fie 200,adica OK
        print("Tweet sters!")
    else:
        print("Nu se poate apela endpoint-ul. Codul de raspuns este %s" % response.status_code)

    """
    while 1:
        LBMethodList()
        idx=input('Please select from the list: ')
        if idx==1:
            twitter.verify_credentials(uniqueID)
        if idx==2:
            status_text=raw_input("Introdu statusul dorit:")
            twitter.update_status(uniqueID,{'status': status_text})
        if idx==0:
            exit("Exit!")
    """
