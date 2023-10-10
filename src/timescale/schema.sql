CREATE TABLE bosche_sensor (
	time TIMESTAMPTZ,
	metric TEXT,
	value NUMERIC
);

SELECT
	create_hypertable ('bosche_sensor', 'time');