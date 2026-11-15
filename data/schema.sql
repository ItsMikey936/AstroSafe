-- =====================================================================
-- Astronaut health monitoring system - revised schema (SQLite)
-- Conventions
--   * Dates:      'YYYY-MM-DD'           (enforced: col IS date(col))
--   * Timestamps: 'YYYY-MM-DD HH:MM:SS'  UTC (enforced: col IS datetime(col))
--   * Files are referenced by relative path only; no binary content is stored.
--   * Constraints: ck_<table>_<rule>; indexes: ix_ (plain) / ux_ (unique).
-- =====================================================================
PRAGMA foreign_keys = ON;

-- ---------------------------------------------------------------------
-- Catalogs
-- ---------------------------------------------------------------------
CREATE TABLE position (
  position_id INTEGER PRIMARY KEY,
  name        TEXT NOT NULL UNIQUE
);

CREATE TABLE alert_state (
  state_id INTEGER PRIMARY KEY,
  name     TEXT NOT NULL UNIQUE
);

CREATE TABLE emergency_type (
  emergency_type_id INTEGER PRIMARY KEY,
  name              TEXT NOT NULL UNIQUE
);

CREATE TABLE metric (
  metric_id INTEGER PRIMARY KEY,
  name      TEXT NOT NULL UNIQUE,
  unit      TEXT NOT NULL
);

CREATE TABLE record_type (
  record_type_id INTEGER PRIMARY KEY,
  name           TEXT NOT NULL UNIQUE
);

-- ---------------------------------------------------------------------
-- Crew and missions
-- ---------------------------------------------------------------------
CREATE TABLE astronaut (
  astronaut_id INTEGER PRIMARY KEY,
  name         TEXT    NOT NULL,
  position_id  INTEGER NOT NULL REFERENCES position(position_id)
);
CREATE INDEX ix_astronaut_position ON astronaut(position_id);

CREATE TABLE mission (
  mission_id INTEGER PRIMARY KEY,
  name       TEXT NOT NULL UNIQUE,
  start_date TEXT NOT NULL
             CONSTRAINT ck_mission_start_format CHECK (start_date IS date(start_date)),
  end_date   TEXT
             CONSTRAINT ck_mission_end_format CHECK (end_date IS NULL OR end_date IS date(end_date)),
  CONSTRAINT ck_mission_dates CHECK (end_date IS NULL OR end_date >= start_date)
);

CREATE TABLE mission_crew (
  mission_id   INTEGER NOT NULL REFERENCES mission(mission_id),
  astronaut_id INTEGER NOT NULL REFERENCES astronaut(astronaut_id),
  PRIMARY KEY (mission_id, astronaut_id)
);
CREATE INDEX ix_mission_crew_astronaut ON mission_crew(astronaut_id);

-- ---------------------------------------------------------------------
-- Watches
-- ---------------------------------------------------------------------
CREATE TABLE watch (
  watch_id TEXT PRIMARY KEY
);

CREATE TABLE watch_assignment (
  watch_id      TEXT    NOT NULL REFERENCES watch(watch_id),
  astronaut_id  INTEGER NOT NULL REFERENCES astronaut(astronaut_id),
  assigned_from TEXT    NOT NULL
                CONSTRAINT ck_watch_assignment_from_format CHECK (assigned_from IS datetime(assigned_from)),
  assigned_to   TEXT
                CONSTRAINT ck_watch_assignment_to_format CHECK (assigned_to IS NULL OR assigned_to IS datetime(assigned_to)),
  PRIMARY KEY (watch_id, assigned_from),
  CONSTRAINT ck_watch_assignment_period CHECK (assigned_to IS NULL OR assigned_to > assigned_from)
);
-- At most one open assignment per watch and per astronaut
CREATE UNIQUE INDEX ux_watch_assignment_open_watch     ON watch_assignment(watch_id)     WHERE assigned_to IS NULL;
CREATE UNIQUE INDEX ux_watch_assignment_open_astronaut ON watch_assignment(astronaut_id) WHERE assigned_to IS NULL;
CREATE INDEX ix_watch_assignment_astronaut ON watch_assignment(astronaut_id, assigned_from);

-- ---------------------------------------------------------------------
-- Biometrics: every second (from the watch)
-- ---------------------------------------------------------------------
CREATE TABLE reading (
  watch_id           TEXT NOT NULL REFERENCES watch(watch_id),
  recorded_at        TEXT NOT NULL
                     CONSTRAINT ck_reading_time_format CHECK (recorded_at IS datetime(recorded_at)),
  bpm                INTEGER NOT NULL
                     CONSTRAINT ck_reading_bpm CHECK (bpm > 0),
  oxygenation_pct    REAL    NOT NULL
                     CONSTRAINT ck_reading_oxygenation CHECK (oxygenation_pct BETWEEN 0 AND 100),
  body_temp_c        REAL    NOT NULL,
  radiation_dose_msv REAL    NOT NULL
                     CONSTRAINT ck_reading_dose CHECK (radiation_dose_msv >= 0),
  PRIMARY KEY (watch_id, recorded_at)
) WITHOUT ROWID;

