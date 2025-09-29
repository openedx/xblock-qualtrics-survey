"""
Handle data access logic for the XBlock
"""

from django.utils.translation import gettext_lazy as _
from xblock.fields import Scope
from xblock.fields import String


class QualtricsSurveyModelMixin:
    """
    Handle data access for XBlock instances
    """

    editable_fields = [
        "display_name",
        "survey_id",
        "your_university",
        "link_text",
        "extra_params",
        "message",
    ]
    display_name = String(
        display_name=_("Display Name:"),
        default="Qualtrics Survey",
        scope=Scope.settings,
        help=_(
            "This name appears in the horizontal navigation at the top "
            "of the page."
        ),
    )
    link_text = String(
        display_name=_("Link Text:"),
        default="Begin Survey",
        scope=Scope.settings,
        help=_("This is the text that will link to your survey."),
    )
    message = String(
        display_name=_("Message:"),
        default="The survey will open in a new browser tab or window.",
        scope=Scope.settings,
        help=_(
            "This is the text that will be displayed "
            "above the link to your survey."
        ),
    )
    extra_params = String(
        display_name=_("Extra Parameters:"),
        default=(
            "example_param_1=example_value_1&"
            "example_param_2=example_value_2"
        ),
        scope=Scope.settings,
        help=_(
            "Here you can add extra parameters to include in the survey url. "
            "you can add set of parameters and their value like:"
            "example_param_1=example_value_1&example_param_2=example_value_2"
            "Make sure it doesn't start with &"
            "If blank, extra parameters are ommitted from the url."
        ),
    )
    survey_id = String(
        display_name=_("Survey ID:"),
        default="Enter your survey ID here.",
        scope=Scope.settings,
        help=_(
            "This is the ID that Qualtrics uses for the survey, which can "
            "include numbers and letters, and should be entered in the "
            "following format: SV_###############"
        ),
    )
    your_university = String(
        display_name=_("Your University's Qualtrics ID:"),
        default="pennstate",
        scope=Scope.settings,
        help=_("This is the id of university in Qualtrics example: pennstate"),
    )
