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
        #if self.api_ver != 'v1':
            # initialize backend refresh token cache with initial values from settings
            # settings will likely store an out of date refresh token after the first
            # refresh, so make sure cache stores up to date token.  Make sure to update
            # the refresh token if a new one obtained outside of this application.
            #self.token_cache = caches[settings.QUALTRICS_API_TOKEN_CACHE]
            #if not self.token_cache.get(BADGR_API_REFRESH_TOKEN_CACHE_KEY):
            #try:
            #    self.token_cache.set(BADGR_API_REFRESH_TOKEN_CACHE_KEY, settings.BADGR_API_REFRESH_TOKEN, timeout=None)
            #except AttributeError:
            #    raise ImproperlyConfigured("BADGR_API_REFRESH_TOKEN not set. See https://badgr.org/app-developers/api-guide/#quickstart")

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

    def create_event_subscription(self, xblock):
        """
        Create event subscription callback on survey complete to XBlock event handler endpoint.
        """
        course_id = getattr(xblock.runtime, 'course_id', None)
        
        headers = {
            'X-API-TOKEN': settings.QUALTRICS_API_TOKEN, 
            'Content-Type': 'application/json'
        }        
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

    def get_survey_response(self, survey_id, response_id, bearer_token):
        """
        Retrieve survey response for learner.
        """
        url = "{}/{}/responses/{}".format(self._api_surveys_base_url, survey_id, response_id)

        payload = {}
        headers = {
            "authorization": "bearer " + bearer_token,
        }
        response_survey = requests.request("GET", url, headers=headers, data=payload)
        self._log_if_raised(response_survey, payload)

        return response_survey

    def get_oauth_token(self): 
        url = "https://clemson.qualtrics.com/oauth2/token"

        # TODO: Find way to store id and secret as environment variables for each client
        payload= {'client_id': '4034ac7845f121397cfffdbcd5f45e59', 'client_secret': 'p3Tpxy4FnppHaVowFJfAUTlgiFkx3JzFivudjg1dW8YafVFqEB0jz7EIcSE4EabK','grant_type': 'client_credentials','scope': 'write:subscriptions read:survey_responses'}
        files=[

        ]
        headers = {
        'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload, files=files)

        print(response.text)
        return response.text

    
