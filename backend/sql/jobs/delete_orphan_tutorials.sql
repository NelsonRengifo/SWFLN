/*
 * Returns CursorResult Object
 */

DELETE FROM tutorials
WHERE NOT EXISTS (SELECT 1 
                  FROM tutorial_metrics 
                  WHERE tutorials.tutorial_id = tutorial_metrics.tutorial_id
                 );