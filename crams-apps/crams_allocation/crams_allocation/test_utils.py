from datetime import datetime
from dateutil.relativedelta import relativedelta

from django.contrib.auth import get_user_model
from mixer.backend.django import mixer

from crams.test_utils import CommonBaseTestCase
from crams_contact.test_utils import UnitTestCase
from crams_allocation import models as allocation_models
from crams_compute import models as compute_models
from crams_storage import models as storage_models
from crams_allocation.product_allocation import models as product_models
from crams_collection import models as collection_models
# from crams_collection.member import models as member_models
from crams_contact import models as contact_models
from crams_manager import models as manager_models
from crams import models as crams_models
from crams.constants import db
from crams.utils.crams_utils import get_random_string


class UnitTestCase(UnitTestCase):
    def setUp(self):
        # set up erb, erbs and funding body
        self.erb = mixer.blend(crams_models.EResearchBody, name='ERB')
        self.erbs = mixer.blend(crams_models.EResearchBodySystem, 
                                name='ERBS', e_research_body=self.erb)
        self.funding_body = mixer.blend(crams_models.FundingBody, name='FundingBody')
        self.funding_scheme = mixer.blend(crams_models.FundingScheme, 
                                          FundingScheme='FundingScheme', 
                                          funding_body=self.funding_body)
        # set up a provider for products
        self.provider = mixer.blend(crams_models.Provider,
                                    name='Provider',
                                    start_date=datetime.now(),
                                    active=True,
                                    description=get_random_string(25))
        # test org, faculty and department
        self.org = mixer.blend(contact_models.Organisation,
                               name='Test Organisation',
                               short_name='test_org')
        self.faculty = mixer.blend(contact_models.Faculty,
                                   faculty_code='testfac0001',
                                   name='Test Faculty',
                                   organisation=self.org)
        self.dept = mixer.blend(contact_models.Department,
                                      name='Test Department',
                                      department_code='testdept0001',
                                      faculty=self.faculty)
        
        # setup zone for storage product
        self.zone = mixer.blend(crams_models.Zone,
                                name='zone',
                                description='zone')
        # setup 2 forcodes
        self.forcode1 = mixer.blend(crams_models.FORCode,
                                    code='xxxxxxx1',
                                    description='FORCode 1')
        self.forcode2 = mixer.blend(crams_models.FORCode,
                                    code='xxxxxxx2',
                                    description='FORCode 2')
        # setup grant_type
        self.grant_type = mixer.blend(collection_models.GrantType,
                                      description=get_random_string(12))
        # setup storage type for storage product
        self.storage_type = mixer.blend(storage_models.StorageType,
                                        storage_type='storage_type')
        # setup compute product
        self.compute_prod = mixer.blend(compute_models.ComputeProduct,
                                        name='Compute Product',
                                        funding_body=self.funding_body,
                                        e_research_system=self.erbs,
                                        provider=self.provider,
                                        unit_cost=0,
                                        operational_cost=0,
                                        cost_unit_type=None,
                                        capacity=0)
        # setup storeage product
        self.storage_prod = mixer.blend(storage_models.StorageProduct,
                                        name='Storage Product',
                                        funding_body=self.funding_body,
                                        e_research_system=self.erbs,
                                        provider=self.provider,
                                        unit_cost=0,
                                        operational_cost=0,
                                        cost_unit_type=None,
                                        capacity=0,
                                        zone=self.zone,
                                        storage_type=self.storage_type,
                                        parent_storage_product=None)
        # setup project, request, storage_request and compute_request questions
        self.project_questions = [self.generate_question('project', 1),
                                  self.generate_question('project', 2),
                                  self.generate_question('project', 3)]
        self.request_questions = [self.generate_question('request', 1),
                                  self.generate_question('request', 2),
                                  self.generate_question('request', 3)]
        self.sp_request_questions = [self.generate_question('sp_request', 1),
                                     self.generate_question('sp_request', 2),
                                     self.generate_question('sp_request', 3)]
        self.cp_request_questions = [self.generate_question('cp_request', 1),
                                     self.generate_question('cp_request', 2),
                                     self.generate_question('cp_request', 3)]
        # fetch applicant role
        self.app_role = contact_models.ContactRole.objects.get(name=db.APPLICANT)
        # generate a project member role    
        self.prjmbr_role = self.generate_contact_role('Project Member', erb=self.erb)

    def generate_allocation_test_data(self):
        # set up erb admin user/contact
        self.admin_user, self.admin_contact, self.admin_token = \
            self.generate_erb_admin_user_and_token(erb=self.erb, org=self.org)
        # set up an applicant user/contact
        self.app_user, self.app_contact = \
            self.generate_user_and_contact(org=self.org)
        # set up an approver user/contact
        self.approver_user, self.approver_contact, self.approver_token = \
            self.generate_erb_admin_user_and_token(erb=self.erb, org=self.org)
        # set approver role
        erb_roles = contact_models.CramsERBUserRoles.objects.get(contact=self.approver_contact)
        erb_roles.approver_erb_systems.add(self.erbs)
        # set up provisioner user/contact
        self.provisioner_user, self.provisioner_contact, self.provisioner_token = \
            self.generate_erb_admin_user_and_token(erb=self.erb, org=self.org)
        # set provisioner role
        erb_roles = contact_models.CramsERBUserRoles.objects.get(contact=self.provisioner_contact)
        erb_roles.providers.add(self.provider)

        # set up faculty admin
        self.faculty_user, self.faculty_contact = \
            self.generate_user_and_contact(org=self.org)
        mixer.blend(manager_models.FacultyManager,
                    contact=self.faculty_contact,
                    faculty=self.faculty,
                    active=True)

        # set up a project member user/contact
        self.prjmbr1_user, self.prjmbr1_contact = \
            self.generate_user_and_contact(org=self.org)
        self.prjmbr2_user, self.prjmbr2_contact = \
            self.generate_user_and_contact(org=self.org)
        self.prjmbr3_user, self.prjmbr3_contact = \
            self.generate_user_and_contact(org=self.org)

        # setup a test user - not associated with any projects
        self.test_user, self.test_contact = \
            self.generate_user_and_contact(org=self.org)
        
        # set up an allocation new/draft status
        self.prj_draft = self.generate_submission_allocation(draft=True)
        
        # set up an allocation submit status
        self.prj_submit = self.generate_submission_allocation()
        
        # set up an allocation approved status
        self.prj_approved = self.generate_approved_allocation()

        # set up an allocation declined status
        self.prj_declined = self.generate_declined_allocation()

        # set up an allocation provisioned status
        self.prj_prov = self.generate_provisioned_allocation()

        # set up an allocation extended/updated status
        self.prj_alloc_ext = self.generate_allocation_extended()

        # set up an allocation extension that has been approved status
        self.prj_alloc_ext_appr = self.generate_allocation_extended_approved()
    
    def generate_question(self, type, idx):
        type_idx = type + '_' + str(idx)
        return mixer.blend(crams_models.Question, 
                           key='key_' + type_idx, 
                           question_type='question_type_' + type_idx,
                           question='question' + type_idx)

    def generate_project_contact(self, contact, role, project):
        mixer.blend(collection_models.ProjectContact, 
                    contact=contact,
                    contact_role=role,
                    project=project)
        # TODO: need to update the migration with default status data 
        # status = mixer.blend(member_models.ProjectMemberStatus,
        #                      code='M', status='Project Member')
        # TODO: add project member module
        # mixer.blend(member_models.ProjectJoinInviteRequest,
        #             surname=contact.surname,
        #             given_name=contact.given_name,
        #             email=contact.email,
        #             project=project,
        #             status=status,
        #             contact=contact)

    def generate_project(self, updated_by, prev_project=None):
        # create a new project copying old values over from previous
        if prev_project:
            project = mixer.blend(collection_models.Project, 
                            department=prev_project.department,
                            title=prev_project.title,
                            description=prev_project.description,
                            notes=prev_project.notes,
                            created_by=updated_by,
                            updated_by=updated_by,
                            current_project=None,
                            crams_id=prev_project.crams_id)
            # set the current_project parent to new project
            prev_project.current_project = project
            prev_project.save()
        else:
            project = mixer.blend(collection_models.Project, 
                                department=self.dept,
                                title=get_random_string(12),
                                description=get_random_string(25),
                                notes=get_random_string(100),
                                created_by=updated_by,
                                updated_by=updated_by,
                                current_project=None,
                                crams_id=get_random_string(25))

        # grant
        mixer.blend(collection_models.Grant,
                    project=project,
                    grant_type=self.grant_type,
                    funding_body_and_scheme=get_random_string(12),
                    grant_id=get_random_string(12),
                    start_year=2000,
                    duration=5,
                    total_funding=10000)
        # domain/forcode
        mixer.blend(collection_models.Domain,
                    percentage=50, 
                    project=project,
                    for_code=self.forcode1)
        mixer.blend(collection_models.Domain,
                    percentage=50, 
                    project=project,
                    for_code=self.forcode2)

        # publication
        mixer.blend(collection_models.Publication,
                    reference=get_random_string(50),
                    project=project)

        return project

    def generate_request(self, project, status, updated_by, prev_request=None):
        if prev_request:
            request = mixer.blend(allocation_models.Request,
                                project=project,
                                current_request=None,
                                request_status=status,
                                data_sensitive=prev_request.data_sensitive,
                                funding_scheme=prev_request.funding_scheme,
                                e_research_system=prev_request.e_research_system,
                                national_percent=prev_request.national_percent,
                                transaction_id=prev_request.transaction_id,
                                allocation_home=prev_request.allocation_home,
                                start_date=prev_request.start_date,
                                end_date=prev_request.end_date,
                                approval_notes='',
                                sent_email=False,
                                allocation_extension_count=0,
                                sent_ext_support_email=False,
                                created_by=updated_by,
                                updated_by=updated_by)
            # set the prev_request parent to new request
            prev_request.current_request = request
            prev_request.save()
        else:
            request = mixer.blend(allocation_models.Request,
                                project=project,
                                current_request=None,
                                request_status=status,
                                data_sensitive=False,
                                funding_scheme=self.funding_scheme,
                                e_research_system=self.erbs,
                                national_percent=100,
                                transaction_id=get_random_string(25),
                                allocation_home=None,
                                start_date=datetime.now(),
                                end_date=(datetime.now() + relativedelta(years=1)),
                                approval_notes='',
                                sent_email=False,
                                allocation_extension_count=0,
                                sent_ext_support_email=False,
                                created_by=updated_by,
                                updated_by=updated_by)
        return request

    def generate_sp_request(self, request, current_quota, 
                            requested_quota_change, approved_quota_change, provision_id=None, prov_det=None):
        sp_request = mixer.blend(product_models.StorageRequest,
                                 current_quota=current_quota,
                                 requested_quota_change=requested_quota_change,
                                 approved_quota_change=approved_quota_change,
                                 storage_product=self.storage_prod,
                                 request=request,
                                 provision_id=provision_id,
                                 provision_details=prov_det)
        return sp_request

    def generate_cp_request(self, request, instances, approved_instances, 
                            cores, approved_cores, core_hours, approved_core_hours):
        cp_request = mixer.blend(product_models.ComputeRequest,
                                 instances=instances,
                                 approved_instances=approved_instances,
                                 cores=cores,
                                 approved_cores=approved_cores,
                                 core_hours=core_hours,
                                 approved_core_hours=approved_core_hours,
                                 compute_product=self.compute_prod,
                                 request=request,
                                 provision_details=None)
        return cp_request

    def generate_copy_allocation(self, prev_project, new_status, updated_by):
        project = self.generate_project(updated_by, prev_project=prev_project)
        prev_request = prev_project.requests.all().first()
        request = self.generate_request(project, new_status, updated_by, prev_request=prev_request)
        # storage and compute request will need to have the quotas adjusted
        # get all the project contacts from prev_project
        prev_prj_contacts = collection_models.ProjectContact.objects.filter(project=prev_project)
        for prj_cont in prev_prj_contacts:
            self.generate_project_contact(
                prj_cont.contact, prj_cont.contact_role, project)

        return project

    def generate_question_responses(self, prj, req, cp_req, sp_req):
        for question in self.project_questions:
            mixer.blend(collection_models.ProjectQuestionResponse,
                        question_response=question.question+'_response',
                        project=prj,
                        question=question)

        for question in self.request_questions:
            mixer.blend(allocation_models.RequestQuestionResponse,
                        question_response=question.question+'_response',
                        request=req,
                        question=question)

        # for question in self.sp_request_questions:
        #     mixer.blend(product_models.StorageRequestQuestionResponse,
        #                 question_response=question.question+'_response',
        #                 storage_allocation=sp_req,
        #                 question=question)

        # for question in self.cp_request_questions:
        #     mixer.blend(product_models.ComputeRequestQuestionResponse,
        #                 question_response=question.question+'_response',
        #                 compute_request=cp_req,
        #                 question=question)


    def generate_submission_allocation(self, draft=False):
        # get submission status
        status = db.REQUEST_STATUS_SUBMITTED
        if draft:
            status = db.REQUEST_STATUS_NEW
        req_status = allocation_models.RequestStatus.objects.get(
            code=status)
        
        # create a project
        project = self.generate_project(self.app_user)
        project.title = 'Test submit check'
        project.save()
        # create a request
        request = self.generate_request(project, req_status, self.app_user)
        # create a storage request
        storage_req = self.generate_sp_request(request, 0, 100, 0)
        # create a compute request
        # compute_req = self.generate_cp_request(request, 4, 0, 8, 0, 1250, 0)
        compute_req = None

        # generate the questions
        self.generate_question_responses(project, request, compute_req, storage_req)

        # set up the project contacts
        self.generate_project_contact(
            self.app_contact, self.app_role, project)
        self.generate_project_contact(
            self.prjmbr1_contact, self.prjmbr_role, project)
        self.generate_project_contact(
            self.prjmbr2_contact, self.prjmbr_role, project)
        self.generate_project_contact(
            self.prjmbr3_contact, self.prjmbr_role, project)

        return project
    
    def generate_approved_allocation(self):
        # get approved status
        req_status = allocation_models.RequestStatus.objects.get(
            code=db.REQUEST_STATUS_APPROVED)

        # generate submission allocation
        sub_project = self.generate_submission_allocation()

        # generate approved allocation
        app_project = self.generate_copy_allocation(sub_project, req_status, self.admin_user)

        app_req = app_project.requests.all().first()
        
        # create provision_details
        prov_det = mixer.blend(crams_models.ProvisionDetails,
                               status='S',
                               message='provision notes',
                               parent_provision_details=None,
                               created_by=self.admin_user,
                               updated_by=self.admin_user)
        # create and set the approved quotas
        # app_cp_req = self.generate_cp_request(app_req, 4, 4, 8, 8, 1250, 1250)
        app_cp_req = None
        app_sp_req = self.generate_sp_request(app_req, 0, 100, 100, prov_det=prov_det)

        # generate the questions
        self.generate_question_responses(app_project, app_req, app_cp_req, app_sp_req)

        return app_project
    
    def generate_declined_allocation(self):
        # get declined status
        req_status = allocation_models.RequestStatus.objects.get(
            code=db.REQUEST_STATUS_DECLINED)

        # generate submission allocation
        sub_project = self.generate_submission_allocation()

        # generate declined allocation
        decl_project = self.generate_copy_allocation(sub_project, req_status, self.admin_user)

        decl_req = decl_project.requests.all().first()
        # create and set the approved quotas
        # decl_cp_req = self.generate_cp_request(decl_req, 4, 0, 8, 0, 1250, 0)
        decl_cp_req = None
        decl_sp_req = self.generate_sp_request(decl_req, 0, 100, 0)

        # generate the questions
        self.generate_question_responses(sub_project, decl_req, decl_cp_req, decl_sp_req)

        return decl_project
    
    def generate_provisioned_allocation(self):
        # generate an approved allocation
        app_project = self.generate_approved_allocation()

        # get the submission project and request
        sub_project = collection_models.Project.objects.get(current_project=app_project)
        app_req = app_project.requests.all().first()
        sub_request = allocation_models.Request.objects.get(current_request=app_req)

        # get provisioned status
        req_status = allocation_models.RequestStatus.objects.get(
            code=db.REQUEST_STATUS_PROVISIONED)

        # generate provisioned allocation
        prov_project = self.generate_copy_allocation(app_project, req_status, self.admin_user)

        # update the submit current_project and current_request
        sub_project.current_project = prov_project
        sub_project.save()
        prov_req = prov_project.requests.all().first()
        sub_request.current_request = prov_req
        sub_request.save()

        # create provision_details
        prov_det = mixer.blend(crams_models.ProvisionDetails,
                               status='P',
                               message='provision notes',
                               parent_provision_details=None,
                               created_by=self.admin_user,
                               updated_by=self.admin_user)

        # create and set the approved quotas
        # prov_cp_req = self.generate_cp_request(prov_req, 4, 4, 8, 8, 1250, 1250)
        prov_cp_req = None
        prov_sp_req = self.generate_sp_request(prov_req, 100, 0, 0)

        # create storage provision id
        prov_sp_req.provision_id = mixer.blend(
            storage_models.StorageProductProvisionId,
            provision_id=get_random_string(15),
            storage_product=self.storage_prod)
        prov_sp_req.save()

        # generate the questions
        self.generate_question_responses(prov_project, prov_req, prov_cp_req, prov_sp_req)
        
        return prov_project

    def generate_allocation_extended(self):
        prj_prov = self.generate_provisioned_allocation()
        req_prov = prj_prov.requests.all().first()
        
        req_status = allocation_models.RequestStatus.objects.get(
            code=db.REQUEST_STATUS_UPDATE_OR_EXTEND)
        
        # create a new extension
        # generate provisioned allocation
        prj_alloc_ext = self.generate_copy_allocation(prj_prov, req_status, self.admin_user)
        req_alloc_ext = prj_alloc_ext.requests.all().first()

        # get the submission/approve project and request
        req_appr = allocation_models.Request.objects.filter(current_request=req_prov, request_status__code='A').first()
        prj_appr = req_appr.project
        req_sub = allocation_models.Request.objects.filter(current_request=req_prov, request_status__code='E').first()
        prj_sub = req_sub.project

        # update the current_project and current_request
        prj_prov.current_project = prj_alloc_ext
        prj_prov.save()
        req_prov.current_request = req_alloc_ext
        req_prov.save()
        prj_appr.current_project = prj_alloc_ext
        prj_appr.save()
        req_appr.current_request = req_alloc_ext
        req_appr.save()
        prj_sub.current_project = prj_alloc_ext
        prj_sub.save()
        req_sub.current_request = req_alloc_ext
        req_sub.save()

        # create and set the approved quotas
        # prov_cp_req = self.generate_cp_request(req_prov, 4, 4, 8, 8, 1250, 1250)
        cp_req_alloc_ext = None
        # current quota is 100gb, extending an additional 100 gb and 0 approved
        sp_req_prov = req_prov.storage_requests.all().first()
        sp_req_alloc_ext = self.generate_sp_request(
            req_alloc_ext, 100, 100, 0, 
            provision_id=sp_req_prov.provision_id, 
            prov_det=sp_req_prov.provision_details)

        # generate the questions
        self.generate_question_responses(prj_alloc_ext, req_alloc_ext, cp_req_alloc_ext, sp_req_alloc_ext)
        
        return prj_alloc_ext
    
    def generate_allocation_extended_approved(self):
        prj_alloc_ext = self.generate_allocation_extended()
        req_alloc_ext = prj_alloc_ext.requests.all().first()
        
        req_status = allocation_models.RequestStatus.objects.get(
            code=db.REQUEST_STATUS_APPROVED)
        
        # create a new extension approved
        prj_alloc_ext_appr = self.generate_copy_allocation(prj_alloc_ext, req_status, self.admin_user)
        req_alloc_ext_appr = prj_alloc_ext_appr.requests.all().first()

        # get the submission/approve/prov project and request
        req_prov = allocation_models.Request.objects.filter(current_request=req_alloc_ext, request_status__code='P').first()
        prj_prov = req_prov.project
        req_appr = allocation_models.Request.objects.filter(current_request=req_alloc_ext, request_status__code='A').first()
        prj_appr = req_appr.project
        req_sub = allocation_models.Request.objects.filter(current_request=req_alloc_ext, request_status__code='E').first()
        prj_sub = req_sub.project

        # update the current_project and current_request
        prj_alloc_ext.current_project = prj_alloc_ext_appr
        prj_alloc_ext.save()
        req_alloc_ext.current_request = req_alloc_ext_appr
        req_alloc_ext.save()
        prj_prov.current_project = prj_alloc_ext_appr
        prj_prov.save()
        req_prov.current_request = req_alloc_ext_appr
        req_prov.save()
        prj_appr.current_project = prj_alloc_ext_appr
        prj_appr.save()
        req_appr.current_request = req_alloc_ext_appr
        req_appr.save()
        prj_sub.current_project = prj_alloc_ext_appr
        prj_sub.save()
        req_sub.current_request = req_alloc_ext_appr
        req_sub.save()

        # create and set the approved quotas
        # prov_cp_req = self.generate_cp_request(req_prov, 4, 4, 8, 8, 1250, 1250)
        cp_req_alloc_ext_appr = None
        # current quota is 100gb, extending an additional 100 gb and 100 approved
        sp_req_alloc_ext = req_alloc_ext.storage_requests.all().first()
        sp_req_alloc_ext_appr = self.generate_sp_request(
            req_alloc_ext_appr, 100, 100, 100, 
            provision_id=sp_req_alloc_ext.provision_id, 
            prov_det=sp_req_alloc_ext.provision_details)

        # generate the questions
        self.generate_question_responses(prj_alloc_ext_appr, req_alloc_ext_appr, cp_req_alloc_ext_appr, sp_req_alloc_ext_appr)
        
        return prj_alloc_ext_appr

    def get_submit_json_payload(self):
        status = allocation_models.RequestStatus.objects.get(
            code=db.REQUEST_STATUS_SUBMITTED)
        return {
                "title": "Collection Title",
                "description": "The collection description.",
                "project_question_responses": [],
                "institutions": [],
                "publications": [],
                "grants": [{
                    "grant_type": {
                        "id": self.grant_type.id
                    },
                    "funding_body_and_scheme": "Funding Body and Scheme",
                    "grant_id": "grant-id-1234",
                    "start_year": 2021,
                    "duration": 24,
                    "total_funding": 100000
                }],
                "project_ids": [],
                "project_contacts": [{
                    "contact": {
                        "id": self.prjmbr1_contact.id,
                        "title": self.prjmbr1_contact.title,
                        "given_name": self.prjmbr1_contact.given_name,
                        "surname": self.prjmbr1_contact.surname,
                        "email": self.prjmbr1_contact.email,
                        "phone": self.prjmbr1_contact.phone,
                        "organisation": None,
                        "orcid": None,
                        "scopusid": None,
                        "contact_details": [{
                            "type": "Business",
                            "phone": None,
                            "email": self.prjmbr1_contact.email
                        }],
                        "latest_contact": None,
                        "contact_ids": [],
                        "last_login": []
                    },
                    "contact_role": self.prjmbr_role.name
                }, {
                    "contact": {
                        "id": self.prjmbr2_contact.id,
                        "title": self.prjmbr2_contact.title,
                        "given_name": self.prjmbr2_contact.given_name,
                        "surname": self.prjmbr2_contact.surname,
                        "email": self.prjmbr2_contact.email,
                        "phone": self.prjmbr2_contact.phone,
                        "organisation": None,
                        "orcid": None,
                        "scopusid": None,
                        "contact_details": [{
                            "type": "Business",
                            "phone": None,
                            "email": self.prjmbr2_contact.email
                        }],
                        "latest_contact": None,
                        "contact_ids": [],
                        "last_login": []
                    },
                    "contact_role": self.prjmbr_role.name
                }],
                "domains": [{
                    "percentage": 50,
                    "for_code": {
                        "id": self.forcode1.id
                    },
                }, {
                    "percentage": 50,
                    "for_code": {
                        "id": self.forcode2.id
                    },
                }],
                "requests": [{
                    "compute_requests": [],
                    "storage_requests": [{
                        "current_quota": 0,
                        "requested_quota_change": 10,
                        "requested_quota_total": 10,
                        "approved_quota_change": 0,
                        "approved_quota_total": 0,
                        "storage_product": {
                            "id": self.storage_prod.id,
                            "name": self.storage_prod.name
                        },
                        "storage_question_responses": []
                    }],
                    "request_question_responses": [{
                        "question_response": self.request_questions[0].question+'_response',
                        "question": {
                            "key": self.request_questions[0].key
                        }
                    }, {
                        "question_response": self.request_questions[1].question+'_response',
                        "question": {
                            "key": self.request_questions[1].key
                        }
                    }, {
                        "question_response": self.request_questions[2].question+'_response',
                        "question": {
                            "key": self.request_questions[2].key
                        } 
                    }],
                    "request_status": {
                        "id": status.id,
                        "code": status.code,
                        "status": status.status
                    },
                    "funding_scheme": {
                        "id": self.funding_scheme.id,
                        "funding_scheme": self.funding_scheme.funding_scheme
                    },
                    "e_research_system": {
                        "id": self.erbs.id,
                        "name": self.erbs.name,
                        "e_research_body": self.erbs.e_research_body.name
                    },
                    "start_date": "2021-03-19",
                    "end_date": "9999-12-31",
                    "approval_notes": "",
                    "sent_email": False,
                    "historic": False,
                    "data_sensitive": False
                }],
                "department": {
                    "department": self.dept.name,
                    "faculty": self.faculty.name,
                    "organisation": self.org.name,
                    "department_id": self.dept.id
                }
            }

    def get_empty_draft_json_payload(self):
        status = allocation_models.RequestStatus.objects.get(
            code=db.REQUEST_STATUS_NEW)
        return {
            "title": "Test Draft",
            "description": "Description Draft",
            "project_question_responses": [],
            "institutions": [],
            "publications": [],
            "grants": [],
            "project_ids": [],
            "project_contacts": [],
            "domains": [],
            "requests": [{
                "compute_requests": [],
                "storage_requests": [],
                "request_question_responses": [],
                "request_status": {
                    "id": status.id,
                    "code": status.code,
                    "status": status.status
                },
                "funding_scheme": {
                    "id": self.funding_scheme.id,
                    "funding_scheme": self.funding_scheme.funding_scheme
                },
                "e_research_system": {
                    "id": self.erbs.id,
                    "name": self.erbs.name,
                    "e_research_body": self.erbs.e_research_body.name
                },
                "start_date": "2021-03-22",
                "end_date": "9999-12-31",
                "approval_notes": "",
                "sent_email": False,
                "historic": False,
                "data_sensitive": None
            }],
            "department": None
        }

    def get_empty_approve_json_payload(self):
        return {
                "compute_requests": [],
                "storage_requests": [
                    {
                        "id": None,
                        "current_quota": 0,
                        "provision_id": None,
                        "storage_product": {
                            "id": None,
                            "storage_type": {
                                "id": None,
                                "storage_type": None
                            },
                            "zone": None,
                            "name": None,
                            "parent_storage_product": None
                        },
                        "requested_quota_change": 0,
                        "requested_quota_total": 0,
                        "approved_quota_change": 0,
                        "approved_quota_total": 0,
                        "storage_question_responses": [],
                        "provision_details": {
                            "status": None,
                            "message": ""
                        }
                    }
                ],
                "funding_scheme": {
                    "id": None,
                    "funding_scheme": None
                },
                "national_percent": 100,
                "approval_notes": "",
                "sent_email": False
            }