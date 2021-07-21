INSERT INTO crams_softwarelicensestatus(code, status) VALUES ('R', 'Submit');
INSERT INTO crams_softwarelicensestatus(code, status) VALUES ('A', 'Approve');
INSERT INTO crams_softwarelicensestatus(code, status) VALUES ('D', 'Decline');

set @erb_id = (SELECT id from crams_eresearchbody where `name` = 'CRAMS-ERB');
INSERT INTO crams_eresearchbodyidkey (`key`, e_research_body_id, description, type)
VALUES ('CRAMS_POSIX_USERID', @erb_id, NULL, 'I');
INSERT INTO crams_eresearchbodyidkey (`key`, e_research_body_id, description, type)
VALUES ('CRAMS_SOFTWARE_GROUP_ID', @erb_id, NULL, 'I');
