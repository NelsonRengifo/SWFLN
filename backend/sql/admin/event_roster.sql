/*
 * Returns CursorResult Object
 */


SELECT event_title, start_date, registrant_name, organization, county, attended
FROM events
WHERE start_date >= :start_date AND end_date <= :end_date 
        AND (:attended IS NULL OR attended = :attended)
ORDER BY start_date ASC
LIMIT 26
OFFSET :OFFSET;
