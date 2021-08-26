-- noinspection SqlDialectInspectionForFile
-- noinspection SqlNoDataSourceInspectionForFile
INSERT INTO crams_allocation_requeststatus (id, code, status, transient) VALUES (1, 'N', 'New Draft', false);
INSERT INTO crams_allocation_requeststatus (id, code, status, transient) VALUES (2, 'E', 'Submitted', false);
INSERT INTO crams_allocation_requeststatus (id, code, status, transient) VALUES (3, 'A', 'Approved', false);
INSERT INTO crams_allocation_requeststatus (id, code, status, transient) VALUES (4, 'P', 'Provisioned', false);
INSERT INTO crams_allocation_requeststatus (id, code, status, transient) VALUES (5, 'X', 'Update/Extension Requested', false);
INSERT INTO crams_allocation_requeststatus (id, code, status, transient) VALUES (6, 'R', 'Declined', false);
INSERT INTO crams_allocation_requeststatus (id, code, status, transient) VALUES (7, 'J', 'Update/Extension Declined', false);
INSERT INTO crams_allocation_requeststatus (id, code, status, transient) VALUES (8, 'L', 'Legacy Submission', false);
INSERT INTO crams_allocation_requeststatus (id, code, status, transient) VALUES (9, 'M', 'Legacy Approved', false);
INSERT INTO crams_allocation_requeststatus (id, code, status, transient) VALUES (10, 'O', 'Legacy Rejected', false);
INSERT INTO crams_allocation_requeststatus (id, code, status, transient) VALUES (11, '_PP', '_PartialProvision', true);
INSERT INTO crams_allocation_requeststatus (id, code, status, transient) VALUES (12, 'D', 'Update/Extension Draft', false);
INSERT INTO crams_allocation_requeststatus (id, code, status, transient) VALUES (13, 'U', 'Application Updated', false);

INSERT INTO crams_allocation_allocationhome(id, code, description) VALUES (1, 'national', 'National/Unassigned');
