SELECT COUNT(*)
FROM events
WHERE start_date >= :start_date AND end_date <= :end_date;