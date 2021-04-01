# coding=utf-8
"""Utils."""

from crams.constants import api


class CramsAPIActionState:
    """class CramsAPIActionState."""
    def __init__(self, parent_obj):
        self.user_erb_roles = list()
        self.error_message = None
        if not parent_obj:
            self.error_message = 'CramsActionState: invalid object'
            return

        self.existing_instance = parent_obj.instance
        self.is_update_action = self.existing_instance is not None
        self.is_create_action = not self.is_update_action
        self.is_partial_action = parent_obj.partial
        self.is_clone_action = False
        self.user_erb_roles_dict = dict()

        if not parent_obj.context or 'request' not in parent_obj.context:
            self.error_message = '"context" object not found, required to ' \
                                 + 'identify current user.'
            raise Exception(self.error_message)

        self.rest_request = parent_obj.context.get('request', None)

        self.is_draft_status_requested = False
        if self.rest_request and api.REQUEST_PARAM_DRAFT \
                in self.rest_request.query_params:
            self.is_draft_status_requested = True

        self.override_data = parent_obj.context.get(api.OVERRIDE_READONLY_DATA,
                                                    None)
        if self.override_data:
            if api.CLONE in self.override_data:
                if not self.existing_instance:
                    self.error_message = 'existing_instance required for \
                                         Clone Action'
                    return
                else:
                    self.is_clone_action = True
                    self.is_update_action = False

        # noinspection PyPep8
        self.update_from_existing = self.is_partial_action or \
            self.is_clone_action

    def set_user_erb_roles(self, key, erb_role_list):
        self.user_erb_roles[key] = erb_role_list
