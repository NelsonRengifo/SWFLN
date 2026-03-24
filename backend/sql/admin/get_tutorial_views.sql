/*
 * Returns CursorResult object
 */

SELECT COALESCE(metric_date::TEXT, 'Total') AS metric_date, SUM(total_views) as views
FROM tutorial_metrics
WHERE metric_date BETWEEN :start_date AND :end_date
GROUP BY ROLLUP (metric_date)
ORDER BY metric_date ASC;