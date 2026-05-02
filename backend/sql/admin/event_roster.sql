/*
 * Returns CursorResult Object
 */


SELECT event_title, start_date, registrant_name, organization, county, attended
FROM events
LIMIT 26
OFFSET :OFFSET;
