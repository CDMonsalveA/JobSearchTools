-- Migration: Create scheduler state table
-- Description: Tracks the last successful spider run timestamp for scheduling logic

CREATE TABLE IF NOT EXISTS scheduler_state (
    id SERIAL PRIMARY KEY,
    last_run_at TIMESTAMP WITH TIME ZONE NOT NULL,
    spider_count INTEGER NOT NULL DEFAULT 0,
    status VARCHAR(50) NOT NULL DEFAULT 'completed',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_scheduler_state_last_run
ON scheduler_state(last_run_at DESC);

-- Insert initial state if table is empty
INSERT INTO scheduler_state (last_run_at, spider_count, status)
SELECT CURRENT_TIMESTAMP - INTERVAL '5 hours', 0, 'completed'
WHERE NOT EXISTS (SELECT 1 FROM scheduler_state);

-- Add comment
COMMENT ON TABLE scheduler_state IS 'Tracks scheduler execution state for persistent scheduling across container restarts';
