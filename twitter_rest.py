from datetime import datetime
from requests.exceptions import ConnectionError, ReadTimeout, SSLError

from requests_oauthlib import OAuth1

import json
import requests
import os
import socket
import ssl
import time

DEFAULT_USER_AGENT = os.getenv('DEFAULT_USER_AGENT', 'python-twitter-peppin')
DEFAULT_CONNECTION_TIMEOUT = os.getenv('DEFAULT_CONNECTION_TIMEOUT', 5)
DEFAULT_STREAMING_TIMEOUT = os.getenv('DEFAULT_STREAMING_TIMEOUT', 90)
DEFAULT_REST_TIMEOUT = os.getenv('DEFAULT_REST_TIMEOUT', 5)



class TwitterAPI(object):

    """ Twitter REST API
    :param consumer_key: Twitter application consumer key
    :param consumer_secret: Twitter application consumer secret
    :param access_token_key: Twitter application access token key
    :param access_token_secret: Twitter application access token secret
    """

    protocol='https'
    domain='twitter.com'
    version='1.1'
    def __init__(
            self,
            consumer_key=None,
            consumer_secret=None,
            access_token_key=None,
            access_token_secret=None,
            uniqueID=None,
            logger=None):
        """Initialize with your Twitter application credentials"""

        if not all([consumer_key, consumer_secret, access_token_key, access_token_secret]):
            raise Exception('Parametrii de conectare nu sunt specificati!')
        self.auth = OAuth1(
            consumer_key,
            consumer_secret,
            access_token_key,
            access_token_secret)##authentificare
        self.consumer_key=consumer_key
        self.consumer_secret=consumer_secret
        self.access_token_key=access_token_key
        self.access_token_secret=access_token_secret
        self.logger = logger
        self.logger.debug( " %s - Twitter object created " %uniqueID)

    def _prepare_url(self, subdomain, path):

            return '%s://%s.%s/%s/%s.json' % (self.protocol,
                                              subdomain,
                                              self.domain,
                                              self.version,
                                              path)

    def request(self, uniqueID, method,subdomain, endpoint, params=None):
        """Realizeaza un request de tip REST API
                :param uniqueID: Pentru a tine tracking a instantei
                :param method: Methoda http folosita pentru apel
                :param method: subdomeniu-ul unde se realizeaza apelul. De obicei este api.domeniu
                :param endpoint:url-ul unde se va face cererea
                :returns: TwitterResponse
                """

        with requests.Session() as session:
            session.auth = self.auth
            url = self._prepare_url(subdomain, endpoint)
            self.logger.debug('%s - Method:%s Endpoint: %s  Params:%s' %(uniqueID,method,url,params))
            session.stream = False
            if method not in(['POST','GET','PUT','DELETE']):
                self.logger.debug( "%s - Invalid Http method request %s"  %(uniqueID,method))
            if method == 'POST':
                data = params
                params = None
            else:
                data = None
            try:
                response = session.request(
                    method,
                    url,
                    data=data,
                    params=params,
                    timeout=300,
                    files=None,
                    proxies=None)
                self.logger.debug("%s - Http response code :%s" %(uniqueID,response.status_code))
            except (ConnectionError, ReadTimeout,SSLError, ssl.SSLError, socket.error) as e:
                self.logger.error(uniqueID+'%s %s' % (type(e), e))
                super(Exception, self).__init__(e)

            return TwitterResponse(response, uniqueID,self.logger)



class TwitterResponse(object):

    """Raspunsul unei cerere REST API. In cazul twitter este un fisier json
    :param response: Obiectul response returnat de cererea  http
    """

    def __init__(self, response, uniqueID,logger):
        self.response = response
        self.logger=logger
        self.uniqueID=uniqueID

    @property
    def headers(self):
        """:returns: Dictionary of API response header contents."""
        return self.response.headers

    @property
    def status_code(self):
        """:returns: HTTP response status code."""
        return self.response.status_code

    @property
    def text(self):
        """:returns: Raw API response text."""
        return self.response.text

    def json(self, **kwargs):
        """Get the response as a JSON object.
        :param \*\*kwargs: Optional arguments that ``json.loads`` takes.
        :returns: response as JSON object.
        :raises: ValueError
        """
        return self.response.json(**kwargs)

    def get_iterator(self):
        """Get API dependent iterator.
        :returns: Iterator for tweets or other message objects in response.
        :raises error is status code!=200
        """

        self.logger.debug(" %s - Response status code: %s " %(self.uniqueID,self.response.status_code))
        if self.response.status_code != 200:
            if self.response.status_code >= 500:
                msg = 'Twitter internal error (you may re-try)'
            else:
                msg = 'Twitter request failed'
            self.logger.debug('%s - Status code %d: %s' % (self.uniqueID,self.response.status_code, msg))
            super(Exception, self).__init__(msg)
        else:
            self.logger.debug( " %s - Succcesful request " %self.uniqueID)

        #if self.stream:
        #   return iter(_StreamingIterable(self.response))
        #else:
            return iter(_RestIterable(self.response))

    def __iter__(self):
        """Get API dependent iterator.
        :returns: Iterator for tweets or other message objects in response.
        :raises: TwitterConnectionError, TwitterRequestError
        """
        return self.get_iterator()



class _RestIterable(object):

    """Iterate statuses, errors or other iterable objects in a REST API response.
    :param response: The request.Response from a Twitter REST API request
    """

    def __init__(self, response):
        resp = response.json()
        # convert json response into something iterable
        if 'errors' in resp:
            self.results = resp['errors']
        elif 'statuses' in resp:
            self.results = resp['statuses']
        elif 'users' in resp:
            self.results = resp['users']
        elif 'ids' in resp:
            self.results = resp['ids']
        elif 'results' in resp:
            self.results = resp['results']
        elif 'data' in resp and not isinstance(resp['data'], dict):
            self.results = resp['data']
        elif hasattr(resp, '__iter__') and not isinstance(resp, dict):
            if len(resp) > 0 and 'trends' in resp[0]:
                self.results = resp[0]['trends']
            else:
                self.results = resp
        else:
            self.results = (resp,)

    def __iter__(self):
        """Return a tweet status as a JSON object."""
        for item in self.results:
            yield item