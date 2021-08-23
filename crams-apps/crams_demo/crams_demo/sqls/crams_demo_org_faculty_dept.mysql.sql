-- Organisation
INSERT INTO crams_contact_organisation (id, `name`, short_name, ands_url, notification_email) VALUES (1, 'CRAMS', 'crams', 'https://crams.com', 'notification_email@crams.com');
INSERT INTO crams_contact_organisation (`name`, short_name, ands_url, notification_email) VALUES ('Organisation N1', 'org1', 'http://www.org1.com/', 'notification_email@org1.com');
INSERT INTO crams_contact_organisation (`name`, short_name, ands_url, notification_email) VALUES ('Organisation N2', 'org2', 'http://www.org2.org.au/', 'notification_email@org2.org.au');
INSERT INTO crams_contact_organisation (`name`, short_name, ands_url, notification_email) VALUES ('Organisation N3', 'org3', 'http://www.org3.com/', 'notification_email@org3.com');

-- Faculties
INSERT INTO crams_contact_faculty (id, faculty_code, `name`, organisation_id) VALUES (1, '50000561', 'Faculty of Arts', 1);
INSERT INTO crams_contact_faculty (id, faculty_code, `name`, organisation_id) VALUES (2, '50000563', 'Faculty of Business & Economics', 1);
INSERT INTO crams_contact_faculty (id, faculty_code, `name`, organisation_id) VALUES (3, '50000565', 'Faculty of Engineering', 1);
INSERT INTO crams_contact_faculty (id, faculty_code, `name`, organisation_id) VALUES (4, '50000566', 'Faculty of Information Technology', 1);
INSERT INTO crams_contact_faculty (id, faculty_code, `name`, organisation_id) VALUES (5, '50000570', 'Faculty of Science', 1);
INSERT INTO crams_contact_faculty (id, faculty_code, `name`, organisation_id) VALUES (6, '', '(Not Applicable)', 1);
INSERT INTO crams_contact_faculty (id, faculty_code, `name`, organisation_id) VALUES (7, '', '(Not Applicable)', 2);
INSERT INTO crams_contact_faculty (id, faculty_code, `name`, organisation_id) VALUES (8, '', '(Not Applicable)', 3);
INSERT INTO crams_contact_faculty (id, faculty_code, `name`, organisation_id) VALUES (9, '', '(Not Applicable)', 4);

-- Departments
INSERT INTO crams_contact_department (department_code, `name`, faculty_id) VALUES ('', '(Not Applicable)', 1);
INSERT INTO crams_contact_department (department_code, `name`, faculty_id) VALUES ('', '(Not Applicable)', 2);
INSERT INTO crams_contact_department (department_code, `name`, faculty_id) VALUES ('', '(Not Applicable)', 3);
INSERT INTO crams_contact_department (department_code, `name`, faculty_id) VALUES ('', '(Not Applicable)', 4);
INSERT INTO crams_contact_department (department_code, `name`, faculty_id) VALUES ('', '(Not Applicable)', 5);
INSERT INTO crams_contact_department (department_code, `name`, faculty_id) VALUES ('', '(Not Applicable)', 6);
INSERT INTO crams_contact_department (department_code, `name`, faculty_id) VALUES ('', '(Not Applicable)', 7);
INSERT INTO crams_contact_department (department_code, `name`, faculty_id) VALUES ('', '(Not Applicable)', 8);
INSERT INTO crams_contact_department (department_code, `name`, faculty_id) VALUES ('', '(Not Applicable)', 9);

