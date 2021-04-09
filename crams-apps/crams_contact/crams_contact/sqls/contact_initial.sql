-- noinspection SqlDialectInspectionForFile
-- noinspection SqlNoDataSourceInspectionForFile

INSERT INTO crams_contact_contactrole (`name`, e_research_body_id, project_leader, read_only, support_notification) VALUES ('Applicant', (SELECT id from crams_eresearchbody where `name` = 'CRAMS-ERB'), FALSE, FALSE, FALSE);
INSERT INTO crams_contact_contactrole (`name`, e_research_body_id, project_leader, read_only, support_notification) VALUES ('Technical Contact', (SELECT id from crams_eresearchbody where `name` = 'CRAMS-ERB'), FALSE, FALSE, FALSE);
INSERT INTO crams_contact_contactrole (`name`, e_research_body_id, project_leader, read_only, support_notification) VALUES ('Data Custodian', (SELECT id from crams_eresearchbody where `name` = 'CRAMS-ERB'), TRUE, FALSE, FALSE);
INSERT INTO crams_contact_contactrole (`name`, e_research_body_id, project_leader, read_only, support_notification) VALUES ('Data Provider', (SELECT id from crams_eresearchbody where `name` = 'CRAMS-ERB'), FALSE, FALSE, FALSE);

INSERT INTO crams_contact_contactrole (`name`, project_leader, read_only, support_notification) VALUES ('E_RESEARCH_BODY Admin', false, false, false);
INSERT INTO crams_contact_contactrole (`name`, project_leader, read_only, support_notification) VALUES ('E_RESEARCH_BODY_SYSTEM Admin', false, false, false);
INSERT INTO crams_contact_contactrole (`name`, project_leader, read_only, support_notification) VALUES ('E_RESEARCH_SYSTEM_DELEGATE', false, false, false);
INSERT INTO crams_contact_contactrole (`name`, project_leader, read_only, support_notification) VALUES ('E_RESEARCH_BODY_SYSTEM_Approver', false, false, false);
INSERT INTO crams_contact_contactrole (`name`, project_leader, read_only, support_notification) VALUES ('E_RESEARCH_BODY_SYSTEM_Provisioner', false, false, false);

