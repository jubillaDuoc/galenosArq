/*
DROP TABLE MEDICO CASCADE;
DROP TABLE ESPECIALIDAD CASCADE;
DROP TABLE CENTRO_MEDICO CASCADE;
DROP TABLE HORA_ATENCION CASCADE;
DROP TABLE HORA_CENTROMEDICO CASCADE;
DROP TABLE MEDICO_DISPONIBILIDAD CASCADE;
DROP TABLE PACIENTE CASCADE;
DROP TABLE CITA CASCADE;
DROP TABLE PAGO CASCADE;
DROP TABLE COMISION CASCADE;
*/

CREATE TABLE ESPECIALIDAD (
    id_especialidad         INTEGER PRIMARY KEY,
    nombre_especialidad     VARCHAR(200) NOT NULL
);

CREATE TABLE MEDICO (
    id_medico               INTEGER PRIMARY KEY,
    nombre_medico           VARCHAR(200) NOT NULL,
    email_medico            VARCHAR(200) NOT NULL,
    id_especialidad         INTEGER NOT NULL REFERENCES ESPECIALIDAD,
    rut_medico              INTEGER NOT NULL
);

CREATE TABLE CENTRO_MEDICO (
    id_centromedico         INTEGER PRIMARY KEY,
    nombre_centromedico     VARCHAR(200) NOT NULL,
    direccion_centromedico  VARCHAR(200) NOT NULL
);

CREATE TABLE HORA_ATENCION (
    id_horaatencion     INTEGER PRIMARY KEY,
    fecha               VARCHAR(200) NOT NULL,
    horainicio          INTEGER NOT NULL,
    horafin             INTEGER NOT NULL
);

CREATE TABLE HORA_CENTROMEDICO (
    id_hora_centromedico    INTEGER PRIMARY KEY,
    id_centromedico         INTEGER NOT NULL REFERENCES CENTRO_MEDICO,
    id_horaatencion         INTEGER NOT NULL REFERENCES HORA_ATENCION
);

CREATE TABLE MEDICO_DISPONIBILIDAD (
    id_med_disp             INTEGER PRIMARY KEY,
    id_medico               INTEGER NOT NULL REFERENCES MEDICO,
    id_hora_centromedico    INTEGER NOT NULL REFERENCES HORA_CENTROMEDICO,
    estado_disponibilidad   VARCHAR(200) NOT NULL
);

CREATE TABLE PACIENTE (
    id_paciente         INTEGER PRIMARY KEY,
    nombre_paciente     VARCHAR(200) NOT NULL,
    email_paciente      VARCHAR(200) NOT NULL,
    numtel_paciente     INTEGER NOT NULL,
    rut_paciente        INTEGER NOT NULL
);

CREATE TABLE CITA (
    id_cita         INTEGER PRIMARY KEY,
    id_med_disp     INTEGER NOT NULL REFERENCES MEDICO_DISPONIBILIDAD,
    id_paciente     INTEGER NOT NULL REFERENCES PACIENTE,
    estado          VARCHAR(200) NOT NULL
);

CREATE TABLE PAGO (
    id_pago         INTEGER PRIMARY KEY,
    monto_pago      INTEGER NOT NULL,
    metodo_pago     VARCHAR(200) NOT NULL,
    id_cita         INTEGER NOT NULL REFERENCES CITA
);

CREATE TABLE COMISION (
    id_comision         INTEGER PRIMARY KEY,
    monto_comision      INTEGER NOT NULL,
    fecha_pagocomision  VARCHAR(200) NOT NULL,
    id_cita             INTEGER NOT NULL REFERENCES CITA
);

CREATE VIEW view_full_cita as
    SELECT cita.id_cita,
        paciente.nombre_paciente,
        paciente.email_paciente,
        medico.nombre_medico,
        especialidad.nombre_especialidad,
        hora_atencion.fecha,
        hora_atencion.horainicio,
        hora_atencion.horafin,
        centro_medico.nombre_centromedico,
        centro_medico.direccion_centromedico
    FROM (((((((cita
        JOIN medico_disponibilidad USING (id_med_disp))
        JOIN medico USING (id_medico))
        JOIN especialidad USING (id_especialidad))
        JOIN hora_centromedico USING (id_hora_centromedico))
        JOIN hora_atencion USING (id_horaatencion))
        JOIN centro_medico USING (id_centromedico))
        JOIN paciente USING (id_paciente));

CREATE SEQUENCE seq_horas_medicas
    START WITH 100
    INCREMENT BY 1;

CREATE SEQUENCE seq_hora_centromedico
    START WITH 100
    INCREMENT BY 1;

CREATE SEQUENCE seq_medico_disponibilidad
    START WITH 100
    INCREMENT BY 1;

CREATE SEQUENCE seq_id_cita
    START WITH 100
    INCREMENT BY 1;

CREATE SEQUENCE seq_id_paciente
    START WITH 100
    INCREMENT BY 1;

INSERT INTO "especialidad" ("id_especialidad", "nombre_especialidad") VALUES
(1,	'Neurologia'),
(2,	'Traumatologia'),
(3,	'Oftalmologia');

INSERT INTO "medico" ("id_medico", "nombre_medico", "email_medico", "id_especialidad", "rut_medico") VALUES
(1,	'Juan Medico',	'juanmedico@example.com',	1,	20279851),
(2,	'Bastian Medico',	'bastianmedico@example.com',	2,	20279852),
(3,	'Jose Medico',	'josemedico@example.com',	2,	20279853),
(4,	'Cabo Medico',	'cabomedico@example.com',	3,	20279854);

INSERT INTO "centro_medico" ("id_centromedico", "nombre_centromedico", "direccion_centromedico") VALUES (1,	'Galenos',	'Galenos 123, Galenos');
