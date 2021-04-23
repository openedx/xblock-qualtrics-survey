"""
Handle data access logic for the XBlock
"""

import six
from datetime import datetime
from xblock.scorable import ScorableXBlockMixin, Score
from django.utils.translation import ugettext_lazy as _
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from xblock.core import XBlock
from xblock.fields import Scope
from xblock.fields import Boolean, List, String, Float
from opaque_keys.edx.keys import UsageKey
from xmodule.modulestore.django import modulestore
from .mixins.handlers import QualtricsHandlersMixin
import requests
import json
from collections import namedtuple
from common.djangoapps.student.models import user_by_anonymous_id
from django.db import models
from opaque_keys.edx.django.models import CourseKeyField
from opaque_keys.edx.django.models import UsageKeyField
from django.conf import settings

from xmodule.fields import ScoreField

import logging
LOGGER = logging.getLogger(__name__)

Score = namedtuple('Score', ['raw_earned', 'raw_possible'])

class QualtricsSubscriptions(models.Model):
    """
    Defines a way to see if a given Qualtrics subscription_id is tied to a course_id, XBlock location id
    """
    class Meta:
        # Since problem_builder isn't added to INSTALLED_APPS until it's imported,
        # specify the app_label here.
        app_label = 'qualtricssurvey'
        unique_together = (
            ('course_id', 'usage_key', 'subscription_id'),
        )
        managed = True

    course_id = CourseKeyField(max_length=255, db_index=True)
    usage_key = UsageKeyField(max_length=255, db_index=True, help_text=_(u'The course block identifier.'))
    subscription_id = models.CharField(max_length=50, db_index=True, help_text=_(u'The subscription id from Qualtrics.'))
    
    # new entry - we are checking because we want to only have one callback for the xblock location
   
class SurveyStatus(models.Model):
    """
    Defines a way to see if a given Qualtrics survey has been completed and graded
    """
    class Meta:
        # Since problem_builder isn't added to INSTALLED_APPS until it's imported,
        # specify the app_label here.
        app_label = 'qualtricssurvey'
        unique_together = (
            ('usage_key', 'user_id'),
        )
        managed = True

    user_id = models.IntegerField(db_index=True)
    usage_key = UsageKeyField(max_length=255, db_index=True, primary_key = True, help_text=_(u'The course block identifier.'))
    status = models.CharField(max_length = 10, db_index=True, help_text=_(u'The current completion status of the survey '))
    # new entry - we are checking because we want to only have one callback for the xblock location