-- ---------------------------------------------------------------------
-- Biometrics: occasional
-- ---------------------------------------------------------------------
CREATE TABLE body_composition (
  astronaut_id                INTEGER NOT NULL REFERENCES astronaut(astronaut_id),
  measured_at                 TEXT    NOT NULL
                              CONSTRAINT ck_body_composition_time_format CHECK (measured_at IS datetime(measured_at)),
  muscle_mass_kg              REAL    NOT NULL
                              CONSTRAINT ck_body_composition_muscle CHECK (muscle_mass_kg > 0),
  bone_mineral_density_g_cm2  REAL    NOT NULL
                              CONSTRAINT ck_body_composition_bone CHECK (bone_mineral_density_g_cm2 > 0),
  PRIMARY KEY (astronaut_id, measured_at)
);

CREATE TABLE sleep_log (
  astronaut_id INTEGER NOT NULL REFERENCES astronaut(astronaut_id),
  sleep_date   TEXT    NOT NULL
               CONSTRAINT ck_sleep_log_date_format CHECK (sleep_date IS date(sleep_date)),
  hours        REAL    NOT NULL
               CONSTRAINT ck_sleep_log_hours CHECK (hours BETWEEN 0 AND 24),
  PRIMARY KEY (astronaut_id, sleep_date)
);

-- Other measured metrics shown on the crew detail screen
-- (intracranial pressure, stress level, fatigue level). Name and unit
-- of each value come from the metric catalog.
CREATE TABLE measurement (
  astronaut_id   INTEGER NOT NULL REFERENCES astronaut(astronaut_id),
  metric_id      INTEGER NOT NULL REFERENCES metric(metric_id),
  measured_at    TEXT    NOT NULL
                 CONSTRAINT ck_measurement_time_format CHECK (measured_at IS datetime(measured_at)),
  measured_value REAL    NOT NULL,
  PRIMARY KEY (astronaut_id, metric_id, measured_at)
);

-- ---------------------------------------------------------------------
-- Thresholds and alerts
-- ---------------------------------------------------------------------
CREATE TABLE threshold (
  emergency_type_id INTEGER NOT NULL REFERENCES emergency_type(emergency_type_id),
  metric_id         INTEGER NOT NULL REFERENCES metric(metric_id),
  state_id          INTEGER NOT NULL REFERENCES alert_state(state_id),
  min_value         REAL,
  max_value         REAL,
  PRIMARY KEY (emergency_type_id, metric_id, state_id),
  CONSTRAINT ck_threshold_bound_present CHECK (min_value IS NOT NULL OR max_value IS NOT NULL),
  CONSTRAINT ck_threshold_bound_order   CHECK (min_value IS NULL OR max_value IS NULL OR min_value <= max_value)
);

CREATE TABLE alert (
  alert_id          INTEGER PRIMARY KEY,
  astronaut_id      INTEGER NOT NULL REFERENCES astronaut(astronaut_id),
  emergency_type_id INTEGER NOT NULL REFERENCES emergency_type(emergency_type_id),
  state_id          INTEGER NOT NULL REFERENCES alert_state(state_id),
  triggered_at      TEXT    NOT NULL
                    CONSTRAINT ck_alert_time_format CHECK (triggered_at IS datetime(triggered_at))
);
CREATE INDEX ix_alert_astronaut_time ON alert(astronaut_id, triggered_at);

-- ---------------------------------------------------------------------
-- Library (procedure screens): image stored as a relative path,
-- description stored as text, plus up to three titled sections.
-- ---------------------------------------------------------------------
CREATE TABLE treatment (
  treatment_id INTEGER PRIMARY KEY,
  name         TEXT NOT NULL UNIQUE,
  description  TEXT NOT NULL,
  image_path   TEXT NOT NULL
               CONSTRAINT ck_treatment_image_relative CHECK (image_path NOT LIKE '/%')
);

CREATE TABLE hazard (
  hazard_id   INTEGER PRIMARY KEY,
  name        TEXT NOT NULL UNIQUE,
  description TEXT NOT NULL,
  image_path  TEXT NOT NULL
              CONSTRAINT ck_hazard_image_relative CHECK (image_path NOT LIKE '/%')
);

CREATE TABLE disease (
  disease_id  INTEGER PRIMARY KEY,
  name        TEXT NOT NULL UNIQUE,
  description TEXT NOT NULL,
  image_path  TEXT NOT NULL
              CONSTRAINT ck_disease_image_relative CHECK (image_path NOT LIKE '/%')
);

