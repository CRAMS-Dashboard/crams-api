# coding=utf-8
"""

"""
from rest_framework import exceptions
from crams_member.models import ProjectMemberStatus, ProjectJoinInviteRequest


def update_project_members_for_new_project_contact(current_cls, param_dict):
    """
    used post: project serializer update project contact
    """
    self_name = 'update_project_members_for_new_project_contact'
    project_data = param_dict.get('project_data')
    if not project_data:
        raise exceptions.ValidationError(self_name + ' aspect requires project data dict')

    project_contact_obj_list = param_dict.get('project_contact_obj_list')
    if not project_contact_obj_list:
        raise exceptions.ValidationError(self_name + ' aspect requires project contact object list')

    current_user = project_data.get('current_user')
    if not current_user:
        raise exceptions.ValidationError(self_name + ' aspect requires current user object')

    current_project = project_data.get('project_obj')
    if not current_user:
        raise exceptions.ValidationError(self_name + ' aspect requires current user object')

    # existing_project_instance can be null
    existing_project_instance = project_data.get('existing_project_instance')

    # get and update the project contacts in the corresponding ProjectJoinInviteRequest
    prj_jn_inv_req = ProjectJoinInviteRequest.objects.filter(project=current_project)
    for project_contact_obj in project_contact_obj_list:
        project = project_contact_obj.project
        contact_obj = project_contact_obj.contact

        if existing_project_instance:
            member_exists = False
            member_status = ProjectMemberStatus.objects.get(code='M')

            # if project and existing_project_instance are the same then we are doing a update
            # if they are different we are moving to a new status skip if not updating
            if project.id == existing_project_instance.id:
                # loop through the membership join invites req for user and make them a member
                for prj_member in prj_jn_inv_req:
                    if prj_member.contact == contact_obj:
                        # activate membership status
                        prj_member.status = member_status
                        prj_member.updated_by = current_user
                        prj_member.save()
                        member_exists = True
                        break
                # member not found in the loop we create a new one
                if not member_exists:
                    prj_member = ProjectJoinInviteRequest()
                    prj_member.project = project
                    prj_member.status = member_status
                    prj_member.contact = contact_obj
                    prj_member.title = contact_obj.title
                    prj_member.surname = contact_obj.surname
                    prj_member.given_name = contact_obj.given_name
                    prj_member.email = contact_obj.email
                    prj_member.created_by = current_user
                    prj_member.save()

    # loop through the membership for removed uses from project
    # if contact is not in project_contacts revoke their membership
    #  skip this next process if not updating existing status

    if existing_project_instance:
        if current_project.id == existing_project_instance.id:
            for prj_member in prj_jn_inv_req:
                member_exists = False
                for prj_cont in current_project.project_contacts.all():
                    if prj_member.contact == prj_cont.contact:
                        member_exists = True
                        break
                # if contact not found in project contact remove membership status
                if not member_exists:
                    prj_member.status = ProjectMemberStatus.objects.get(code='V')
                    prj_member.save()


def update_project_join_invite_request(current_cls, param_dict):
    """
    used post: project serializer update project
    Checks if ProjectJoinInviteRequest exists using old project,
    if found will update from old project to new project.
    """
    self_name = 'update_project_join_invite_request'
    existing_project_instance = param_dict.get('existing_project_instance')
    if not existing_project_instance:
        raise exceptions.ValidationError(self_name + ' aspect requires existing project instance object')

    saved_project_instance = param_dict.get('saved_project_instance')
    if not saved_project_instance:
        raise exceptions.ValidationError(self_name + ' aspect requires new project instance object')

    if saved_project_instance == existing_project_instance:
        # For application updated status, the no new project is created
        return

    prj_jn_inv_req_list = ProjectJoinInviteRequest.objects.filter(
        project=existing_project_instance)
    for prj_jn_inv_req in prj_jn_inv_req_list:
        prj_jn_inv_req.project = saved_project_instance
        prj_jn_inv_req.save()
