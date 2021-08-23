-- contact role ids
set @applicant_id = (SELECT id from crams_contact_contactrole where `name` = 'Applicant' and e_research_body_id is NULL);
set @technical_contact_id = (SELECT id from crams_contact_contactrole where name = 'Technical Contact' and e_research_body_id = (SELECT id from crams_eresearchbody where `name` = 'CRAMS-ERB'));
set @data_custodian_id = (SELECT id from crams_contact_contactrole where name = 'Data Custodian' and e_research_body_id = (SELECT id from crams_eresearchbody where `name` = 'CRAMS-ERB'));
set @erb_admin_id = (SELECT id from crams_contact_contactrole where name = 'E_RESEARCH_BODY Admin');

-- Membership approval
INSERT INTO `crams_allocation_notificationtemplate` (`template_file_path`, `alert_funding_body`, `project_member_status_id`, `e_research_system_id`)
VALUES('notification/project-member-approval.html', 0, (SELECT id FROM crams_projectmemberstatus WHERE `code` = 'M'), (SELECT id FROM crams_eresearchbodysystem WHERE `name` = 'CRAMS-ERB-SYS'));
set @notif_temp_id = (select LAST_INSERT_ID());
-- Notification Contact Roles
-- Applicant
INSERT INTO `crams_allocation_notificationcontactrole` (`contact_role_id`, `notification_id`) VALUES (@applicant_id, @notif_temp_id);
-- Data Custodian
INSERT INTO `crams_allocation_notificationcontactrole` (`contact_role_id`, `notification_id`) VALUES (@data_custodian_id, @notif_temp_id);
-- Technical Contact
INSERT INTO `crams_allocation_notificationcontactrole` (`contact_role_id`, `notification_id`) VALUES (@technical_contact_id, @notif_temp_id);
-- ERB Admin
INSERT INTO `crams_allocation_notificationcontactrole` (`contact_role_id`, `notification_id`) VALUES (@erb_admin_id, @notif_temp_id);

-- Membership revoked
INSERT INTO `crams_allocation_notificationtemplate` (`template_file_path`, `alert_funding_body`, `project_member_status_id`, `e_research_system_id`) VALUES('notification/project-member-revoked.html', 0, (SELECT id FROM crams_projectmemberstatus WHERE `code` = 'V'), (SELECT id FROM crams_eresearchbodysystem WHERE `name` = 'CRAMS-ERB-SYS'));
set @notif_temp_id = (select LAST_INSERT_ID());
-- Notification Contact Roles
-- Applicant
INSERT INTO `crams_allocation_notificationcontactrole` (`contact_role_id`, `notification_id`) VALUES (@applicant_id, @notif_temp_id);
-- Data Custodian
INSERT INTO `crams_allocation_notificationcontactrole` (`contact_role_id`, `notification_id`) VALUES (@data_custodian_id, @notif_temp_id);
-- Technical Contact
INSERT INTO `crams_allocation_notificationcontactrole` (`contact_role_id`, `notification_id`) VALUES (@technical_contact_id, @notif_temp_id);
-- ERB Admin
INSERT INTO `crams_allocation_notificationcontactrole` (`contact_role_id`, `notification_id`) VALUES (@erb_admin_id, @notif_temp_id);

-- Membership contact role change
INSERT INTO `crams_allocation_notificationtemplate` (`template_file_path`, `alert_funding_body`, `project_member_status_id`, `e_research_system_id`)
VALUES('notification/project-member-user-role-changed.html', 0, (SELECT id FROM crams_projectmemberstatus WHERE `code` = 'U'), (SELECT id FROM crams_eresearchbodysystem WHERE `name` = 'CRAMS-ERB-SYS'));
set @notif_temp_id = (select LAST_INSERT_ID());
-- Notification Contact Roles
-- Applicant
INSERT INTO `crams_allocation_notificationcontactrole` (`contact_role_id`, `notification_id`) VALUES (@applicant_id, @notif_temp_id);
-- Data Custodian
INSERT INTO `crams_allocation_notificationcontactrole` (`contact_role_id`, `notification_id`) VALUES (@data_custodian_id, @notif_temp_id);
-- Technical Contact
INSERT INTO `crams_allocation_notificationcontactrole` (`contact_role_id`, `notification_id`) VALUES (@technical_contact_id, @notif_temp_id);
-- ERB Admin
INSERT INTO `crams_allocation_notificationcontactrole` (`contact_role_id`, `notification_id`) VALUES (@erb_admin_id, @notif_temp_id);