CREATE TABLE treatment_section (
  treatment_id   INTEGER NOT NULL REFERENCES treatment(treatment_id) ON DELETE CASCADE,
  section_number INTEGER NOT NULL
                 CONSTRAINT ck_treatment_section_number CHECK (section_number BETWEEN 1 AND 3),
  title          TEXT    NOT NULL,
  description    TEXT    NOT NULL,
  PRIMARY KEY (treatment_id, section_number)
);

CREATE TABLE hazard_section (
  hazard_id      INTEGER NOT NULL REFERENCES hazard(hazard_id) ON DELETE CASCADE,
  section_number INTEGER NOT NULL
                 CONSTRAINT ck_hazard_section_number CHECK (section_number BETWEEN 1 AND 3),
  title          TEXT    NOT NULL,
  description    TEXT    NOT NULL,
  PRIMARY KEY (hazard_id, section_number)
);

CREATE TABLE disease_section (
  disease_id     INTEGER NOT NULL REFERENCES disease(disease_id) ON DELETE CASCADE,
  section_number INTEGER NOT NULL
                 CONSTRAINT ck_disease_section_number CHECK (section_number BETWEEN 1 AND 3),
  title          TEXT    NOT NULL,
  description    TEXT    NOT NULL,
  PRIMARY KEY (disease_id, section_number)
);

CREATE TABLE disease_treatment (
  disease_id   INTEGER NOT NULL REFERENCES disease(disease_id),
  treatment_id INTEGER NOT NULL REFERENCES treatment(treatment_id),
  PRIMARY KEY (disease_id, treatment_id)
);
CREATE INDEX ix_disease_treatment_treatment ON disease_treatment(treatment_id);

CREATE TABLE emergency_hazard (
  emergency_type_id INTEGER NOT NULL REFERENCES emergency_type(emergency_type_id),
  hazard_id         INTEGER NOT NULL REFERENCES hazard(hazard_id),
  PRIMARY KEY (emergency_type_id, hazard_id)
);
CREATE INDEX ix_emergency_hazard_hazard ON emergency_hazard(hazard_id);

CREATE TABLE emergency_treatment (
  emergency_type_id INTEGER NOT NULL REFERENCES emergency_type(emergency_type_id),
  treatment_id      INTEGER NOT NULL REFERENCES treatment(treatment_id),
  PRIMARY KEY (emergency_type_id, treatment_id)
);
CREATE INDEX ix_emergency_treatment_treatment ON emergency_treatment(treatment_id);

-- ---------------------------------------------------------------------
-- Records (includes voice records)
-- ---------------------------------------------------------------------
CREATE TABLE record (
  record_id      INTEGER PRIMARY KEY,
  astronaut_id   INTEGER NOT NULL REFERENCES astronaut(astronaut_id),
  record_type_id INTEGER NOT NULL REFERENCES record_type(record_type_id),
  record_date    TEXT    NOT NULL
                 CONSTRAINT ck_record_date_format CHECK (record_date IS date(record_date)),
  file_path      TEXT    NOT NULL
                 CONSTRAINT ck_record_file_relative CHECK (file_path NOT LIKE '/%')
);
CREATE INDEX ix_record_astronaut_date ON record(astronaut_id, record_date);
CREATE INDEX ix_record_type ON record(record_type_id);

-- ---------------------------------------------------------------------
-- Derived data as views (not stored)
-- ---------------------------------------------------------------------
-- Daily radiation dose per astronaut (assumes each reading holds the dose
-- received during that reading's interval).
CREATE VIEW v_daily_dose AS
SELECT wa.astronaut_id,
       date(r.recorded_at)       AS day,
       SUM(r.radiation_dose_msv) AS daily_dose_msv
FROM reading r
JOIN watch_assignment wa
  ON wa.watch_id = r.watch_id
 AND r.recorded_at >= wa.assigned_from
 AND (wa.assigned_to IS NULL OR r.recorded_at < wa.assigned_to)
GROUP BY wa.astronaut_id, date(r.recorded_at);

-- Running total of the daily dose per astronaut.
CREATE VIEW v_cumulative_dose AS
SELECT astronaut_id,
       day,
       SUM(daily_dose_msv) OVER (PARTITION BY astronaut_id ORDER BY day) AS cumulative_dose_msv
FROM v_daily_dose;

-- Latest reading of each astronaut's currently assigned watch
-- (crew general view: SpO2 and bpm; crew detail: body temperature).
CREATE VIEW v_latest_reading AS
SELECT wa.astronaut_id,
       r.watch_id,
       r.recorded_at,
       r.bpm,
       r.oxygenation_pct,
       r.body_temp_c,
       r.radiation_dose_msv
FROM watch_assignment wa
JOIN reading r
  ON r.watch_id = wa.watch_id
WHERE wa.assigned_to IS NULL
  AND r.recorded_at = (SELECT MAX(r2.recorded_at)
                       FROM reading r2
                       WHERE r2.watch_id = wa.watch_id
                         AND r2.recorded_at >= wa.assigned_from);
