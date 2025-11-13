#!/bin/bash
# Docker entrypoint script for JobSearchTools scheduler
# Handles database initialization and migrations before starting the scheduler

set -e

echo "=========================================="
echo "JobSearchTools Scheduler - Starting"
echo "=========================================="

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
until PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -c '\q' 2>/dev/null; do
    echo "PostgreSQL is unavailable - sleeping"
    sleep 2
done

echo "PostgreSQL is ready!"

# Run database migrations
echo "Running database migrations..."
MIGRATION_DIR="/app/src/jobsearchtools/job_scraper/job_scraper/migrations"

if [ -d "$MIGRATION_DIR" ]; then
    for migration_file in "$MIGRATION_DIR"/*.sql; do
        if [ -f "$migration_file" ]; then
            echo "Applying migration: $(basename "$migration_file")"
            PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -f "$migration_file"
        fi
    done
    echo "Migrations completed successfully"
else
    echo "No migrations directory found, skipping..."
fi

# Start the scheduler
echo "Starting JobSearchTools scheduler..."
exec python -m jobsearchtools.scheduler