INSERT INTO crams_contact_department (department_code, `name`, faculty_id) VALUES ('50000575', 'Sch of Social Sciences', 1);
INSERT INTO crams_contact_department (department_code, `name`, faculty_id) VALUES ('50000576', 'Sch of Media Film & Journalism', 1);
INSERT INTO crams_contact_department (department_code, `name`, faculty_id) VALUES ('50000582', 'Arts Faculty Office', 1);
INSERT INTO crams_contact_department (department_code, `name`, faculty_id) VALUES ('50000731', 'Sociology', 1);
INSERT INTO crams_contact_department (department_code, `name`, faculty_id) VALUES ('50000737', 'Literary Studies', 1);
INSERT INTO crams_contact_department (department_code, `name`, faculty_id) VALUES ('50000738', 'Film & Screen Studies', 1);
INSERT INTO crams_contact_department (department_code, `name`, faculty_id) VALUES ('50000746', 'History', 1);
INSERT INTO crams_contact_department (department_code, `name`, faculty_id) VALUES ('50000752', 'Philosophy', 1);
INSERT INTO crams_contact_department (department_code, `name`, faculty_id) VALUES ('50000753', 'Linguistics', 1);
INSERT INTO crams_contact_department (department_code, `name`, faculty_id) VALUES ('50006629', 'Anthropology', 1);
INSERT INTO crams_contact_department (department_code, `name`, faculty_id) VALUES ('50099151', 'Journalism', 1);
INSERT INTO crams_contact_department (department_code, `name`, faculty_id) VALUES ('50168617', 'Music Technology', 1);
INSERT INTO crams_contact_department (department_code, `name`, faculty_id) VALUES ('50140748', 'Composition', 1);
INSERT INTO crams_contact_department (department_code, `name`, faculty_id) VALUES ('50025358', 'Communications & Media Studies', 1);
INSERT INTO crams_contact_department (department_code, `name`, faculty_id) VALUES ('50000780', 'Business & Economics Faculty Office', 2);
INSERT INTO crams_contact_department (department_code, `name`, faculty_id) VALUES ('50000782', 'Business Law & Taxation', 2);
INSERT INTO crams_contact_department (department_code, `name`, faculty_id) VALUES ('50000784', 'Department of Economics', 2);
INSERT INTO crams_contact_department (department_code, `name`, faculty_id) VALUES ('50000793', 'Department of Management', 2);
INSERT INTO crams_contact_department (department_code, `name`, faculty_id) VALUES ('50000794', 'Department of Marketing', 2);
INSERT INTO crams_contact_department (department_code, `name`, faculty_id) VALUES ('50168343', 'Accounting', 2);
INSERT INTO crams_contact_department (department_code, `name`, faculty_id) VALUES ('50168344', 'Banking & Finance', 2);
INSERT INTO crams_contact_department (department_code, `name`, faculty_id) VALUES ('50024034', 'Financial Accounting & Auditing', 2);
INSERT INTO crams_contact_department (department_code, `name`, faculty_id) VALUES ('50000862', 'Engineering Office of the Dean', 3);
INSERT INTO crams_contact_department (department_code, `name`, faculty_id) VALUES ('50000863', 'Chemical Engineering', 3);
INSERT INTO crams_contact_department (department_code, `name`, faculty_id) VALUES ('50000864', 'Civil Engineering', 3);
INSERT INTO crams_contact_department (department_code, `name`, faculty_id) VALUES ('50000865', 'Electrical & Computer Systems Eng', 3);
INSERT INTO crams_contact_department (department_code, `name`, faculty_id) VALUES ('50000866', 'Materials Science & Engineering', 3);
INSERT INTO crams_contact_department (department_code, `name`, faculty_id) VALUES ('50000867', 'Mechanical & Aerospace Engineering', 3);
INSERT INTO crams_contact_department (department_code, `name`, faculty_id) VALUES ('50174825', 'Eng & IT Finance & Resources', 3);
INSERT INTO crams_contact_department (department_code, `name`, faculty_id) VALUES ('50174826', 'Eng & IT Academic & Student Services', 3);
INSERT INTO crams_contact_department (department_code, `name`, faculty_id) VALUES ('50174827', 'Eng & IT Marketing & External Engagement', 3);
INSERT INTO crams_contact_department (department_code, `name`, faculty_id) VALUES ('50069831', 'Biological Engineering', 3);
INSERT INTO crams_contact_department (department_code, `name`, faculty_id) VALUES ('50080739', 'Inst of Railway Technology', 3);
INSERT INTO crams_contact_department (department_code, `name`, faculty_id) VALUES ('50000927', 'Information Technology Faculty Office', 4);
INSERT INTO crams_contact_department (department_code, `name`, faculty_id) VALUES ('50174822', 'IT & Eng Finance & Resources', 4);
INSERT INTO crams_contact_department (department_code, `name`, faculty_id) VALUES ('50174823', 'IT & Eng Academic & Student Services', 4);
INSERT INTO crams_contact_department (department_code, `name`, faculty_id) VALUES ('50174824', 'IT & Eng Marketing & External Engagement', 4);
INSERT INTO crams_contact_department (department_code, `name`, faculty_id) VALUES ('50000945', 'Science Faculty Office', 5);
INSERT INTO crams_contact_department (department_code, `name`, faculty_id) VALUES ('50000974', 'Sch of Biological Sciences', 5);
INSERT INTO crams_contact_department (department_code, `name`, faculty_id) VALUES ('50000975', 'Sch of Chemistry', 5);
INSERT INTO crams_contact_department (department_code, `name`, faculty_id) VALUES ('50000977', 'Sch of Mathematical Sciences', 5);
INSERT INTO crams_contact_department (department_code, `name`, faculty_id) VALUES ('50123381', 'Green Chemical Futures', 5);
INSERT INTO crams_contact_department (department_code, `name`, faculty_id) VALUES ('50181807', 'Sch of Earth Atmosphere & Environment', 5);
INSERT INTO crams_contact_department (department_code, `name`, faculty_id) VALUES ('50189102', 'Sch of Physics & Astronomy', 5);

