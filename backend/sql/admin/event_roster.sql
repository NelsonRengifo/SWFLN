/*
 * Returns CursorResult Object
 */


SELECT event_title, start_date, registrant_name, organization, county, attended
FROM events
WHERE start_date >= :start_date AND end_date <= :end_date
LIMIT 26
OFFSET :OFFSET;
