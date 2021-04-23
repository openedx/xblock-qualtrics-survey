"""
Mixin fragment/html behavior into XBlocks

Note: We should resume test coverage for all lines in this file once
split into its own library.
"""


from django.template.context import Context
from xblock.core import XBlock
from xblock.fragment import Fragment
from qualtricssurvey.models import QualtricsSubscriptions
from qualtricssurvey.models import SurveyStatus
from django.conf import settings
from common.djangoapps.student.models import user_by_anonymous_id
import json
import requests
from django.core import serializers
import logging
LOGGER = logging.getLogger(__name__)

class XBlockFragmentBuilderMixin:
    """
    Create a default XBlock fragment builder
    """
    static_css = [
        'view.css',
    ]
    static_js = [
        'view.js',
    ]
    static_js_init = 'QualtricsSurveyView'
    template = 'view.html'

    def provide_context(self, context):  # pragma: no cover
        """
        Build a context dictionary to render the student view

        This should generally be overriden by child classes.
        """
        context = context or {}
        context = dict(context)
        return context

    @XBlock.supports('multi_device')
    def student_view(self, context=None):
        """
        Build the fragment for the default student view
        """
        template = self.template
        context = self.provide_context(context)
        static_css = self.static_css or []
        static_js = self.static_js or []
        js_init = self.static_js_init
        fragment = self.build_fragment(
            template=template,
            context=context,
            css=static_css,
            js=static_js,
            js_init=js_init,
        )
    
        # Checking if the survey has subscription for event callback and creates it if not
        try:
            qualtrics_subscription = QualtricsSubscriptions.objects.get(course_id=getattr(self.runtime, 'course_id', None), usage_key=self.location)
    
        except:
            headers = {'X-API-TOKEN': u'{}'.format(settings.QUALTRICS_API_TOKEN), 'Content-Type': 'application/json'}
            payload = json.dumps({
                "topics": "surveyengine.completedResponse." + self.survey_id,
                "publicationUrl": "http://google.com/courses/course-v1:edX+DemoX+Demo_Course/xblock/block-v1:edX+DemoX+Demo_Course+type@qualtricssurvey+block@00116206cd3a4059b4749fe26b5417bd/handler_noauth/end_survey"
            })

            response = requests.request("POST", settings.QUALTRICS_BASE_URL, headers=headers, data=payload)
            subscription_id = response.json()['result']['id']

            if subscription_id:
                qualtrics_subscription = QualtricsSubscriptions(course_id=getattr(self.runtime, 'course_id', None), usage_key=self.location, subscription_id=subscription_id)
                qualtrics_subscription.save()
            
            else:
                LOGGER.error(u"Could not locate a subscription id from Qualtrics API for course {} - XBlock location {}".format(
                course_id, self.location))
                raise
        
        try:
            survey_status = SurveyStatus.objects.get( usage_key = self.location, user_id=self.xmodule_runtime.user_id)
        except:
            survey_status = SurveyStatus( usage_key = self.location, user_id=user.id, status = "incomplete")
            survey_status.save()
        
        return fragment

    def build_fragment(
            self,
            template='',
            context=None,
            css=None,
            js=None,
            js_init=None,
    ):
        """
        Creates a fragment for display.
        """
        
        context = context or {}
        css = css or []
        js = js or []
        rendered_template = ''
        if template:  # pragma: no cover
            template = 'templates/' + template
            rendered_template = self.loader.render_django_template(
                template,
                context=Context(context),
                i18n_service=self.runtime.service(self, 'i18n'),
            )
        fragment = Fragment(rendered_template)
        for item in css:
            if item.startswith('/'):
                url = item
            else:
                item = 'public/' + item
                url = self.runtime.local_resource_url(self, item)
            fragment.add_css_url(url)
        for item in js:
            item = 'public/' + item
            url = self.runtime.local_resource_url(self, item)
            fragment.add_javascript_url(url)
        if js_init:  # pragma: no cover
            fragment.initialize_js(js_init)
        return fragment
