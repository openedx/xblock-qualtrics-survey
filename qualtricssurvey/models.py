"""
Handle data access logic for the XBlock
"""

import six
from datetime import datetime

from django.utils.translation import ugettext_lazy as _
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from xblock.fields import Scope
from xblock.fields import Boolean, String

from opaque_keys.edx.keys import UsageKey
from xmodule.modulestore.django import modulestore

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
                qs_course_instructor = block_iter.qualtrics_instructor_info
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
            return None
        if (str(CourseOverview.get_from_id(raw_course_id).end_date) != 'None'):
            return  str(CourseOverview.get_from_id(raw_course_id).start_date)
        return  str(CourseOverview.get_from_id(raw_course_id).start_date.date())

        datetime = str(CourseOverview.get_from_id(raw_course_id).start_date)
        if " " in datetime:
            date = datetime.split(' ')
            return date[0]
        else :
            return datetime

    @property
    def course_end_date(self):
        try:
            raw_course_id = getattr(self.runtime, 'course_id', None) 
        except AttributeError:
            return None
        if (str(CourseOverview.get_from_id(raw_course_id).end_date) != 'None'):
            return  str(CourseOverview.get_from_id(raw_course_id).end_date.date())
            date = datetime.split(' ')
            return date[0]
        else :
            return datetime

        return  str(CourseOverview.get_from_id(raw_course_id).end_date)
    
    @property
    def course_institution(self):
        source_block_id_str = str(self.location)
        try:
            usage_key = UsageKey.from_string(source_block_id_str)
        except InvalidKeyError:
            raise ValueError("Could not find the specified Block ID.")
            
        src_block = modulestore().get_item(usage_key)
        institution,  instructor, term = self._get_context_course_advanced_settings(src_block)
        return institution
    
    @property
    def course_instructor(self):
        source_block_id_str = str(self.location)
        try:
            usage_key = UsageKey.from_string(source_block_id_str)
        except InvalidKeyError:
            raise ValueError("Could not find the specified Block ID.")
    
        src_block = modulestore().get_item(usage_key)
        institution, instructor, term = self._get_context_course_advanced_settings(src_block)
        
        return instructor

    @property
    def course_term(self):
        source_block_id_str = str(self.location)
        try:
            usage_key = UsageKey.from_string(source_block_id_str)
        except InvalidKeyError:
            raise ValueError("Could not find the specified Block ID.")
            
        src_block = modulestore().get_item(usage_key)
        institution, instructor, term = self._get_context_course_advanced_settings(src_block)
        return term

