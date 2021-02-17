"""
Handle view logic for the XBlock
"""
from xblockutils.resources import ResourceLoader
from xblockutils.studio_editable import StudioEditableXBlockMixin

from .mixins.fragment import XBlockFragmentBuilderMixin

#xmodule.course_module import CourseFields
class QualtricsSurveyViewMixin(
        XBlockFragmentBuilderMixin,
        StudioEditableXBlockMixin,
):
    """
    Handle view logic for the XBlock
    """

    loader = ResourceLoader(__name__)
    show_in_read_only_mode = True

    def provide_context(self, context=None):
        """
        Build a context dictionary to render the student view
        """
        context = context or {}
        context = dict(context)
        # param_name = self.param_name
        # anon_user_id = self.get_anon_id()
        # user_id_string = ''
        # if param_name:
        #     user_id_string = ("{param_name}={anon_user_id}").format(
        #         param_name=param_name,
        #         anon_user_id=anon_user_id,
        #     )
        param_course_id = self.get_course_id()
        course_id_string = ("course_id={param_course_id}").format(
            param_course_id=param_course_id,
        )
        param_course_name = self.get_course_name()
        course_name_string = ("course_name={param_course_name}").format(
            param_course_name=param_course_name,
        )
        param_course_org = self.get_course_org()
        course_org_string = ("course_org={param_course_org}").format(
            param_course_org=param_course_org,
        )
        param_course_number = self.get_course_number()
        course_number_string = ("course_number={param_course_number}").format(
            param_course_number=param_course_number,
        )
        param_course_run = self.get_course_run() 
        course_run_string = ("course_run={param_course_run}").format(
            param_course_run=param_course_run,
        )
        param_course_term = self.get_course_term()
        course_term_string = ("course_term={param_course_term}").format(
            param_course_term=param_course_term,
        )
        param_course_start_date = self.get_course_start_date()
        course_start_date_string = ("course_start_date={param_course_start_date}").format(
            param_course_start_date=param_course_start_date,
        )
        param_course_end_date = self.get_course_end_date()
        course_end_date_string = ("course_end_date={param_course_end_date}").format(
            param_course_end_date=param_course_end_date,
        )
        param_course_institution = self.get_course_institution()
        course_institution_string = ("course_institution={param_course_institution}").format(
            param_course_institution=param_course_institution,
        )
        param_course_instructors = self.get_course_instructors()
        course_instructor_string = ("course_instructor={param_course_instructors}").format(
            param_course_instructors=param_course_instructors,
        )
        param_course_module_name = self.get_course_module_name()
        course_module_name_string = ("module_name={param_course_module_name}").format(
            param_course_module_name=param_course_module_name,
        )
        param_display_simulation_exists = '1' if self.should_show_simulation_exists() else '0'
        show_simulation_exists_string = ("simulation_exists={param_display_simulation_exists}").format(
            param_display_simulation_exists=param_display_simulation_exists,
        )
        param_display_meta = '1' if self.should_show_meta_information() else '0'
        show_meta_information_string = ("display_meta={param_display_meta}").format(
            param_display_meta=param_display_meta,
        )
        context.update({
            'survey_id': self.survey_id,
            'your_university': self.your_university,
            # 'link_text': self.link_text,
            # 'user_id_string': user_id_string,
            'course_id_string': course_id_string,
            'course_name_string': course_name_string,
            'course_org_string': course_org_string,
            'course_number_string': course_number_string,
            'course_run_string': course_run_string,
            'course_term_string': course_term_string,
            'course_start_date_string': course_start_date_string,
            'course_end_date_string': course_end_date_string,
            'course_institution_string': course_institution_string,
            'course_instructor_string': course_instructor_string,
            'course_module_name_string': course_module_name_string,
            #'course_module_id_string': self.module_id,
            'show_simulation_exists_string': show_simulation_exists_string,
            'show_meta_information_string': show_meta_information_string,
            'message': self.message,
        })
        
        return context