class CourseDetailsXBlockMixin(object):
    """
    Handles all course related information from the platform.
    """

    def _get_context(self, block):
        """
        Return section, subsection, and unit names for `block`.
        """
        block_names_by_type = {}
        block_iter = block
        while block_iter:
            block_iter_type = block_iter.scope_ids.block_type
            block_names_by_type[block_iter_type] = block_iter.display_name_with_default
            block_iter = block_iter.get_parent() if block_iter.parent else None
        section_name = block_names_by_type.get('chapter', '')
        subsection_name = block_names_by_type.get('sequential', '')
        unit_name = block_names_by_type.get('vertical', '')
        return section_name, subsection_name, unit_name

    def _get_context_course_advanced_settings(self, block):
        """
        Return CMS Advanced Settings
        """
        block_iter = block
        qs_course_institution = 'None'
        qs_course_instructor = 'None'
        qs_course_term = 'perpetual'
        while block_iter:
            block_iter_type = block_iter.scope_ids.block_type
    
            if block_iter_type == 'course':  
                qs_course_institution = block_iter.qualtrics_institution
                qs_course_instructor = block_iter.qualtrics_instructors
                qs_course_term = block_iter.qualtrics_term
            
            block_iter = block_iter.get_parent() if block_iter.parent else None

        return qs_course_institution, qs_course_instructor, qs_course_term

    @property
    def course_id(self):
        try:
            raw_course_id = getattr(self.runtime, 'course_id', None)
        except AttributeError:
            return None

        return str(raw_course_id)

    @property
    def course_name(self):
        try:
            raw_course_id = getattr(self.runtime, 'course_id', None) 
        except AttributeError:
            return None

        return CourseOverview.get_from_id(raw_course_id).display_name

    @property
    def module_name(self):
        source_block_id_str = str(self.location)
        try:
            usage_key = UsageKey.from_string(source_block_id_str)
        except InvalidKeyError:
            raise ValueError("Could not find the specified Block ID.")
        
        src_block = modulestore().get_item(usage_key)
        section_name, subsection_name, unit_name = self._get_context(src_block)
        return section_name

    @property
    def course_org(self):
        try:
            raw_course_id = getattr(self.runtime, 'course_id', None)
        except AttributeError:
            return None

        return str(raw_course_id.org)

    @property
    def course_number(self):
        try:
            raw_course_id = getattr(self.runtime, 'course_id', None)
        except AttributeError:
            return None
            
        return str(raw_course_id.course)

    @property
    def course_run(self):
        try:
            raw_course_id = getattr(self.runtime, 'course_id', None)
        except AttributeError:
            return None           

        return str(raw_course_id.run)
    
    @property
    def course_start_date(self):
        try:
            raw_course_id = getattr(self.runtime, 'course_id', None) 
        except AttributeError:
            return ""
        # if (str(CourseOverview.get_from_id(raw_course_id).end_date) != 'None'):
        #     return  str(CourseOverview.get_from_id(raw_course_id).start_date)
        # return  str(CourseOverview.get_from_id(raw_course_id).start_date.date())

        # datetime = str(CourseOverview.get_from_id(raw_course_id).start_date)
        # if " " in datetime:
        #     date = datetime.split(' ')
        #     return date[0]
        # else:
        #     return datetime

        if CourseOverview.get_from_id(raw_course_id).start_date is None:
            return ""

        return str(CourseOverview.get_from_id(raw_course_id).start_date.date())

    @property
    def course_end_date(self):
        try:
            raw_course_id = getattr(self.runtime, 'course_id', None) 
        except AttributeError:
            return ""

        if CourseOverview.get_from_id(raw_course_id).end_date is None:
            return ""

        return str(CourseOverview.get_from_id(raw_course_id).end_date.date())
    
    @property
    def course_institution(self):
        source_block_id_str = str(self.location)
        try:
            usage_key = UsageKey.from_string(source_block_id_str)
        except InvalidKeyError:
            raise ValueError("Could not find the specified Block ID.")
            
        src_block = modulestore().get_item(usage_key)
        institution, instructors, term = self._get_context_course_advanced_settings(src_block)
        return institution
    
    @property
    def course_instructors(self):
        source_block_id_str = str(self.location)
        try:
            usage_key = UsageKey.from_string(source_block_id_str)
        except InvalidKeyError:
            raise ValueError("Could not find the specified Block ID.")
    
        src_block = modulestore().get_item(usage_key)
        institution, instructors, term = self._get_context_course_advanced_settings(src_block)
        
        return instructors

    @property
    def course_term(self):
        source_block_id_str = str(self.location)
        try:
            usage_key = UsageKey.from_string(source_block_id_str)
        except InvalidKeyError:
            raise ValueError("Could not find the specified Block ID.")
            
        src_block = modulestore().get_item(usage_key)
        institution, instructors, term = self._get_context_course_advanced_settings(src_block)
        return term

