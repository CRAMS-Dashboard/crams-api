START TRANSACTION ;
-- Get racmon e_research_body_id
set @racmon_erb_id = (SELECT id from crams_eresearchbody where `name` = 'RaCMon');

-- Insert racmon erb ReviewConfig
INSERT INTO review_reviewconfig (email_notification_template_file, enable, e_research_body_id)
VALUES ('notification/racmon/review.html', TRUE, @racmon_erb_id);

-- Get the review_conf_id
set @review_config_id = (select LAST_INSERT_ID());

-- Get Data Custodian ContactRole
set @dc_role = (SELECT id from crams_contactrole
    where `name` = 'Data Custodian' and e_research_body_id = @racmon_erb_id);

-- Get Tech Contact
set @tc_role = (SELECT id from crams_contactrole
    where `name` = 'Technical Contact' and e_research_body_id = @racmon_erb_id);

-- Get ERB Admin ContactRole
set @admin_role = (SELECT id from crams_contactrole
    where `name` = 'E_RESEARCH_BODY Admin');

-- Insert ReviewContactRoles for ReviewConfig erb
INSERT INTO review_reviewcontactrole (contact_role_id, review_config_id)
VALUES (@dc_role, @review_config_id);

INSERT INTO review_reviewcontactrole (contact_role_id, review_config_id)
VALUES (@tc_role, @review_config_id);

INSERT INTO review_reviewcontactrole (contact_role_id, review_config_id)
VALUES (@admin_role, @review_config_id);

COMMIT;