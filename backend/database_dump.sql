BEGIN TRANSACTION;
CREATE TABLE assignments (
	id INTEGER NOT NULL, 
	base_id INTEGER, 
	equipment_type_id INTEGER, 
	personnel VARCHAR, 
	kind VARCHAR, 
	quantity INTEGER, 
	date DATE, 
	PRIMARY KEY (id), 
	FOREIGN KEY(base_id) REFERENCES bases (id), 
	FOREIGN KEY(equipment_type_id) REFERENCES equipment_types (id)
);
INSERT INTO "assignments" VALUES(1,1,1,'Sgt. Rao','assigned',5,'2026-09-25');
INSERT INTO "assignments" VALUES(2,1,1,'Sgt. Rao','expended',2,'2026-09-28');
CREATE TABLE audit_logs (
	id INTEGER NOT NULL, 
	timestamp DATETIME, 
	username VARCHAR, 
	action VARCHAR, 
	detail VARCHAR, 
	PRIMARY KEY (id)
);
INSERT INTO "audit_logs" VALUES(1,'2026-09-30 10:05:53.368369','admin','LOGIN','');
INSERT INTO "audit_logs" VALUES(2,'2026-10-01 04:16:56.143856','admin','LOGIN','');
INSERT INTO "audit_logs" VALUES(3,'2026-10-01 04:20:18.258054','commander','LOGIN','');
CREATE TABLE bases (
	id INTEGER NOT NULL, 
	name VARCHAR, 
	PRIMARY KEY (id), 
	UNIQUE (name)
);
INSERT INTO "bases" VALUES(1,'Alpha');
INSERT INTO "bases" VALUES(2,'Bravo');
INSERT INTO "bases" VALUES(3,'Charlie');
CREATE TABLE equipment_types (
	id INTEGER NOT NULL, 
	name VARCHAR, 
	category VARCHAR, 
	PRIMARY KEY (id), 
	UNIQUE (name)
);
INSERT INTO "equipment_types" VALUES(1,'M4 Rifle','weapon');
INSERT INTO "equipment_types" VALUES(2,'Humvee','vehicle');
INSERT INTO "equipment_types" VALUES(3,'5.56mm Ammo','ammunition');
CREATE TABLE purchases (
	id INTEGER NOT NULL, 
	base_id INTEGER, 
	equipment_type_id INTEGER, 
	quantity INTEGER, 
	date DATE, 
	PRIMARY KEY (id), 
	FOREIGN KEY(base_id) REFERENCES bases (id), 
	FOREIGN KEY(equipment_type_id) REFERENCES equipment_types (id)
);
INSERT INTO "purchases" VALUES(1,1,1,100,'2026-08-31');
INSERT INTO "purchases" VALUES(2,2,2,20,'2026-09-10');
CREATE TABLE transfers (
	id INTEGER NOT NULL, 
	from_base_id INTEGER, 
	to_base_id INTEGER, 
	equipment_type_id INTEGER, 
	quantity INTEGER, 
	date DATE, 
	created_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(from_base_id) REFERENCES bases (id), 
	FOREIGN KEY(to_base_id) REFERENCES bases (id), 
	FOREIGN KEY(equipment_type_id) REFERENCES equipment_types (id)
);
INSERT INTO "transfers" VALUES(1,1,2,1,10,'2026-09-20','2026-09-30 09:54:55.858539');
CREATE TABLE users (
	id INTEGER NOT NULL, 
	username VARCHAR, 
	password_hash VARCHAR, 
	role VARCHAR, 
	base_id INTEGER, 
	PRIMARY KEY (id), 
	UNIQUE (username), 
	FOREIGN KEY(base_id) REFERENCES bases (id)
);
INSERT INTO "users" VALUES(1,'admin','1af490cf160a302fad7876f75bc6362609ea2322592a368d75e5c6d44c3e1537','admin',NULL);
INSERT INTO "users" VALUES(2,'commander','62bb63cdfe57624a91a391dc37bd740a35918e700c2192834d8067ffb3d5e739','base_commander',1);
INSERT INTO "users" VALUES(3,'logistics','9bc9e954b8496f420416a9b73f62f3cd04fd479743140bad280cafa505d6520b','logistics_officer',1);
COMMIT;