class QualtricsSurveyModelMixin(ScorableXBlockMixin, CourseDetailsXBlockMixin):
    """
    Handle data access for XBlock instances
    """
    survey_completed = False

    editable_fields = [
        'display_name',
        'survey_id',
        'your_university',
        # 'link_text',
        # 'param_name',
        'message',
        'course_id_override',
        'course_name_override',
        'course_org_override',
        'course_number_override',
        'course_run_override',
        'course_term_override',
        'course_start_date_override',
        'course_end_date_override',
        'course_institution_override',
        'course_instructors_override',
        'show_simulation_exists',
        'show_meta_information',
        'weight'
    ]
    course_id_override = String(
        display_name=_('Course Identifier:'),
        default='',
        scope=Scope.settings,
        help=_(
            'Enter in the course identifier override with '
            'following format: {key type}:{org}+{course}+{run} (e.g. course-v1:edX+DemoX+2014) or {org}/{course}/{run} (e.g. edX/DemoX/2014).'
        ),
    )
    course_name_override = String(
        display_name=_('Course Name:'),
        default='',
        scope=Scope.settings,
        help=_(
            'Enter in the course name override.'
        ),
    )
    course_number_override = String(
        display_name=_('Course Number:'),
        default='',
        scope=Scope.settings,
        help=_(
            'Enter in the course number override.'
        ),
    )
    course_org_override = String(
        display_name=_('Course Organization:'),
        default='',
        scope=Scope.settings,
        help=_(
            'Enter in the course organization override.'
        ),
    )
    course_run_override = String(
        display_name=_('Course Run:'),
        default='',
        scope=Scope.settings,
        help=_(
            'Enter in the course run override.'
        ),
    )
    course_term_override = String(
        display_name=_('Course Term:'),
        default='',
        scope=Scope.settings,
        help=_(
            'Enter in the course term override (e.g. "2015_Fall" or "2021_Spring").'
        ),
    )
    course_start_date_override = String(
        display_name=_('Course Start Date:'),
        default='',
        scope=Scope.settings,
        help=_(
            'Enter in the course start date override (e.g. "2019-08-20").'
        ),
    )
    course_end_date_override = String(
        display_name=_('Course End Date:'),
        default='',
        scope=Scope.settings,
        help=_(
            'Enter in the course start date override (e.g. "2019-08-20").'
        ),
    )
    course_institution_override = String(
        display_name=_('Course Institution:'),
        default='',
        scope=Scope.settings,
        help=_(
            'Enter in the course institution override (e.g. "Clemson").'
        ),
    )
    course_instructors_override = List(
        display_name=_('Course Instructor(s):'),
        default=[],
        scope=Scope.settings,
        help=_(
            'Enter in the course instructor(s) override. If there are multiple instructors use a comma to seperate values. (e.g. ["John Smith", "Sally Smith"])'
        ),
    )
    display_name = String(
        display_name=_('Display Name:'),
        default='Qualtrics Survey',
        scope=Scope.settings,
        help=_(
            'This name appears in the horizontal navigation at the top '
            'of the page.'
        ),
    )
    # link_text = String(
    #     display_name=_('Link Text:'),
    #     default='Begin Survey',
    #     scope=Scope.settings,
    #     help=_('This is the text that will link to your survey.'),
    # )
    message = String(
        display_name=_('Message:'),
        default='We need your help! Please take time now to complete this survey; your feedback '
            'will help us improve this curriculum for other learners. Once you have completed '
            'the survey please continue the course by clicking the next button. Thanks! ',
        scope=Scope.settings,
        help=_(
            'This is the text that will be displayed '
            'above the link to your survey.'
        ),
    )
    # param_name = String(
    #     display_name=_('Param Name:'),
    #     default='a',
    #     scope=Scope.settings,
    #     help=_(
    #         'This is the name for the User ID parameter in the url. '
    #         'If blank, User ID is ommitted from the url.'
    #     ),
    # )
    show_simulation_exists = Boolean(
        display_name=_("Simulation Exists"),
        help=_("Displays simulation questions from the survey when the query parameters is passed. "
               "This is disabled by default."),
        scope=Scope.settings,
        default=False
    )
    show_meta_information = Boolean(
        display_name=_("Show Qualtrics Survey Meta Information"),
        help=_("Displays 'meta' information about the survey to show query parameters passed. "
               "A default value can be set in Advanced Settings."),
        scope=Scope.settings,
        default=False
    )
    survey_id = String(
        display_name=_('Survey ID:'),
        default='Enter your survey ID here.',
        scope=Scope.settings,
        help=_(
            'This is the ID that Qualtrics uses for the survey, which can '
            'include numbers and letters, and should be entered in the '
            'following format: SV_###############'
        ),
    )
    your_university = String(
        display_name=_('Your University:'),
        default='clemson',
        scope=Scope.settings,
        help=_('This is the name of your university.'),
    )

    weight = Float(
        display_name=_("Problem Weight"),
        default=0,
        help=_("Defines the number of points each problem is worth. "
               "If the value is not set, each response field in the problem is worth one point."),
        values={"min": 0, "step": .1},
        scope=Scope.settings
    )
    score = ScoreField(
        help=_("Dictionary with the current student score"), 
        scope=Scope.user_state, 
        enforce_type=False)
    
    earned_score = 0
    has_score = True
          
    @property
    def descriptor(self):
        """
        Returns this XBlock object.
        This is for backwards compatibility with the XModule API.
        Some LMS code still assumes a descriptor attribute on the XBlock object.
        See courseware.module_render.rebind_noauth_module_to_user.
        """
        return self

    # pylint: disable=no-member
    def get_anon_id(self):
    #     """
    #     Return an anonymous user id
    #     """
         try:
            user_id = self.xmodule_runtime.anonymous_student_id
         except AttributeError:
             user_id = -1
         return user_id

    # pylint: disable=no-member
    def get_course_id(self):
        """
        Return the course_id of the course where this XBlock is used.
        Encode return value for Qualtrics query parameter usage.
        """
        if self.course_id_override:
            return six.text_type(six.moves.urllib.parse.quote(self.course_id_override))
            
        return six.text_type(six.moves.urllib.parse.quote(self.course_id))

    # pylint: disable=no-member
    def get_course_name(self):
        """
        Return the course_name of the course where this XBlock is used.
        Encode return value for Qualtrics query parameter usage.
        """
        if self.course_name_override:
            return six.text_type(six.moves.urllib.parse.quote(self.course_name_override))

        return six.text_type(six.moves.urllib.parse.quote(self.course_name))
        
    # pylint: disable=no-member
    def get_course_org(self):
        """
        Return the course_org of the course where this XBlock is used.
        Encode return value for Qualtrics query parameter usage.
        """
        if self.course_org_override:
            return six.text_type(six.moves.urllib.parse.quote(self.course_org_override))

        return six.text_type(six.moves.urllib.parse.quote(self.course_org))

    # pylint: disable=no-member
    def get_course_number(self):
        """
        Return the course_number of the course where this XBlock is used.
        Encode return value for Qualtrics query parameter usage.
        """
        if self.course_number_override:
            return six.text_type(six.moves.urllib.parse.quote(self.course_number_override))

        return six.text_type(six.moves.urllib.parse.quote(self.course_number))

    # pylint: disable=no-member
    def get_course_run(self):
        """
        Return the course_run of the course where this XBlock is used.
        Encode return value for Qualtrics query parameter usage.
        """
        if self.course_run_override:
            return six.text_type(six.moves.urllib.parse.quote(self.course_run_override))

        return six.text_type(six.moves.urllib.parse.quote(self.course_run))

    # pylint: disable=no-member
    def get_course_term(self):
        """
        Return the course_term of the course where this XBlock is used.
        Encode return value for Qualtrics query parameter usage.
        """
        if self.course_term_override:
            return six.text_type(six.moves.urllib.parse.quote(self.course_term_override))

        return six.text_type(six.moves.urllib.parse.quote(self.course_term))

    def get_course_start_date(self):
        """
        Return the course_start_date of the course where this XBlock is used.
        Encode return value for Qualtrics query parameter usage.
        """
        if self.course_start_date_override:
            return six.text_type(six.moves.urllib.parse.quote(self.course_start_date_override))

        return six.text_type(six.moves.urllib.parse.quote(self.course_start_date))

    def get_course_end_date(self):
        """
        Return the course_start_date of the course where this XBlock is used.
        Encode return value for Qualtrics query parameter usage.
        """
        if self.course_end_date_override:
            return six.text_type(six.moves.urllib.parse.quote(self.course_end_date_override))

        return six.text_type(six.moves.urllib.parse.quote(self.course_end_date))
        

    def get_course_institution(self):
        """
        Return the course_institution of the course where this XBlock is used.
        Encode return value for Qualtrics query parameter usage.
        """
        if self.course_institution_override:
            return six.text_type(six.moves.urllib.parse.quote(self.course_institution_override))

        return six.text_type(six.moves.urllib.parse.quote(self.course_institution))

    def get_course_instructors(self):
        """
        Return the course_instructor of the course where this XBlock is used.
        Encode return value for Qualtrics query parameter usage.
        """
        if self.course_instructors_override:
            return six.text_type(six.moves.urllib.parse.quote(', '.join(self.course_instructors_override)))

        return six.text_type(six.moves.urllib.parse.quote(', '.join(self.course_instructors)))
    
    def get_course_module_name(self):
        """
        Return the module_name of the course where this XBlock is used.
        """
        return self.module_name

    def should_show_simulation_exists(self):
        """
        Return True/False to indicate whether to show the "Simulation Exists" questions.
        """
        return self.show_simulation_exists

    def get_survey_id(self) :
        return self.survey_id


    # pylint: disable=no-member
    def should_show_meta_information(self):
        """
        Return True/False to indicate whether to show the "Show Qualtrics Survey Meta Information" information.
        """
        return self.show_meta_information
              
    def max_score(self):
        """
        Return the weight of the problem. This method is in the staff debug information
        """
        return self.weight

    def get_is_graded(self):
        try:
            survey_status = SurveyStatus.objects.get(usage_key=self.location, user_id=self.xmodule_runtime.user_id).status
            if (survey_status == "Complete"):
                is_graded = "Graded"
                return is_graded
        except:
            pass

        is_graded = "Ungraded"   
        return is_graded

    def get_earned_score(self):
        return self.score.raw_earned

    def set_earned_score(self):
        self.earned_score = self.weight

    def publish_grade(self):
        grade_dict = {
            'value': self.score.raw_earned,
            'max_value': self.score.raw_possible,
        }
        self.runtime.publish(self, "grade", grade_dict)

    @XBlock.json_handler
    def get_survey_status(self, data, suffix=''):
        try:
            survey_status = SurveyStatus.objects.get(usage_key=self.location, user_id=self.xmodule_runtime.user_id).status
                
        except:
            survey_status = "Incomplete"
            grade = 0

        # Prevents dividing by zero when computing weighted score for unweighted survey
        if (self.score.raw_possible != 0) :
            earned_score = (self.score.raw_earned/self.score.raw_possible) * self.weight
        
        else: 
            earned_score = 0


        return {'survey_status': survey_status, 'max_score': self.weight, 'earned_score': earned_score}
        

    @QualtricsHandlersMixin.x_www_form_handler
    def end_survey(self, data, suffix=''):  # pylint: disable=unused-argument
        """
        Called upon completion of the survey
        """
        
        survey_id = data.get("SurveyID")
        response_id = data.get("ResponseID")
        url = "https://clemson.qualtrics.com/API/v3/surveys/{}/responses/{}".format(survey_id, response_id)

        payload={}
        headers = {
        'X-API-TOKEN': 'bJjfXqGYjXqp0triy3dnRmwD1vZ6lXFeAw41GTLW'
        }

        response_survey = requests.request("GET", url, headers=headers, data=payload)

        data_response_survey = response_survey.json()
        
        response = {
            "Message": "Data processed from the Qualtrics Event Subscription API postback `surveyengine.completedResponse` event."
        }
        status = data.get("Status")

        if status == "Complete":
            result = data_response_survey["result"]
            values = result["values"]
            real_user = user_by_anonymous_id(values["anonymous_user_id"])
            self.system.rebind_noauth_module_to_user(self, real_user)

            self.set_earned_score()
            score = self.calculate_score()
            self.set_score(score)
            self.publish_grade()
        
            # Updates database survey status to complete
            survey_status = SurveyStatus.objects.get(usage_key=self.location, user_id=real_user.id)
            survey_status.status='Complete'
            survey_status.save()

        return response

    def has_submitted_answer(self):
        """
        Currently unused.
        """
        return self.done

    def set_score(self, score):
        """
        Sets the internal score for the problem. This is not derived directly
        from the internal LCP in keeping with the ScorableXBlock spec.
        """
        self.score = score

    def get_score(self):
        """
        Returns the score currently set on the block.
        """
        return self.score

    def calculate_score(self):
        """
        Returns the score calculated from the current problem state.
        """
        return Score(raw_earned=self.earned_score, raw_possible=self.weight)