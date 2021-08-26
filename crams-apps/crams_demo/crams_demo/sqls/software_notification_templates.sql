-- Get HPC ERB
set @erb_id = (SELECT id from crams_eresearchbody where `name` = 'CRAMS-ERB');

-- Get Contact Roles
set @applicant_id = (SELECT id from crams_contact_contactrole where `name` = 'Applicant');
set @erb_admin_id = (SELECT id from crams_contact_contactrole where `name` = 'E_RESEARCH_BODY Admin');

-- Notification for Software License Submit/Request
set @software_license_status_id = (SELECT id from crams_softwarelicensestatus where code = 'R');
INSERT INTO `crams_allocation_notificationtemplate`(template_file_path, alert_funding_body, contact_license_status_id, e_research_body_id) VALUES ('notification/software-license-request.html', FALSE, @software_license_status_id, @erb_id);
set @not_temp_id = (SELECT LAST_INSERT_ID());
INSERT INTO `crams_allocation_notificationcontactrole`(contact_role_id, notification_id) VALUES (@erb_admin_id, @not_temp_id);

-- Notification for Software License Approve
set @software_license_status_id = (SELECT id from crams_softwarelicensestatus where code = 'A');
INSERT INTO `crams_allocation_notificationtemplate`(template_file_path, alert_funding_body, contact_license_status_id, e_research_body_id) VALUES ('notification/software-license-approve.html', FALSE, @software_license_status_id, @erb_id);
set @not_temp_id = (SELECT LAST_INSERT_ID());
INSERT INTO `crams_allocation_notificationcontactrole`(contact_role_id, notification_id) VALUES (@applicant_id, @not_temp_id);

-- Notification for Software License Decline
set @software_license_status_id = (SELECT id from crams_softwarelicensestatus where code = 'D');
INSERT INTO `crams_allocation_notificationtemplate`(template_file_path, alert_funding_body, contact_license_status_id, e_research_body_id) VALUES ('notification/software-license-decline.html', FALSE, @software_license_status_id, @erb_id);
set @not_temp_id = (SELECT LAST_INSERT_ID());
INSERT INTO `crams_allocation_notificationcontactrole`(contact_role_id, notification_id) VALUES (@applicant_id, @not_temp_id);