-- Membership invite
INSERT INTO `crams_allocation_notificationtemplate` (`template_file_path`, `alert_funding_body`, `project_member_status_id`, `e_research_system_id`) VALUES('notification/project-member-invite.html', 0, (SELECT id FROM crams_projectmemberstatus WHERE `code` = 'I'), (SELECT id FROM crams_eresearchbodysystem WHERE `name` = 'CRAMS-ERB-SYS'));
set @notif_temp_id = (select LAST_INSERT_ID());
-- Notification Contact Roles
-- Applicant
INSERT INTO `crams_allocation_notificationcontactrole` (`contact_role_id`, `notification_id`) VALUES (@applicant_id, @notif_temp_id);
-- Data Custodian
INSERT INTO `crams_allocation_notificationcontactrole` (`contact_role_id`, `notification_id`) VALUES (@data_custodian_id, @notif_temp_id);
-- Technical Contact
INSERT INTO `crams_allocation_notificationcontactrole` (`contact_role_id`, `notification_id`) VALUES (@technical_contact_id, @notif_temp_id);
-- ERB Admin
INSERT INTO `crams_allocation_notificationcontactrole` (`contact_role_id`, `notification_id`) VALUES (@erb_admin_id, @notif_temp_id);


-- Membership invite cancelled
INSERT INTO `crams_allocation_notificationtemplate` (`template_file_path`, `alert_funding_body`, `project_member_status_id`, `e_research_system_id`) VALUES('notification/project-member-invite-cancelled.html', 0, (SELECT id FROM crams_projectmemberstatus WHERE `code` = 'C'), (SELECT id FROM crams_eresearchbodysystem WHERE `name` = 'CRAMS-ERB-SYS'));
set @notif_temp_id = (select LAST_INSERT_ID());
-- Notification Contact Roles
-- Applicant
INSERT INTO `crams_allocation_notificationcontactrole` (`contact_role_id`, `notification_id`) VALUES (@applicant_id, @notif_temp_id);
-- Data Custodian
INSERT INTO `crams_allocation_notificationcontactrole` (`contact_role_id`, `notification_id`) VALUES (@data_custodian_id, @notif_temp_id);
-- Technical Contact
INSERT INTO `crams_allocation_notificationcontactrole` (`contact_role_id`, `notification_id`) VALUES (@technical_contact_id, @notif_temp_id);
-- ERB Admin
INSERT INTO `crams_allocation_notificationcontactrole` (`contact_role_id`, `notification_id`) VALUES (@erb_admin_id, @notif_temp_id);

-- Membership invite decline
INSERT INTO `crams_allocation_notificationtemplate` (`template_file_path`, `alert_funding_body`, `project_member_status_id`, `e_research_system_id`) VALUES('notification/project-member-invite-decline.html', 0, (SELECT id FROM crams_projectmemberstatus WHERE `code` = 'D'), (SELECT id FROM crams_eresearchbodysystem WHERE `name` = 'CRAMS-ERB-SYS'));
set @notif_temp_id = (select LAST_INSERT_ID());
-- Notification Contact Roles
-- Applicant
INSERT INTO `crams_allocation_notificationcontactrole` (`contact_role_id`, `notification_id`) VALUES (@applicant_id, @notif_temp_id);
-- Data Custodian
INSERT INTO `crams_allocation_notificationcontactrole` (`contact_role_id`, `notification_id`) VALUES (@data_custodian_id, @notif_temp_id);
-- Technical Contact
INSERT INTO `crams_allocation_notificationcontactrole` (`contact_role_id`, `notification_id`) VALUES (@technical_contact_id, @notif_temp_id);
-- ERB Admin
INSERT INTO `crams_allocation_notificationcontactrole` (`contact_role_id`, `notification_id`) VALUES (@erb_admin_id, @notif_temp_id);

