INSERT INTO crams_duration (id, duration, duration_label) VALUES (1, 1, '1-month');
INSERT INTO crams_duration (id, duration, duration_label) VALUES (2, 3, '3-months');
INSERT INTO crams_duration (id, duration, duration_label) VALUES (3, 6, '6-months');
INSERT INTO crams_duration (id, duration, duration_label) VALUES (4, 12, '12-months');
INSERT INTO crams_fundingbody (`name`, email) VALUES ('CRAMS', 'crams@crams.com');

-- add funding scheme
INSERT INTO crams_fundingscheme (funding_scheme, funding_body_id) VALUES ('CRAMS-FS', (SELECT id from crams_fundingbody where `name` = 'CRAMS'));

-- Add eResearch Body, related systems and update products
INSERT INTO crams_eresearchbody (`name`, email) VALUES ('CRAMS-ERB', 'crams@crams.com');

INSERT INTO crams_eresearchbodysystem (e_research_body_id, `name`) VALUES ((SELECT id from crams_eresearchbody where `name` = 'CRAMS-ERB'), 'CRAMS-ERB-SYS');
INSERT INTO crams_eresearchbodyidkey (`key`, e_research_body_id, `type`) VALUES ('CRAMS',(SELECT id from crams_eresearchbody where `name` = 'CRAMS-ERB'), 'I');

INSERT INTO crams_provider (id, `name`, active,  created_by_id, creation_ts, description, last_modified_ts, start_date, updated_by_id) VALUES (1, 'CRAMS', true, NULL, '2016-02-01 09:42:48.669521+11', NULL, '2016-02-01 09:42:53.378836+11', '2016-02-01', NULL);
