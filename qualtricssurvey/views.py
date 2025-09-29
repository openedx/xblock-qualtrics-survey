"""
Handle view logic for the XBlock
"""
from urllib.parse import parse_qsl
from urllib.parse import urlencode

try:
    from xblock.utils.resources import ResourceLoader
    from xblock.utils.studio_editable import StudioEditableXBlockMixin
except ModuleNotFoundError:
    # For backward compatibility with releases older than Quince.
    from xblockutils.resources import ResourceLoader
    from xblockutils.studio_editable import StudioEditableXBlockMixin

from .mixins.fragment import XBlockFragmentBuilderMixin


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
        query_params = self._user_query_params()
        query_params.extend(self._extra_query_params())
        query_string = ''
        if query_params:
            query_string = f"?{urlencode(query_params, doseq=True)}"
        context.update({
            'xblock_id': str(self.scope_ids.usage_id),
            'survey_id': self.survey_id,
            'your_university': self.your_university,
            'link_text': self.link_text,
            'query_string': query_string,
            'message': self.message,
        })
        return context

    def _user_query_params(self):
        """
        Return query parameters derived from the current user.
        """
        params = []
        runtime = getattr(self, 'runtime', None)
        if not runtime:
            return params

        try:
            user_service = runtime.service(self, 'user')
        except Exception:  # pragma: no cover - service may be unavailable
            user_service = None

        user = user_service.get_current_user() if user_service else None

        opt_attrs = getattr(user, 'opt_attrs', {}) if user else {}
        user_id = getattr(user, 'user_id', None)
        if not user_id and hasattr(opt_attrs, 'get'):
            user_id = opt_attrs.get('edx-platform.user_id')

        emails = getattr(user, 'emails', []) if user else []
        primary_email = emails[0] if emails else None

        if not user_id:
            anonymous_id = getattr(runtime, 'anonymous_student_id', None)
            if not anonymous_id:
                xmodule_runtime = getattr(self, 'xmodule_runtime', None)
                anonymous_id = getattr(
                    xmodule_runtime,
                    'anonymous_student_id',
                    None,
                )
            user_id = anonymous_id

        if user_id:
            params.append(('edxuid', user_id))

        if primary_email:
            params.append(('email', primary_email))

        return params

    def _extra_query_params(self):
        """
        Return query parameters defined by the author.
        """
        extra_params = getattr(self, 'extra_params', '') or ''
        extra_params = extra_params.strip()
        if not extra_params:
            return []

        cleaned = extra_params.lstrip('&?')
        if not cleaned:
            return []

        parsed = parse_qsl(cleaned, keep_blank_values=True)
        return parsed
