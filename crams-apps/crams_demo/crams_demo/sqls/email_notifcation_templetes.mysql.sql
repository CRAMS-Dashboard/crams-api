INSERT INTO `crams_allocation_notificationtemplate` (`template_file_path`, `request_status_id`, `alert_funding_body`, `funding_body_id`, `e_research_system_id`)
VALUES('notification/submit.html', (SELECT id FROM crams_allocation_requeststatus WHERE `code` = 'N'), 0, (SELECT id from crams_fundingbody where `name` = 'CRAMS'), (SELECT id FROM crams_eresearchbodysystem WHERE `name` = 'CRAMS-ERB-SYS'));

INSERT INTO `crams_allocation_notificationtemplate` (`template_file_path`, `request_status_id`, `alert_funding_body`, `funding_body_id`, `e_research_system_id`)
VALUES('notification/submit.html', (SELECT id FROM crams_allocation_requeststatus WHERE `code` = 'E'), 0, (SELECT id from crams_fundingbody where `name` = 'CRAMS'), (SELECT id FROM crams_eresearchbodysystem WHERE `name` = 'CRAMS-ERB-SYS'));

set @applicant_id = (SELECT id from crams_contact_contactrole where `name` = 'Applicant' and e_research_body_id is NULL);
set @technical_contact_id = (SELECT id from crams_contact_contactrole where name = 'Technical Contact' and e_research_body_id = (SELECT id from crams_eresearchbody where `name` = 'CRAMS-ERB'));
set @data_custodian_id = (SELECT id from crams_contact_contactrole where name = 'Data Custodian' and e_research_body_id = (SELECT id from crams_eresearchbody where `name` = 'CRAMS-ERB'));
set @approver_id = (SELECT id from crams_contact_contactrole where `name` = 'E_RESEARCH_BODY_SYSTEM_Approver');
set @provisioner_id = (SELECT id from crams_contact_contactrole where `name` = 'E_RESEARCH_BODY_SYSTEM_Provisioner');

set @erb_admin_id = (SELECT id from crams_contact_contactrole where `name` = 'E_RESEARCH_BODY Admin');

set @notification_id = (SELECT id from crams_allocation_notificationtemplate where `e_research_system_id` = (SELECT id FROM crams_eresearchbodysystem WHERE `name` = 'CRAMS-ERB-SYS') and `request_status_id` = (SELECT id FROM crams_allocation_requeststatus WHERE `code` = 'E'));

INSERT INTO crams_allocation_notificationcontactrole(contact_role_id, notification_id) values (@technical_contact_id, @notification_id);   -- Technical Contact Email notification
INSERT INTO crams_allocation_notificationcontactrole(contact_role_id, notification_id) values (@data_custodian_id, @notification_id);   -- Data Custodian Email notification
INSERT INTO crams_allocation_notificationcontactrole(contact_role_id, notification_id) values (@approver_id, @notification_id);   -- Approver Email notification
INSERT INTO crams_allocation_notificationcontactrole(contact_role_id, notification_id) values (@applicant_id, @notification_id);   -- Applicant Email notification
INSERT INTO crams_allocation_notificationcontactrole(contact_role_id, notification_id) values (@erb_admin_id, @notification_id);   -- ERB admin Email notification

