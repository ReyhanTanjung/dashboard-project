CREATE TABLE energy_data (
    id SERIAL PRIMARY KEY,
    reading_time TIMESTAMP NOT NULL,
    active_energy_import DOUBLE PRECISION NOT NULL,
    active_energy_export DOUBLE PRECISION NOT NULL,
    reactive_energy_import DOUBLE PRECISION NOT NULL,
    reactive_energy_export DOUBLE PRECISION NOT NULL,
    apparent_energy_import DOUBLE PRECISION NOT NULL,
    apparent_energy_export DOUBLE PRECISION NOT NULL
);
