-- R@CMon Questions
INSERT INTO crams_question (`key`, question_type, question) VALUES ('racm_authorization', 'racmon-general-request', 'Please confirm that you have the authority to store this collection on [Your Organisation] infrastructure.');
INSERT INTO crams_question (`key`, question_type, question) VALUES ('racm_data_migration_src', 'racmon-general-request', 'Where is the collection currently stored?');
INSERT INTO crams_question (`key`, question_type, question) VALUES ('racm_data_migration_assistance', 'racmon-general-request', 'Do you require assistance to migrate your data?');
INSERT INTO crams_question (`key`, question_type, question) VALUES ('racm_current_access_method', 'racmon-general-request', 'How do you or your users currently access your collection?');
INSERT INTO crams_question (`key`, question_type, question) VALUES ('racm_preferred_access_method', 'racmon-general-request', 'What is your preferred access method?');
INSERT INTO crams_question (`key`, question_type, question) VALUES ('racm_data_format', 'racmon-usage information-request', 'Identify the format(s) of the data to be stored at [Your Organisation]');
INSERT INTO crams_question (`key`, question_type, question) VALUES ('racm_only_copy', 'racmon-usage information-request', 'Will [Your Organisation] be hosting the only copy of the collection?');
INSERT INTO crams_question (`key`, question_type, question) VALUES ('racm_can_be_regenerated', 'racmon-usage information-request', 'If yes, how easily can the data be regenerated? Delete the options that do not apply.');
INSERT INTO crams_question (`key`, question_type, question) VALUES ('racm_loss_impact', 'racmon-usage information-request', 'What would be the impact and/or cost incurred if data is lost?');
INSERT INTO crams_question (`key`, question_type, question) VALUES ('racm_current_size', 'racmon-usage information-request', 'Current size of data ');
INSERT INTO crams_question (`key`, question_type, question) VALUES ('racm_data_retention_period', 'racmon-usage Data retention period information-request', 'Data Retention Period (Year)');
INSERT INTO crams_question (`key`, question_type, question) VALUES ('racm_electronic_inf_class', 'Electronic information classification  information-request', 'Electronic Information Classification');

-- R@CMon Privacy
INSERT INTO crams_question (`key`, question_type, question) VALUES ('racm_privacy_q1', 'privacy', 'Publish the information on this dashboard for you to view details about your collection');
INSERT INTO crams_question (`key`, question_type, question) VALUES ('racm_privacy_q2', 'privacy', 'Contacting you from time to time to improve our service and/or let you know about any service interruptions, changes or updates');
INSERT INTO crams_question (`key`, question_type, question) VALUES ('racm_privacy_q3', 'privacy', 'Creating metadata records which may be sent to the your organisation to enable research discovery by public users through the RDA portal (www.researchdata.ands.org.au)');
INSERT INTO crams_question (`key`, question_type, question) VALUES ('racm_privacy_q4', 'privacy', 'Adding your collection name and list you as a data custodian to the [Your Organisation] website.');