INSERT INTO `crams_allocation_notificationtemplate` (`template_file_path`, `request_status_id`, `alert_funding_body`, `funding_body_id`, `e_research_system_id`)
VALUES('notification/submit.html', (SELECT id FROM crams_allocation_requeststatus WHERE `code` = 'X'), 0, (SELECT id from crams_fundingbody where `name` = 'CRAMS'), (SELECT id FROM crams_eresearchbodysystem WHERE `name` = 'CRAMS-ERB-SYS'));
set @notification_id = (SELECT id from crams_allocation_notificationtemplate where `e_research_system_id` = (SELECT id FROM crams_eresearchbodysystem WHERE `name` = 'CRAMS-ERB-SYS') and `request_status_id` = (SELECT id FROM crams_allocation_requeststatus WHERE `code` = 'X'));
INSERT INTO crams_allocation_notificationcontactrole(contact_role_id, notification_id) values (@technical_contact_id, @notification_id);   -- Technical Contact Email notification
INSERT INTO crams_allocation_notificationcontactrole(contact_role_id, notification_id) values (@data_custodian_id, @notification_id);   -- Data Custodian Email notification
INSERT INTO crams_allocation_notificationcontactrole(contact_role_id, notification_id) values (@approver_id, @notification_id);   -- Approver Email notification
INSERT INTO crams_allocation_notificationcontactrole(contact_role_id, notification_id) values (@applicant_id, @notification_id);   -- Applicant Email notification
INSERT INTO crams_allocation_notificationcontactrole(contact_role_id, notification_id) values (@erb_admin_id, @notification_id);   -- ERB admin Email notification

INSERT INTO `crams_allocation_notificationtemplate` (`template_file_path`, `request_status_id`, `alert_funding_body`, `funding_body_id`, `e_research_system_id`)
VALUES('notification/approve.html', (SELECT id FROM crams_allocation_requeststatus WHERE `code` = 'A'), 0, (SELECT id from crams_fundingbody where `name` = 'CRAMS'), (SELECT id FROM crams_eresearchbodysystem WHERE `name` = 'CRAMS-ERB-SYS'));
set @notification_id = (SELECT id from crams_allocation_notificationtemplate where `e_research_system_id` = (SELECT id FROM crams_eresearchbodysystem WHERE `name` = 'CRAMS-ERB-SYS') and `request_status_id` = (SELECT id FROM crams_allocation_requeststatus WHERE `code` = 'A'));
INSERT INTO crams_allocation_notificationcontactrole(contact_role_id, notification_id) values (@technical_contact_id, @notification_id);   -- Technical Contact Email notification
INSERT INTO crams_allocation_notificationcontactrole(contact_role_id, notification_id) values (@data_custodian_id, @notification_id);   -- Data Custodian Email notification
INSERT INTO crams_allocation_notificationcontactrole(contact_role_id, notification_id) values (@approver_id, @notification_id);   -- Approver Email notification
INSERT INTO crams_allocation_notificationcontactrole(contact_role_id, notification_id) values (@provisioner_id, @notification_id);   -- Provisioner Email notification
INSERT INTO crams_allocation_notificationcontactrole(contact_role_id, notification_id) values (@applicant_id, @notification_id);   -- Applicant Email notification
INSERT INTO crams_allocation_notificationcontactrole(contact_role_id, notification_id) values (@erb_admin_id, @notification_id);   -- ERB admin Email notification


INSERT INTO `crams_allocation_notificationtemplate` (`template_file_path`, `request_status_id`, `alert_funding_body`, `funding_body_id`, `e_research_system_id`)
VALUES('notification/reject.html', (SELECT id FROM crams_allocation_requeststatus WHERE `code` = 'R'), 0, (SELECT id from crams_fundingbody where `name` = 'CRAMS'), (SELECT id FROM crams_eresearchbodysystem WHERE `name` = 'CRAMS-ERB-SYS'));
set @notification_id = (SELECT id from crams_allocation_notificationtemplate where `e_research_system_id` = (SELECT id FROM crams_eresearchbodysystem WHERE `name` = 'CRAMS-ERB-SYS') and `request_status_id` = (SELECT id FROM crams_allocation_requeststatus WHERE `code` = 'R'));
INSERT INTO crams_allocation_notificationcontactrole(contact_role_id, notification_id) values (@technical_contact_id, @notification_id);   -- Technical Contact Email notification
INSERT INTO crams_allocation_notificationcontactrole(contact_role_id, notification_id) values (@data_custodian_id, @notification_id);   -- Data Custodian Email notification
INSERT INTO crams_allocation_notificationcontactrole(contact_role_id, notification_id) values (@approver_id, @notification_id);   -- Approver Email notification
INSERT INTO crams_allocation_notificationcontactrole(contact_role_id, notification_id) values (@applicant_id, @notification_id);   -- Applicant Email notification
INSERT INTO crams_allocation_notificationcontactrole(contact_role_id, notification_id) values (@erb_admin_id, @notification_id);   -- ERB admin Email notification

