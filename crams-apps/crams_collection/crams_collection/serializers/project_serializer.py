# coding=utf-8
"""Project Serailizers."""

import logging
from rest_framework.exceptions import ParseError, PermissionDenied
from rest_framework.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.db import transaction

from crams.constants.db import APPLICANT
from crams.models import Question
from crams_contact.models import ContactRole
from crams_contact.serializers.organisation_serializers import DepartmentSerializer
from crams_log import log_process
from crams_collection.log.project_contact_log import ProjectContactLogger
from crams_collection.log.project_log import ProjectMetaLogger

from crams_collection.models import Project
from crams_collection.serializers import base_project_serializer
from crams_collection.serializers import domain_serializers
from crams_collection.serializers import grant_serializers
from crams_collection.serializers import publication_serializers
from crams_collection.serializers import question_serializers
from crams_collection.serializers.project_contact_serializer import ProjectContactSerializer


User = get_user_model()
LOG = logging.getLogger(__name__)


class ProjectSerializer(base_project_serializer.ReadOnlyProjectSerializer):
    def create_new_project_archive_existing(self, existing_project_instance):
        """
        By default all changes to Project meta data will be logged in crams_log and existing Project will be updated
        To override this logic and keep an archived copy of existing project metadata, override this method.
        """
        return existing_project_instance is None

    def _add_applicant_contact(self, new_project):
        if not self.context:
            raise ParseError(
                'ProjectSerializer: "self.context" object not found, ' +
                'required to identify current user.')

        try:
            applicant_role = ContactRole.objects.get(name=APPLICANT)
        except ContactRole.DoesNotExist:
            raise ParseError('Data Error: Contact Role Applicant not found')

        current_user = self.get_current_user()
        pc_serializer = ProjectContactSerializer(context=self.context)
        pc_serializer.add_given_user_as_project_contact(
            current_user, new_project, applicant_role)

    def _generate_unique_crams_id(self, project):
        """
        Generates a unique crams_id for the project
        This should only be used once when creating a new project
        When updating a project, it will return its existing crams_id
        """
        project.crams_id = 'CRAMS_COL_{}'.format(project.id)
        project.save()

    def validate(self, data):
        """validate.

        :param data:
        :return: :raise ValidationError:
        """
        if self.cramsActionState.error_message:
            msg = self.cramsActionState.error_message
            raise ValidationError('CramsRequestSerializer: ' + msg)

        aspect_data_param_dict = self.build_aspect_param_dict(data=data)
        self.run_pre_aspect_for_method(ProjectSerializer.validate.__name__, aspect_data_param_dict)
        self.validate_concurrent_update()
        self.run_post_aspect_for_method(ProjectSerializer.validate.__name__, aspect_data_param_dict)
        return data

    def validate_concurrent_update(self):
        if self.cramsActionState.is_update_action:
            project = self.cramsActionState.existing_instance
            if project.current_project:
                concurrent_user = project.current_project.updated_by
                raise ParseError('concurrent update: {} has updated '
                                 'project, please refresh and try again'
                                 .format(repr(concurrent_user)))

    @transaction.atomic
    def update(self, instance, validated_data):
        # for partial updates with no data other than override data,
        # the validate method would not have been invoked, hence repeat
        # actionState setup
        """update.

        :param instance:
        :param validated_data:
        :return:
        """
        aspect_data_dict = self.build_aspect_param_dict(validated_data=validated_data, existing_instance=instance)
        self.run_pre_aspect_for_method(ProjectSerializer.update.__name__, aspect_data_dict)
        
        current_contact = self.contact
        if self.project_contact_has_readonly_access(instance, current_contact):
            msg = 'User does not have update access on Project '
            raise PermissionDenied(msg + instance.title)

        new_project = self.save_project(validated_data, instance)
        # if new project pk is same as the old project pk skip setting the current_project
        if new_project.id != instance.id:
            old_project_instance = instance
            old_project_instance.current_project = new_project
            old_project_instance.save()
            Project.objects.filter(current_project=old_project_instance).update(
                current_project=new_project)

        aspect_data_dict['saved_project'] = new_project
        self.run_post_aspect_for_method(ProjectSerializer.update.__name__, aspect_data_dict)
        return new_project

    @transaction.atomic
    def create(self, validated_data):
        """create.

        :param validated_data:
        :return:
        """
        aspect_data_param_dict = self.build_aspect_param_dict(validated_data=validated_data)
        self.run_pre_aspect_for_method(ProjectSerializer.create.__name__, aspect_data_param_dict)

        new_project = self.save_project(validated_data, None)
        
        self._generate_unique_crams_id(new_project)
        self._add_applicant_contact(new_project)

        aspect_data_param_dict['saved_project'] = new_project
        self.run_post_aspect_for_method(ProjectSerializer.create.__name__, aspect_data_param_dict)
        return new_project

    def update_project_question_responses(self, related_field, project_data):
        def changed_msg(questions_set, msg):
            ret_msg = msg
            for pqr_tuple in questions_set:
                question, new_response, existing_response = pqr_tuple
                ret_msg += question.key + ','
            return ret_msg

        project = project_data.get('project_obj')
        existing_project_instance = project_data.get('existing_project_instance')
        changed_fields_set = project_data.get('changed_fields_set')

        proj_question_responses_data = self.initial_data.get(related_field)

        # fetch the question id based on key
        # the question could change but still use the old id
        for qr in proj_question_responses_data:
            qu = Question.objects.filter(key=qr.get('question').get('key')).first()
            if qu:
                qr['question']['id'] = qu.id

        ret_changed_obj = \
            question_serializers.ProjectQuestionResponseSerializer.save_project_question_response(
                proj_question_responses_data, new_parent=project, old_parent=existing_project_instance)

        if ret_changed_obj.err_list:
            raise ValidationError(ret_changed_obj.err_list)

        changed_list = list()
        if ret_changed_obj.modified_related_field_set:
            base_msg = 'modified: '
            changed_list.append(changed_msg(ret_changed_obj.modified_related_field_set, base_msg))
        if ret_changed_obj.new_related_field_set:
            base_msg = 'added new: '
            changed_list.append(changed_msg(ret_changed_obj.new_related_field_set, base_msg))
        if ret_changed_obj.removed_related_field_set:
            base_msg = 'removed: '
            changed_list.append(changed_msg(ret_changed_obj.removed_related_field_set, base_msg))
        if changed_list:
            change_msg = 'Project_questions: ' + ' && '.join(changed_list)
            changed_fields_set.add(change_msg)

    def update_publications(self, related_field, project_data):
        def changed_msg(publication_ref_set, msg):
            return msg + ','.join(publication_ref_set)

        project = project_data.get('project_obj')
        existing_project_instance = project_data.get('existing_project_instance')
        changed_fields_set = project_data.get('changed_fields_set')

        publications_data = self.initial_data.get(related_field)
        obj_dict, modified_pub_set, new_pub_set, removed_pub_set = \
            publication_serializers.PublicationSerializer.save_project_publication_return_changes(
                publications_data, parent_project=project, existing_project_instance=existing_project_instance)

        changed_list = list()
        if modified_pub_set:
            base_msg = 'modified: '
            changed_list.append(changed_msg(modified_pub_set, base_msg))
        if new_pub_set:
            base_msg = 'added new: '
            changed_list.append(changed_msg(new_pub_set, base_msg))
        if removed_pub_set:
            base_msg = 'removed: '
            changed_list.append(changed_msg(removed_pub_set, base_msg))
        if changed_list:
            change_msg = 'Project_publications: ' + ' && '.join(changed_list)
            changed_fields_set.add(change_msg)

    def update_grants(self, related_field, project_data):
        def changed_msg(grant_ref_set, msg):
            ret_msg = ''
            for g_tuple in grant_ref_set:
                funding_body_and_scheme, grant_type, grant_id = g_tuple
                ret_msg += '({},{})'.format(funding_body_and_scheme, grant_type.description)
            if ret_msg:
                return msg + ret_msg

        project = project_data.get('project_obj')
        existing_project_instance = project_data.get('existing_project_instance')
        changed_fields_set = project_data.get('changed_fields_set')

        grants_data = self.initial_data.get(related_field)
        ret_changed_obj = \
            grant_serializers.GrantSerializer.save_project_grants_return_changes(
                grants_data, parent_project=project, existing_project_instance=existing_project_instance)

        if ret_changed_obj.err_list:
            raise ValidationError(ret_changed_obj.err_list)

        changed_list = list()
        if ret_changed_obj.modified_related_field_set:
            base_msg = 'modified: '
            changed_list.append(changed_msg(ret_changed_obj.modified_related_field_set, base_msg))
        if ret_changed_obj.new_related_field_set:
            base_msg = 'added new: '
            changed_list.append(changed_msg(ret_changed_obj.new_related_field_set, base_msg))
        if ret_changed_obj.removed_related_field_set:
            base_msg = 'removed: '
            changed_list.append(changed_msg(ret_changed_obj.removed_related_field_set, base_msg))
        if changed_list:
            change_msg = 'Project_grants: ' + ' && '.join(changed_list)
            changed_fields_set.add(change_msg)

    def update_domains(self, related_field, project_data):
        def changed_msg(domain_tuple_set, msg):
            for_code_list = list()
            for domain_tuple in domain_tuple_set:
                for_code, new_percentage, existing_percentage = domain_tuple
                for_code_list.append(for_code.code)
            return msg + ','.join(for_code_list)

        project = project_data.get('project_obj')
        existing_project_instance = project_data.get('existing_project_instance')
        changed_fields_set = project_data.get('changed_fields_set')

        domains_data = self.initial_data.get(related_field)
        changed_ret_obj = \
            domain_serializers.DomainSerializer.save_parent_domain_return_changes(
                domains_data, parent_project=project, existing_project_instance=existing_project_instance)
        if changed_ret_obj.err_list:
            raise ValidationError(changed_ret_obj.err_list)

        changed_list = list()
        if changed_ret_obj.modified_related_field_set:
            base_msg = 'modified: '
            changed_list.append(changed_msg(changed_ret_obj.modified_related_field_set, base_msg))
        if changed_ret_obj.new_related_field_set:
            base_msg = 'added new: '
            changed_list.append(changed_msg(changed_ret_obj.new_related_field_set, base_msg))
        if changed_ret_obj.removed_related_field_set:
            base_msg = 'removed: '
            changed_list.append(changed_msg(changed_ret_obj.removed_related_field_set, base_msg))
        if changed_list:
            change_msg = 'Project_domains: ' + ' && '.join(changed_list)
            changed_fields_set.add(change_msg)

    def update_project_contacts(self, related_field, project_data):
        aspect_data_param_dict = self.build_aspect_param_dict(project_data=project_data)
        self.run_pre_aspect_for_method(
            ProjectSerializer.update_project_contacts.__name__, aspect_data_param_dict)

        project = project_data.get('project_obj')
        current_user = project_data.get('current_user')
        aspect_data_param_dict['current_user'] = current_user
        existing_project_instance = project_data.get('existing_project_instance')
        aspect_data_param_dict['existing_project_instance'] = existing_project_instance
        changed_fields_set = project_data.get('changed_fields_set')

        project_contacts_data = self.initial_data.get(related_field)

        project_contact_obj_list = list()
        aspect_data_param_dict['project_contact_obj_list'] = project_contact_obj_list
        if project_contacts_data:
            existing_pc_set = set()
            if existing_project_instance:
                for pc in existing_project_instance.project_contacts.all():
                    pc_tuple = (pc.contact, pc.contact_role)
                    existing_pc_set.add(pc_tuple)

            pc_serializer = ProjectContactSerializer
            new_pc_set = set()

            for proj_contact_data in project_contacts_data:
                sz = pc_serializer(data=proj_contact_data, context=self.context)
                sz.is_valid(raise_exception=True)

                contact_obj = sz.validated_data.get('contact')
                role_obj = sz.validated_data.get('contact_role')
                pc_obj, created = pc_serializer.create_project_contact(contact_obj, role_obj, project)
                project_contact_obj_list.append(pc_obj)

                new_pc_tuple = (pc_obj.contact, pc_obj.contact_role)
                new_pc_set.add(new_pc_tuple)

            # Log New Project Contacts
            new_pcs = new_pc_set - existing_pc_set
            new_contacts = ''
            for new_tuple in new_pcs:
                contact, role = new_tuple
                new_contacts += '({},{})'.format(role.name, contact.email)
                ProjectContactLogger.log_project_contact_add(
                    project, contact, role, created_by_user_obj=current_user)
            if new_contacts:
                changed_fields_set.add('New Contact add:' + new_contacts)

            # Log removed Project Contacts
            removed_pcs = existing_pc_set - new_pc_set
            removed_contacts = ''
            for old_tuple in removed_pcs:
                contact, role = old_tuple
                if project == existing_project_instance:
                    obj = pc_serializer.fetch_if_exists(project, contact, role)
                    if obj:
                        obj.delete()
                removed_contacts += '({},{})'.format(role.name, contact.email)
                ProjectContactLogger.log_remove_project_contact(
                    project, contact, role, created_by_user_obj=current_user)
            if removed_contacts:
                changed_fields_set.add('Removed Contacts:' + removed_contacts)

        self.run_post_aspect_for_method(ProjectSerializer.update_project_contacts.__name__, aspect_data_param_dict)

    def save_project(self, validated_data, existing_project_instance):
        """save project.

        :param validated_data:
        :param existing_project_instance:
        :return: :raise ParseError:
        """
        aspect_data_param_dict = self.build_aspect_param_dict(
            validated_data=validated_data, existing_project_instance=existing_project_instance)
        self.run_pre_aspect_for_method(ProjectSerializer.save_project.__name__, aspect_data_param_dict)

        if 'current_project' in validated_data:
            raise ParseError(
                'Projects with current_project value set are historic, ' +
                'readonly records. Update fail')
        related_fields_update_dict = {
            # Note: include only one/many to many relationships here
            # for example: Department which is a many to one relationship (with respect to Project) is not set here
            'project_question_responses': self.update_project_question_responses,
            'publications': self.update_publications,
            'grants': self.update_grants,
            'project_contacts': self.update_project_contacts,
            'domains': self.update_domains,
            'current_project': None
        }
        related_fields = related_fields_update_dict.keys()

        project_data = dict()
        for k, v in validated_data.items():
            if k not in related_fields:
                project_data[k] = v

        # Project
        current_user = self.get_current_user()
        current_contact = self.contact
        project_data['updated_by'] = current_user
        if existing_project_instance:
            project_data['created_by'] = existing_project_instance.created_by
        else:
            project_data['created_by'] = current_user

        # Fetch project data to log
        field_fn_dict = {
            'title': None,
            'description': None,
            'notes': None,
            'department': lambda obj: DepartmentSerializer(obj).data if obj is not None else None
        }
        changed_project_fields_set, _, _ = log_process.generate_before_after_json(
            existing_project_instance, project_data, check_field_extract_fn_dict=field_fn_dict)
        changed_fields_set = set()
        if changed_project_fields_set:
            changed_fields_set = {'Changed: Project[' + ','.join(changed_project_fields_set) + ']'}

        # only save a new project if save_new flag is True
        save_new = self.create_new_project_archive_existing(existing_project_instance)
        if save_new:
            project = Project.objects.create(**project_data)
        else:
            # Updating existing project instance
            project = existing_project_instance
            if changed_project_fields_set:
                for field in changed_project_fields_set:
                    setattr(project, field, project_data.get(field))
                project.updated_by = project_data.get('updated_by')
                project.save()

        aspect_data_param_dict['save_new'] = save_new
        aspect_data_param_dict['saved_project'] = project

        # update related fields
        for k in related_fields_update_dict.keys():
            project_data[k] = validated_data.get(k)

        err_dict = dict()
        project_data['project_obj'] = project
        project_data['save_new'] = save_new
        project_data['current_user'] = current_user
        project_data['existing_project_instance'] = existing_project_instance
        project_data['changed_fields_set'] = changed_fields_set
        for related_field, update_fn in related_fields_update_dict.items():
            if update_fn:
                err_list = update_fn(related_field, project_data)
                if err_list:
                    err_dict[related_field] = err_list

        if err_dict:
            raise ValidationError(err_dict)

        # log if data has changed, both for create and update of project
        if changed_fields_set:
            if not existing_project_instance:
                log_message = 'New Project'
            else:
                log_message = ','.join(changed_fields_set)
            ProjectMetaLogger.log_project_metadata_change(
                project, existing_project_instance, current_user, message=log_message,
                contact=current_contact, sz_context=self.context)

        self.run_post_aspect_for_method(ProjectSerializer.save_project.__name__, aspect_data_param_dict)
        return project
