# Migration: `7817cb5869b5_add_google_id_and_image_to_user_model.py`

## Purpose
This migration script, identified by `7817cb5869b5`, is a significant initial migration that sets up the core database schema for the application. It creates several key tables, including `job_listings`, `users`, `education`, `experience`, `job_preferences`, and `projects`. It also specifically adds `google_id` and `image` columns to the `users` table, supporting Google OAuth integration.

## Revision Details
- **Revision ID**: `7817cb5869b5`
- **Revises**: `None` (This indicates it's a base migration, or the first in its branch).
- **Create Date**: `2025-07-19 21:24:36.372609`

## `upgrade()` Function - Schema Changes
This function performs the following operations:

### Table Creation

1.  **`job_listings` Table**:
    -   `id` (String, Primary Key)
    -   `title` (String, Not Null)
    -   `company` (String, Not Null)
    -   `location` (String, Not Null)
    -   `description` (Text, Not Null)
    -   `requirements` (Text, Nullable)
    -   `salary` (String, Nullable)
    -   `posting_date` (DateTime, Nullable)
    -   `url` (String, Not Null, Unique)
    -   `source` (String, Nullable)
    -   `date_discovered` (DateTime, Nullable)
    -   `is_applied` (Boolean, Nullable)
    -   `application_status` (String, Nullable)

2.  **`users` Table**:
    -   `id` (Integer, Primary Key)
    -   `username` (String, Not Null, Unique)
    -   `email` (String, Unique Index `ix_users_email`)
    -   `hashed_password` (String, Nullable)
    -   `google_id` (String, Nullable, Unique Index `ix_users_google_id`)
    -   `image` (String, Nullable)
    -   `is_active` (Boolean, Nullable)
    -   `created_at` (DateTime, Nullable)
    -   `phone` (String, Nullable)
    -   `address` (String, Nullable)
    -   `portfolio_url` (String, Nullable)
    -   `personal_website` (String, Nullable)
    -   `linkedin_profile` (String, Nullable)
    -   `github_profile` (String, Nullable)
    -   `years_of_experience` (Integer, Nullable)
    -   `skills` (Text, Nullable)

3.  **`education` Table**:
    -   `id` (Integer, Primary Key)
    -   `user_id` (Integer, Foreign Key to `users.id`)
    -   `degree` (String, Not Null)
    -   `university` (String, Not Null)
    -   `field_of_study` (String, Not Null)
    -   `start_date` (DateTime, Not Null)
    -   `end_date` (DateTime, Nullable)
    -   `description` (Text, Nullable)

4.  **`experience` Table**:
    -   `id` (Integer, Primary Key)
    -   `user_id` (Integer, Foreign Key to `users.id`)
    -   `title` (String, Not Null)
    -   `company` (String, Not Null)
    -   `location` (String, Nullable)
    -   `start_date` (DateTime, Not Null)
    -   `end_date` (DateTime, Nullable)
    -   `description` (Text, Nullable)

5.  **`job_preferences` Table**:
    -   `id` (Integer, Primary Key)
    -   `user_id` (Integer, Foreign Key to `users.id`, Unique)
    -   `company_size` (String, Nullable)
    -   `industry` (String, Nullable)
    -   `job_titles` (Text, Nullable)
    -   `locations` (Text, Nullable)
    -   `remote` (Boolean, Nullable)

6.  **`projects` Table**:
    -   `id` (Integer, Primary Key)
    -   `user_id` (Integer, Foreign Key to `users.id`)
    -   `name` (String, Not Null)
    -   `description` (Text, Nullable)
    -   `technologies` (Text, Nullable)
    -   `url` (String, Nullable)

## `downgrade()` Function - Reversion
This function reverses the `upgrade()` operations by dropping all the tables created:
-   `projects`
-   `job_preferences`
-   `experience`
-   `education`
-   `users` (including dropping its indexes)
-   `job_listings`

## Usage
This migration is crucial for initializing the database schema. It should be applied as one of the first migrations when setting up a new database instance for the application.