INSERT INTO `crams_allocation_notificationtemplate` (`template_file_path`, `request_status_id`, `alert_funding_body`, `funding_body_id`, `e_research_system_id`)
VALUES('notification/reject.html', (SELECT id FROM crams_allocation_requeststatus WHERE `code` = 'J'), 0, (SELECT id from crams_fundingbody where `name` = 'CRAMS'), (SELECT id FROM crams_eresearchbodysystem WHERE `name` = 'CRAMS-ERB-SYS'));
set @notification_id = (SELECT id from crams_allocation_notificationtemplate where `e_research_system_id` = (SELECT id FROM crams_eresearchbodysystem WHERE `name` = 'CRAMS-ERB-SYS') and `request_status_id` = (SELECT id FROM crams_allocation_requeststatus WHERE `code` = 'J'));
INSERT INTO crams_allocation_notificationcontactrole(contact_role_id, notification_id) values (@technical_contact_id, @notification_id);   -- Technical Contact Email notification
INSERT INTO crams_allocation_notificationcontactrole(contact_role_id, notification_id) values (@data_custodian_id, @notification_id);   -- Data Custodian Email notification
INSERT INTO crams_allocation_notificationcontactrole(contact_role_id, notification_id) values (@approver_id, @notification_id);   -- Approver Email notification
INSERT INTO crams_allocation_notificationcontactrole(contact_role_id, notification_id) values (@applicant_id, @notification_id);   -- Applicant Email notification
INSERT INTO crams_allocation_notificationcontactrole(contact_role_id, notification_id) values (@erb_admin_id, @notification_id);   -- ERB admin Email notification

INSERT INTO `crams_allocation_notificationtemplate` (`template_file_path`, `request_status_id`, `alert_funding_body`, `funding_body_id`, `e_research_system_id`)
VALUES('notification/provision.html', (SELECT id FROM crams_allocation_requeststatus WHERE `code` = 'P'), 0, (SELECT id from crams_fundingbody where `name` = 'CRAMS'), (SELECT id FROM crams_eresearchbodysystem WHERE `name` = 'CRAMS-ERB-SYS'));
set @notification_id = (SELECT id from crams_allocation_notificationtemplate where `e_research_system_id` = (SELECT id FROM crams_eresearchbodysystem WHERE `name` = 'CRAMS-ERB-SYS') and `request_status_id` = (SELECT id FROM crams_allocation_requeststatus WHERE `code` = 'P'));
INSERT INTO crams_allocation_notificationcontactrole(contact_role_id, notification_id) values (@technical_contact_id, @notification_id);   -- Technical Contact Email notification
INSERT INTO crams_allocation_notificationcontactrole(contact_role_id, notification_id) values (@data_custodian_id, @notification_id);   -- Data Custodian Email notification
INSERT INTO crams_allocation_notificationcontactrole(contact_role_id, notification_id) values (@approver_id, @notification_id);   -- Approver Email notification
INSERT INTO crams_allocation_notificationcontactrole(contact_role_id, notification_id) values (@provisioner_id, @notification_id);   -- Provisioner Email notification
INSERT INTO crams_allocation_notificationcontactrole(contact_role_id, notification_id) values (@applicant_id, @notification_id);   -- Applicant Email notification
INSERT INTO crams_allocation_notificationcontactrole(contact_role_id, notification_id) values (@erb_admin_id, @notification_id);   -- ERB admin Email notification