-- Membership reject
INSERT INTO `crams_allocation_notificationtemplate` (`template_file_path`, `alert_funding_body`, `project_member_status_id`, `e_research_system_id`) VALUES('notification/project-member-reject.html', 0, (SELECT id FROM crams_projectmemberstatus WHERE `code` = 'E'), (SELECT id FROM crams_eresearchbodysystem WHERE `name` = 'CRAMS-ERB-SYS'));
set @notif_temp_id = (select LAST_INSERT_ID());
-- Notification Contact Roles
-- Applicant
INSERT INTO `crams_allocation_notificationcontactrole` (`contact_role_id`, `notification_id`) VALUES (@applicant_id, @notif_temp_id);
-- Data Custodian
INSERT INTO `crams_allocation_notificationcontactrole` (`contact_role_id`, `notification_id`) VALUES (@data_custodian_id, @notif_temp_id);
-- Technical Contact
INSERT INTO `crams_allocation_notificationcontactrole` (`contact_role_id`, `notification_id`) VALUES (@technical_contact_id, @notif_temp_id);
-- ERB Admin
INSERT INTO `crams_allocation_notificationcontactrole` (`contact_role_id`, `notification_id`) VALUES (@erb_admin_id, @notif_temp_id);

-- Membership request cancelled
INSERT INTO `crams_allocation_notificationtemplate` (`template_file_path`, `alert_funding_body`, `project_member_status_id`, `e_research_system_id`) VALUES('notification/project-member-request-cancelled.html', 0, (SELECT id FROM crams_projectmemberstatus WHERE `code` = 'L'), (SELECT id FROM crams_eresearchbodysystem WHERE `name` = 'CRAMS-ERB-SYS'));
set @notif_temp_id = (select LAST_INSERT_ID());
-- Notification Contact Roles
-- Applicant
INSERT INTO `crams_allocation_notificationcontactrole` (`contact_role_id`, `notification_id`) VALUES (@applicant_id, @notif_temp_id);
-- Data Custodian
INSERT INTO `crams_allocation_notificationcontactrole` (`contact_role_id`, `notification_id`) VALUES (@data_custodian_id, @notif_temp_id);
-- Technical Contact
INSERT INTO `crams_allocation_notificationcontactrole` (`contact_role_id`, `notification_id`) VALUES (@technical_contact_id, @notif_temp_id);
-- ERB Admin
INSERT INTO `crams_allocation_notificationcontactrole` (`contact_role_id`, `notification_id`) VALUES (@erb_admin_id, @notif_temp_id);

-- Membership request user
INSERT INTO `crams_allocation_notificationtemplate` (`template_file_path`, `alert_funding_body`, `project_member_status_id`, `e_research_system_id`) VALUES('notification/project-member-request_user.html', 0, (SELECT id FROM crams_projectmemberstatus WHERE `code` = 'R'), (SELECT id FROM crams_eresearchbodysystem WHERE `name` = 'CRAMS-ERB-SYS'));
set @notif_temp_id = (select LAST_INSERT_ID());
-- Notification Contact Roles
-- Applicant
INSERT INTO `crams_allocation_notificationcontactrole` (`contact_role_id`, `notification_id`) VALUES (@applicant_id, @notif_temp_id);
-- Data Custodian
INSERT INTO `crams_allocation_notificationcontactrole` (`contact_role_id`, `notification_id`) VALUES (@data_custodian_id, @notif_temp_id);
-- Technical Contact
INSERT INTO `crams_allocation_notificationcontactrole` (`contact_role_id`, `notification_id`) VALUES (@technical_contact_id, @notif_temp_id);
-- ERB Admin
INSERT INTO `crams_allocation_notificationcontactrole` (`contact_role_id`, `notification_id`) VALUES (@erb_admin_id, @notif_temp_id);
