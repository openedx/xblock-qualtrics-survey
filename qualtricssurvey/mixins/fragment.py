"""
Mixin fragment/html behavior into XBlocks

Note: We should resume test coverage for all lines in this file once
split into its own library.
"""


from django.template.context import Context
from xblock.core import XBlock
from xblock.fragment import Fragment
#from qualtricssurvey.models import SurveyStatus
from django.conf import settings
import json
import requests
from django.core import serializers
import logging
LOGGER = logging.getLogger(__name__)

from ..models import QualtricsSubscriptions
from ..qualtrics_api import QualtricsApi
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
       
        # Create Qualtrics event subscription callback to specific XBlock event handler on load of the student view.
        # Checking if the survey has subscription for event callback and stores and entry in the database.
        
        course_id = getattr(self.runtime, 'course_id', None)
        try:
            qualtrics_subscription = QualtricsSubscriptions.objects.get(course_id=course_id, usage_key=self.location)
        except QualtricsSubscriptions.DoesNotExist:
            subscription_id = QualtricsApi().create_event_subscription(self)

            if subscription_id is not None:
                qualtrics_subscription = QualtricsSubscriptions(course_id=course_id, usage_key=self.location, subscription_id=subscription_id)
                qualtrics_subscription.save()                
            else:
                LOGGER.error(u"Could not locate a subscription id from Qualtrics API for course {} - XBlock location {}".format(course_id, self.location))
                        
         
        # Marks survey as incomplete for case that the learner's state was deleted
        if (self.score is None):
            self.is_answered = False
       
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
