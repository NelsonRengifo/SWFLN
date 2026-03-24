/*
 * Returns CursorResult object
 */

SELECT COALESCE(event_type, 'total') as event_type, COUNT(*) AS total_events
FROM events
WHERE (:start_date IS NULL OR events.start_date >= :start_date)
      AND
      (:end_date IS NULL OR events.end_date <= :end_date)
GROUP BY ROLLUP (event_type)
ORDER BY event_type ASC;