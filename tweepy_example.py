import os
import tweepy as tw
from ConfigParser import SafeConfigParser


if __name__ == '__main__':
    """ 
        Verificare fisier de configurare 
        In medii de productie cheile nu se pastreaza in cod, ci in fisiere de configurare/variabile de system/parametrii de intrare/etc
        Cheile pentru Twitter se genereaza din interfata de developer de la Twitter
        https://developer.twitter.com/
    
    """

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

    """ 
       Initializarea conexiunii folosing librararii tweepy
       instalarea librariei se face cu pip install tweepy
    """
    auth = tw.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token_key, access_token_secret)
    api = tw.API(auth, wait_on_rate_limit=True)  ##aici s-a creat obiectul conexiune twitter

    api.verify_credentials() ##endpoint  account/verify_credentials
    """ 
      Afisare date utilizator 
    """
    try:
        user=api.get_user(screen_name="CZ_2020") ##inlocuieste parametrul cu user-ul de twitter dorit  #endpoint users/show.json
        print("ID-ul intern al user-ului %s" %user.id)
        print("Followers %s" % user.followers_count)
        print("Lista prieteni: ")
        for friend in user.friends():
            print friend.screen_name
    except:
        print("User-ul specificat nu poate fi gasit")

    """ 
        Afisare my tweets
    
    """
    print("Afisare my tweeets inaitne de o noua postare")
    public_tweets = api.home_timeline()##endpoint statuses /home_timeline
    for tweet in public_tweets:
        print("Id-ul intern al tweeet-ului %s" %tweet.id)
        print("Text tweet %s" %tweet.text)

    """ 
            Postare new tweet
    """
    try:
        api.update_status("Tweet cu referinta @CiprianNeagoe1") ##endpoint statuses/update
    except:
        print("Nu se posta un nou tweeet")




    """ 
                Stergere tweeet
    """
    try:
        api.destroy_status(1232669203724984320)##endpoint statuses/destroy/:id
        print("Tweet-ul a fost sters")
    except:
        None##Nu fac nimic daca tweet-ul nu exists


    """ Trimitere mesaj """
    directMessage = api.send_direct_message(api.get_user(screen_name="CiprianNeagoe1").id, "test")##endpoint direct_messages/events/new.json
    try:
        directMessage = api.send_direct_message("CiprianNeagoe1","test")
        print("Mesajul a fost transmis")
    except:
        None

    """ Messaje trimise """
    print("Lista mesaje trimise")
    try:
        messages=api.list_direct_messages()#endpoint direct_messages/events/list
    except:
        None

    """ 
        Folosim functionalitatea de cautare 
    """
    print("Lista tweet-uri care contin cuvantul Python")
    search_results=api.search(q="python", count=10) ##q este cuvantul cautat in tweets,iar count reprezinta numerele de rezulate dorite
    for i in search_results:#iterator printre inregistrarile returnate de interogare
        print("Text %s" %i.text)
        print("Location %s" % i.user.location)
        print("Name %s" % i.user.name)
        print("Data %s" % i.created_at)
        print("--------------------------------------------------------------")