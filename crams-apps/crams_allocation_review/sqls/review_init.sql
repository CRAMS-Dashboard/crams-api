
-- Insert racmon erb ReviewConfig
INSERT INTO review_reviewconfig (email_notification_template_file, enable, e_research_body_id)
VALUES ('notification/racmon/review.html', 1, (SELECT id from crams_eresearchbody where name = 'RaCMon'));

-- Insert ReviewContactRoles for ReviewConfig erb
INSERT INTO review_reviewcontactrole (contact_role_id, review_config_id)
VALUES ((SELECT id from crams_contactrole
    where name = 'Data Custodian' and e_research_body_id = (SELECT id from crams_eresearchbody where `name` = 'RaCMon')),
    (SELECT id from review_reviewconfig WHERE email_notification_template_file = 'notification/racmon/review.html'));

INSERT INTO review_reviewcontactrole (contact_role_id, review_config_id)
VALUES ((SELECT id from crams_contactrole
    where name = 'Technical Contact' and e_research_body_id = (SELECT id from crams_eresearchbody where `name` = 'RaCMon')),
    (SELECT id from review_reviewconfig WHERE email_notification_template_file = 'notification/racmon/review.html'));

INSERT INTO review_reviewcontactrole (contact_role_id, review_config_id)
VALUES ((SELECT id from crams_contactrole where name = 'E_RESEARCH_BODY Admin'),
    (SELECT id from review_reviewconfig WHERE email_notification_template_file = 'notification/racmon/review.html'));
