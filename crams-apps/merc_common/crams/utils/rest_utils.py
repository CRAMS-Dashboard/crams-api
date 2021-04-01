# coding=utf-8
"""

"""

from rest_framework.renderers import BrowsableAPIRenderer


def get_current_user_from_context(serializer_self):
    current_user = None
    context = None

    if hasattr(serializer_self, 'context'):
        context = serializer_self.context
        current_user = context.get('current_user', None)
        if not current_user:
            http_request = serializer_self.context.get('request', None)
            if http_request:
                current_user = http_request.user
    elif serializer_self.request:
        current_user = serializer_self.request.user
        context = dict()
        context['request'] = serializer_self.request

    return current_user, context


# reference: https://bradmontgomery.net/blog/
#                disabling-forms-django-rest-frameworks-browsable-api/
class BrowsableAPIRendererWithoutForms(BrowsableAPIRenderer):
    """Renders the browsable api, but excludes the forms."""

    def get_context(self, *args, **kwargs):
        ctx = super().get_context(*args, **kwargs)
        ctx['display_edit_forms'] = False
        return ctx

    def show_form_for_method(self, view, method, request, obj):
        """We never want to do this! So just return False."""
        return False

    def get_rendered_html_form(self, data, view, method, request):
        """Why render _any_ forms at all. This method should return
        rendered HTML, so let's simply return an empty string.
        """
        return ""
