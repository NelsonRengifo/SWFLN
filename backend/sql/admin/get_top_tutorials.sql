/*
 * Returns CursorResult object
 */

SELECT tutorials.tutorial_name, SUM(tutorial_metrics.total_views) AS total_views
FROM tutorials 
INNER JOIN tutorial_metrics ON tutorials.tutorial_id = tutorial_metrics.tutorial_id
WHERE (:start_date IS NULL OR tutorial_metrics.metric_date >= :start_date) 
      AND
      (:end_date IS NULL OR tutorial_metrics.metric_date <= :end_date)
GROUP BY tutorials.tutorial_name
ORDER BY total_views DESC
LIMIT :limit;