INSERT INTO `crams_allocation_notificationtemplate` (`template_file_path`, `request_status_id`, `alert_funding_body`, `funding_body_id`, `e_research_system_id`)
VALUES('notification/partial_provision.html', (SELECT id FROM crams_allocation_requeststatus WHERE `code` = '_PP'), 0, (SELECT id from crams_fundingbody where `name` = 'CRAMS'), (SELECT id FROM crams_eresearchbodysystem WHERE `name` = 'CRAMS-ERB-SYS'));
set @notification_id = (SELECT id from crams_allocation_notificationtemplate where `e_research_system_id` = (SELECT id FROM crams_eresearchbodysystem WHERE `name` = 'CRAMS-ERB-SYS') and `request_status_id` = (SELECT id FROM crams_allocation_requeststatus WHERE `code` = '_PP'));
INSERT INTO crams_allocation_notificationcontactrole(contact_role_id, notification_id) values (@technical_contact_id, @notification_id);   -- Technical Contact Email notification
INSERT INTO crams_allocation_notificationcontactrole(contact_role_id, notification_id) values (@data_custodian_id, @notification_id);   -- Data Custodian Email notification
INSERT INTO crams_allocation_notificationcontactrole(contact_role_id, notification_id) values (@approver_id, @notification_id);   -- Approver Email notification
INSERT INTO crams_allocation_notificationcontactrole(contact_role_id, notification_id) values (@applicant_id, @notification_id);   -- Applicant Email notification
INSERT INTO crams_allocation_notificationcontactrole(contact_role_id, notification_id) values (@erb_admin_id, @notification_id);   -- ERB admin Email notification

INSERT INTO `crams_allocation_notificationtemplate` (`template_file_path`, `request_status_id`, `alert_funding_body`, `e_research_system_id`, `system_key_id`)
VALUES('notification/freshdesk_submit.html', (SELECT id FROM crams_allocation_requeststatus WHERE `code` = 'E'), 0, (SELECT id FROM crams_eresearchbodysystem WHERE `name` = 'CRAMS-ERB-SYS'), (SELECT id FROM crams_eresearchbodyidkey WHERE `key` = 'CRAMS'));

INSERT INTO `crams_allocation_notificationtemplate` (`template_file_path`, `request_status_id`, `alert_funding_body`, `e_research_system_id`, `system_key_id`)
VALUES('notification/freshdesk_extend.html', (SELECT id FROM crams_allocation_requeststatus WHERE `code` = 'X'), 0, (SELECT id FROM crams_eresearchbodysystem WHERE `name` = 'CRAMS-ERB-SYS'), (SELECT id FROM crams_eresearchbodyidkey WHERE `key` = 'CRAMS'));

-- ADMIN ALERT system key
INSERT INTO `crams_eresearchbodyidkey` (`key`, `e_research_body_id`, `description`, `type`)
VALUES ('ADMIN_ALERT_EMAIL', (SELECT id from crams_eresearchbody where `name` = 'CRAMS-ERB'), NULL, 'I');

INSERT INTO `crams_allocation_notificationtemplate` (`template_file_path`, `alert_funding_body`, `e_research_body_id`, `system_key_id`)
VALUES ('notification/admin_application_updated.html', 0, (SELECT id from crams_eresearchbody where `name` = 'CRAMS-ERB'), ((SELECT id FROM crams_eresearchbodyidkey WHERE `key` = 'ADMIN_ALERT_EMAIL' and `e_research_body_id` = (SELECT id from crams_eresearchbody where `name` = 'CRAMS-ERB'))));
set @notif_temp_id = (select LAST_INSERT_ID());
INSERT INTO `crams_allocation_notificationcontactrole` (`contact_role_id`, `notification_id`) VALUES ((SELECT id from crams_contact_contactrole where `name` = 'E_RESEARCH_BODY Admin'), @notif_temp_id);
INSERT INTO `crams_allocation_notificationcontactrole` (`contact_role_id`, `notification_id`) VALUES((SELECT id from crams_contact_contactrole where `name` = 'E_RESEARCH_BODY_SYSTEM Admin'), @notif_temp_id);

