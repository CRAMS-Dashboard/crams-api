INSERT INTO `crams_allocation_notificationtemplate` (`template_file_path`, `request_status_id`, `alert_funding_body`, `e_research_system_id`, `system_key_id`)
VALUES('notification/submit.html', (SELECT id FROM crams_allocation_requeststatus WHERE `code` = 'E'), 0, (SELECT id FROM crams_eresearchbodysystem WHERE `name` = 'CRAMS-ERB-SYS'), (SELECT id FROM crams_eresearchbodyidkey WHERE `key` = 'CRAMS'));

INSERT INTO `crams_allocation_notificationtemplate` (`template_file_path`, `request_status_id`, `alert_funding_body`, `e_research_system_id`, `system_key_id`)
VALUES('notification/freshdesk_submit.html', (SELECT id FROM crams_allocation_requeststatus WHERE `code` = 'E'), 0, (SELECT id FROM crams_eresearchbodysystem WHERE `name` = 'CRAMS-ERB-SYS'), (SELECT id FROM crams_eresearchbodyidkey WHERE `key` = 'CRAMS'));
