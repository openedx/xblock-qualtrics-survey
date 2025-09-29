#!/usr/bin/env python
"""
Test the Qualtrics Survey XBlock
"""
import unittest

from unittest import mock
from opaque_keys.edx.locations import SlashSeparatedCourseKey
from xblock.field_data import DictFieldData

from qualtricssurvey.xblocks import QualtricsSurvey


def mock_an_xblock(field_overrides=None, user_service=None):
    """
    Create and return an instance of the XBlock
    """
    course_id = SlashSeparatedCourseKey('foo', 'bar', 'baz')
    runtime = mock.Mock(course_id=course_id)
    runtime.anonymous_student_id = 'anon-user-id'

    i18n_service = mock.Mock()
    i18n_service.ugettext.side_effect = lambda text: text
    i18n_service.gettext.side_effect = lambda text: text

    def local_resource_url(_block, _path):
        return 'http://example.org/resource'

    runtime.local_resource_url = mock.Mock(side_effect=local_resource_url)

    def service(_block, service_name):
        if service_name == 'user' and user_service is not None:
            return user_service
        if service_name == 'i18n':
            return i18n_service
        raise Exception('Service not available')

    runtime.service = mock.Mock(side_effect=service)

    scope_ids = mock.Mock()
    scope_ids.usage_id = 'usage-id'
    field_data = DictFieldData(field_overrides or {})
    xblock = QualtricsSurvey(runtime, field_data, scope_ids)
    xblock.xmodule_runtime = runtime
    return xblock


class TestRender(unittest.TestCase):
    """
    Test the HTML rendering of the XBlock
    """

    def setUp(self):
        self.xblock = mock_an_xblock()

    def test_render(self):
        student_view = self.xblock.student_view()
        html = student_view.content
        self.assertIsNotNone(html)
        self.assertNotEqual('', html)
        self.assertIn('qualtricssurvey_block', html)

    def test_student_view(self):
        """
        Checks the student view using the anonymous user fallback when
        runtime user services are unavailable.
        """
        xblock = self.xblock
        fragment = xblock.student_view()
        content = fragment.content
        self.assertIn('Begin Survey', content)
        self.assertIn('target="_blank"', content)
        self.assertIn(
            'href="https://pennstate.qualtrics.com/jfe/form/Enter your survey '
            'ID here.?',
            content
        )
        self.assertIn('example_param_1=example_value_1', content)
        self.assertIn('example_param_2=example_value_2', content)
        self.assertIn('?edxuid=anon-user-id', content)
        self.assertIn(xblock.message, content)

    def test_student_view_with_user_service(self):
        """
        Checks the student view when the runtime provides user information.
        """
        user = mock.Mock()
        user.user_id = None
        user.opt_attrs = {
            'edx-platform.user_id': '12345',
        }
        user.emails = ['user@example.com']
        user_service = mock.Mock()
        user_service.get_current_user.return_value = user
        xblock = mock_an_xblock(
            field_overrides={'extra_params': 'foo=bar&baz='},
            user_service=user_service,
        )

        content = xblock.student_view().content

        self.assertIn('?edxuid=12345', content)
        self.assertIn('&amp;email=user%40example.com', content)
        self.assertIn('&amp;foo=bar', content)
        self.assertIn('&amp;baz=', content)

    def test_custom_message(self):
        """
        Checks the student view with a custom message.
        """
        message = 'test message'
        xblock = self.xblock
        xblock.message = message
        fragment = xblock.student_view()
        message_html = '<p>' + message + '</p>'
        content = fragment.content
        self.assertIn(message_html, content)


if __name__ == '__main__':
    unittest.main()
