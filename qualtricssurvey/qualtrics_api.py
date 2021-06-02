from django.conf import settings
from lazy import lazy
from requests.packages.urllib3.exceptions import HTTPError
import requests
import json
from django.core.cache import caches

import logging
LOGGER = logging.getLogger(__name__)

class QualtricsApi():
    """
    Backend class for communicating with Qualtrics API (https://api.qualtrics.com/)
    """

    def __init__(self):
        self.api_ver = settings.QUALTRICS_API_VERSION
        if self.api_ver != 'v1':
            # initialize backend token cache
            self.token_cache = caches[settings.QUALTRICS_API_TOKEN_CACHE]
           
    def _log_if_raised(self, response, data):
        """
        Log server response if there was an error.
        """
        
        try:
            response.raise_for_status()
        except HTTPError:
            LOGGER.error(
                u"Encountered an error when retrieving data from Qualtrics. Response sent from %r with headers %r.\n"
                u"and data values %r\n"
                u"Response status was %s.\n%s",
                response.request.url, response.request.headers,
                data,
                response.status_code, response.content
            )
            raise

    @lazy
    def _api_base_url(self):
        """
        Base URL for all API requests.
        """
        return "{}/{}".format(settings.QUALTRICS_API_BASE_URL, settings.QUALTRICS_API_VERSION)

    @lazy
    def _api_eventsubscriptions_base_url(self):
        """
        Base URL for eventsubscriptions-specific requests.
        """
        return "{}/{}".format(self._api_base_url, "eventsubscriptions")

    @lazy
    def _api_surveys_base_url(self):
        """
        Base URL for surveys-specific requests.
        """
        return "{}/{}".format(self._api_base_url, "surveys")

    @lazy
    def _site_prefix(self):
        """
        Get the prefix for the site URL-- protocol.
        """
        scheme = u"https" if settings.HTTPS == "on" else u"http"
        return u'{}://{}'.format(scheme, settings.LMS_BASE)

    def get_headers(self):
        # Headers to send along with the request-- used for authentication

        # v1 is deprecated and will result in 404 error
        if settings.QUALTRICS_API_VERSION == 'v1':
            headers = {
                'X-API-TOKEN': settings.QUALTRICS_API_TOKEN, 
                'Content-Type': 'application/json'
            }
            return headers
        
        else:
            headers = {
                "authorization": "bearer " + self.get_oauth_token(),
                'Content-Type': 'application/json'
            }
            return headers

    def create_event_subscription(self, xblock):
        """
        Create event subscription callback on survey complete to XBlock event handler endpoint.
        """
        
        course_id = getattr(xblock.runtime, 'course_id', None)
        
        headers = self.get_headers()
      
        payload = json.dumps({
            "topics": "surveyengine.completedResponse." + xblock.survey_id,
            "publicationUrl": "{}/courses/{}/xblock/{}/handler_noauth/end_survey".format(
                self._site_prefix, course_id, xblock.location
            )
        })
        
        response = requests.request("POST", self._api_eventsubscriptions_base_url, headers=headers, data=payload)
        
        if response.ok:
            subscription_id = response.json()['result']['id']
            return subscription_id
        
        LOGGER.error(u"Could not create a subscription from Qualtrics API for course {} - XBlock location {}".format(course_id, xblock.location))

        return None

    def get_survey_response(self, survey_id, response_id):
        """
        Retrieve survey response for learner.
        """
        
        url = "{}/{}/responses/{}".format(self._api_surveys_base_url, survey_id, response_id)

        payload = {}
        headers = self.get_headers()
       
        response_survey = requests.request("GET", url, headers=headers, data=payload)
        self._log_if_raised(response_survey, payload)

        return response_survey

    def get_oauth_token(self):
        """
        Checks for valid auth token in cache and returns it, otherwise a new one is generated and saved to cache
        """
        token_cached = self.token_cache.get('qualtrics_api_auth_token')

        if token_cached is not None:
            return token_cached
        else:
            url = settings.QUALTRICS_OAUTH_URL

            clientId = settings.QUALTRICS_CLIENT_ID
            clientSecret = settings.QUALTRICS_CLIENT_SECRET

            payload= {'grant_type': 'client_credentials','scope': 'write:subscriptions read:survey_responses'}

            response = requests.post(url, auth=(clientId, clientSecret), data=payload)
            
            if response.ok:
                token = response.json()['access_token']
                self.token_cache.set('qualtrics_api_auth_token', token, getattr(settings, 'QUALTRICS_API_TOKEN_EXPIRATION', 3599))  #24h
                return token

            else:
                response.raise_for_status()
          

    
