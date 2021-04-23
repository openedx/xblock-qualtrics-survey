from django.conf import settings
from lazy import lazy
from requests.packages.urllib3.exceptions import HTTPError
import requests
import json

import logging
LOGGER = logging.getLogger(__name__)

class QualtricsApi():
    """
    Backend class for communicating with Qualtrics API (https://api.qualtrics.com/)
    """

    def __init__(self):
        pass

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

    def get_survey_response(self, survey_id, response_id):
        """
        Retrieve survey response for learner.
        """
        url = "{}/{}/responses/{}".format(self._api_surveys_base_url, survey_id, response_id)

        payload = {}
        headers = {
            'X-API-TOKEN': settings.QUALTRICS_API_TOKEN
        }
        response_survey = requests.request("GET", url, headers=headers, data=payload)
        self._log_if_raised(response_survey, payload)

        return response_survey

    
