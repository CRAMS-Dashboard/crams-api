-- Membership approval
INSERT INTO `crams_allocation_notificationtemplate` (`template_file_path`, `alert_funding_body`, `project_member_status_id`, `e_research_system_id`)
VALUES('notification/project-member-approval.html', 0, (SELECT id FROM crams_projectmemberstatus WHERE `code` = 'M'), (SELECT id FROM crams_eresearchbodysystem WHERE `name` = 'CRAMS-ERB-SYS'));

-- Membership revoked
INSERT INTO `crams_allocation_notificationtemplate` (`template_file_path`, `alert_funding_body`, `project_member_status_id`, `e_research_system_id`)
VALUES('notification/project-member-revoked.html', 0, (SELECT id FROM crams_projectmemberstatus WHERE `code` = 'V'), (SELECT id FROM crams_eresearchbodysystem WHERE `name` = 'CRAMS-ERB-SYS'));

-- Membership contact role change
INSERT INTO `crams_allocation_notificationtemplate` (`template_file_path`, `alert_funding_body`, `project_member_status_id`, `e_research_system_id`)
VALUES('notification/project-member-user-role-changed.html', 0, (SELECT id FROM crams_projectmemberstatus WHERE `code` = 'U'), (SELECT id FROM crams_eresearchbodysystem WHERE `name` = 'CRAMS-ERB-SYS'));