class QualtricsSurveyModelMixin(CourseDetailsXBlockMixin):
    """
    Handle data access for XBlock instances
    """

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
        'course_instructor_override',
        'show_simulation_exists',
        'show_meta_information',
    ]
    course_id_override = String(
        display_name=_('Course Identifier:'),
        default='%%COURSE_ID%%',
        scope=Scope.settings,
        help=_(
            'Enter in the Open edX course identifier override with '
            'following format: {key type}:{org}+{course}+{run} (e.g. course-v1:edX+DemoX+2014) or {org}/{course}/{run} (e.g. edX/DemoX/2014). '
            'Default value of %%COURSE_ID%% will pull automatically from the platform.'
        ),
    )
    course_name_override = String(
        display_name=_('Course Name:'),
        default='%%COURSE_NAME%%',
        scope=Scope.settings,
        help=_(
            'Enter in the Open edX course name override. '
            'Default value of %%COURSE_NAME%% will pull automatically from the platform.'
        ),
    )
    course_number_override = String(
        display_name=_('Course Number:'),
        default='%%COURSE_NUMBER%%',
        scope=Scope.settings,
        help=_(
            'Enter in the Open edX course number override.'
            'Default value of %%COURSE_NUMBER%% will pull automatically from the platform.'
        ),
    )
    course_org_override = String(
        display_name=_('Course Organization:'),
        default='%%COURSE_ORG%%',
        scope=Scope.settings,
        help=_(
            'Enter in the Open edX course organization override.'
            'Default value of %%COURSE_ORG%% will pull automatically from the platform.'
        ),
    )
    course_run_override = String(
        display_name=_('Course Run:'),
        default='%%COURSE_RUN%%',
        scope=Scope.settings,
        help=_(
            'Enter in the Open edX course run override.'
            'Default value of %%COURSE_RUN%% will pull automatically from the platform.'
        ),
    )
    course_term_override = String(
        display_name=_('Course Term:'),
        default='perpetual',
        scope=Scope.settings,
        help=_(
            'Enter in the Open edX course term override (e.g. "2019_Fall" or "2021_Spring").'
            'Default value of %%COURSE_TERM%% will pull automatically from the platform.'
        ),
    )
    course_start_date_override = String(
        display_name=_('Course Start Date:'),
        default='%%COURSE_START_DATE%%',
        scope=Scope.settings,
        help=_(
            'Enter in the Open edX course start date override (e.g. "08/20/2019").'
            'Default value of %%COURSE_START_DATE%% will pull automatically from the platform.'
        ),
    )
    course_end_date_override = String(
        display_name=_('Course End Date:'),
        default='%%COURSE_END_DATE%%',
        scope=Scope.settings,
        help=_(
            'Enter in the Open edX course start date override (e.g. "08/20/2019").'
            'Default value of %%COURSE_START_DATE%% will pull automatically from the platform.'
        ),
    )
    course_institution_override = String(
        display_name=_('Course Institution:'),
        default='None',
        scope=Scope.settings,
        help=_(
            'Enter in the Open edX course institution override (e.g. "Clemson").'
            'Default value will be set to None'
        ),
    )
    course_instructor_override = String(
        display_name=_('Course Instructor:'),
        default='None',
        scope=Scope.settings,
        help=_(
            'Enter in the Open edX course instructor override. If there are multiple instructors use a comma to seperate values.'
            'Default value will be set to None'
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

    # pylint: disable=no-member
    # def get_anon_id(self):
    #     """
    #     Return an anonymous user id
    #     """
    #     try:
    #         user_id = self.xmodule_runtime.anonymous_student_id
    #     except AttributeError:
    #         user_id = -1
    #     return user_id

    # pylint: disable=no-member
    def get_course_id(self):
        """
        Return the course_id of the course where this XBlock is used.
        Substitute %%-encoded keywords in the XBlock field with actual string.
        """
        if self.course_id_override is not None and self.course_id is not None:
            # Substitute all %%-encoded keywords in the message body
            return six.text_type(six.moves.urllib.parse.quote(self.course_id_override.replace("%%COURSE_ID%%", self.course_id)))
            
        return six.text_type(six.moves.urllib.parse.quote(self.course_id_override))

    # pylint: disable=no-member
    def get_course_name(self):
        """
        Return the course_name of the course where this XBlock is used.
        Substitute %%-encoded keywords in the XBlock field with actual string.
        """
        if self.course_name_override is not None and self.course_name is not None:
            # Substitute all %%-encoded keywords in the message body
            return six.text_type(six.moves.urllib.parse.quote(self.course_name_override.replace("%%COURSE_NAME%%", self.course_name)))

        return self.course_name_override 

    # pylint: disable=no-member
    def get_course_org(self):
        """
        Return the course_org of the course where this XBlock is used.
        Substitute %%-encoded keywords in the XBlock field with actual string.
        """
        if self.course_org_override is not None and self.course_org is not None:
            # Substitute all %%-encoded keywords in the message body
            return six.text_type(six.moves.urllib.parse.quote(self.course_org_override.replace("%%COURSE_ORG%%", self.course_org)))

        return self.course_org_override

    # pylint: disable=no-member
    def get_course_number(self):
        """
        Return the course_number of the course where this XBlock is used.
        Substitute %%-encoded keywords in the XBlock field with actual string.
        """
        if self.course_number_override is not None and self.course_number is not None:
            # Substitute all %%-encoded keywords in the message body
            return six.text_type(six.moves.urllib.parse.quote(self.course_number_override.replace("%%COURSE_NUMBER%%", self.course_number)))

        return self.course_number_override

    # pylint: disable=no-member
    def get_course_run(self):
        """
        Return the course_run of the course where this XBlock is used.
        Substitute %%-encoded keywords in the XBlock field with actual string.
        """
        if self.course_run_override is not None and self.course_run is not None:
            # Substitute all %%-encoded keywords in the message body
            return six.text_type(six.moves.urllib.parse.quote(self.course_run_override.replace("%%COURSE_RUN%%", self.course_run)))

        return self.course_run_override

    # pylint: disable=no-member
    def get_course_term(self):
        """
        Return the course_term of the course where this XBlock is used.
        Substitute %%-encoded keywords in the XBlock field with actual string.
        """
        if self.course_term_override is not None:
            if self.course_term_override != 'perpetual':
            # Substitute all %%-encoded keywords in the message body
                return self.course_term_override

        return self.course_term

    def get_course_start_date(self):
        """
        Return the course_start_date of the course where this XBlock is used.
        Substitute %%-encoded keywords in the XBlock field with actual string.
        """
        if self.course_start_date_override is not None:
            # Substitute all %%-encoded keywords in the message body
            return six.text_type(six.moves.urllib.parse.quote(self.course_start_date_override.replace("%%COURSE_START_DATE%%", self.course_start_date)))

        return self.course_start_date_override

    def get_course_end_date(self):
        """
        Return the course_start_date of the course where this XBlock is used.
        Substitute %%-encoded keywords in the XBlock field with actual string.
        """
        if self.course_end_date_override is not None:
            # Substitute all %%-encoded keywords in the message body
            return six.text_type(six.moves.urllib.parse.quote(self.course_end_date_override.replace("%%COURSE_END_DATE%%", self.course_end_date)))

        return self.course_end_date_override
        

    def get_course_institution(self):
        """
        Return the course_institution of the course where this XBlock is used.
        Substitute %%-encoded keywords in the XBlock field with actual string.
        """
        if self.course_institution_override is not None:
            if self.course_institution_override != "None": #self.course_institution_override.default:
            # Substitute all %%-encoded keywords in the message body
                return self.course_institution_override

        return self.course_institution

    def get_course_instructor(self):
        """
        Return the course_instructor of the course where this XBlock is used.
        Substitute %%-encoded keywords in the XBlock field with actual string.
        """
        if self.course_instructor_override is not None:
            if self.course_instructor_override != "None":
                names = str(self.course_instructor_override)
                names =names.replace(" ", "")

                return names

        instructors = self.course_instructor
        encoded_names = str(instructors.get('instructors'))
        encoded_names = names.replace("'", "")
        encoded_names = names.replace("[", "")
        encoded_names = names.replace("]", "")
        encoded_names = names.replace(" ", "")
    
        return encoded_names
    
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


    # pylint: disable=no-member
    def should_show_meta_information(self):
        """
        Return True/False to indicate whether to show the "Show Qualtrics Survey Meta Information" information.
        """
        return self.show_meta_information

