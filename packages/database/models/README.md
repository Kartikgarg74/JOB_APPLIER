# Database Models Module

## Purpose
This module (`models.py`) defines the SQLAlchemy ORM (Object Relational Mapper) models that represent the database tables and their relationships. These models are the Pythonic representation of the application's data structure, allowing for object-oriented interaction with the database.

## Dependencies
- `sqlalchemy`: For defining columns, data types, and foreign keys.
- `sqlalchemy.orm.relationship`: For defining relationships between models.
- `datetime.datetime`: For `DateTime` column defaults.
- `.config.Base`: The declarative base class from which all ORM models inherit.

## Key Components

### `User` Model
- **Table Name**: `users`
- **Purpose**: Represents individual user accounts and their core profile information.
- **Fields**:
  - `id` (Integer, Primary Key)
  - `username` (String, Unique, Not Null)
  - `email` (String, Unique, Indexed)
  - `hashed_password` (String, Nullable): For traditional password-based login.
  - `google_id` (String, Unique, Indexed, Nullable): For Google OAuth login.
  - `image` (String, Nullable): URL to user's profile image.
  - `is_active` (Boolean, Default: True)
  - `created_at` (DateTime, Default: UTC Now)
  - `phone` (String, Nullable)
  - `address` (String, Nullable)
  - `portfolio_url` (String, Nullable)
  - `personal_website` (String, Nullable)
  - `linkedin_profile` (String, Nullable)
  - `github_profile` (String, Nullable)
  - `years_of_experience` (Integer, Nullable)
  - `skills` (Text, Nullable): Note: This field is deprecated in favor of the `Skill` relationship.
- **Relationships**:
  - `education`: One-to-many with `Education` (cascades delete).
  - `experience`: One-to-many with `Experience` (cascades delete).
  - `projects`: One-to-many with `Project` (cascades delete).
  - `job_preferences`: One-to-one with `JobPreference` (cascades delete).
  - `skills`: One-to-many with `Skill` (cascades delete).

### `Education` Model
- **Table Name**: `education`
- **Purpose**: Stores educational background for a user.
- **Fields**:
  - `id` (Integer, Primary Key)
  - `user_id` (Integer, Foreign Key to `users.id`)
  - `degree` (String, Not Null)
  - `university` (String, Not Null)
  - `field_of_study` (String, Not Null)
  - `start_date` (DateTime, Not Null)
  - `end_date` (DateTime, Nullable)
  - `description` (Text, Nullable)
- **Relationship**: `user`: Many-to-one with `User`.

### `Experience` Model
- **Table Name**: `experience`
- **Purpose**: Stores professional work experience for a user.
- **Fields**:
  - `id` (Integer, Primary Key)
  - `user_id` (Integer, Foreign Key to `users.id`)
  - `title` (String, Not Null)
  - `company` (String, Not Null)
  - `location` (String, Nullable)
  - `start_date` (DateTime, Not Null)
  - `end_date` (DateTime, Nullable)
  - `description` (Text, Nullable)
- **Relationship**: `user`: Many-to-one with `User`.

### `Project` Model
- **Table Name**: `projects`
- **Purpose**: Stores personal or professional projects for a user.
- **Fields**:
  - `id` (Integer, Primary Key)
  - `user_id` (Integer, Foreign Key to `users.id`)
  - `name` (String, Not Null)
  - `description` (Text, Nullable)
  - `technologies` (Text, Nullable): Stores technologies used (e.g., comma-separated string or JSON).
  - `url` (String, Nullable)
- **Relationship**: `user`: Many-to-one with `User`.

### `JobPreference` Model
- **Table Name**: `job_preferences`
- **Purpose**: Stores a user's job search preferences.
- **Fields**:
  - `id` (Integer, Primary Key)
  - `user_id` (Integer, Foreign Key to `users.id`, Unique)
  - `company_size` (String, Nullable)
  - `industry` (String, Nullable)
  - `job_titles` (Text, Nullable): Stores preferred job titles.
  - `locations` (Text, Nullable): Stores preferred locations.
  - `remote` (Boolean, Default: False)
- **Relationship**: `user`: One-to-one with `User`.

### `Skill` Model
- **Table Name**: `skills`
- **Purpose**: Stores individual skills for a user.
- **Fields**:
  - `id` (Integer, Primary Key)
  - `user_id` (Integer, Foreign Key to `users.id`)
  - `name` (String, Not Null)
  - `proficiency` (String, Nullable)
- **Relationship**: `user`: Many-to-one with `User`.

## Usage
These models are used throughout the application to interact with the database. They provide a structured way to define, query, and manipulate data, abstracting away raw SQL queries. They are typically used in conjunction with SQLAlchemy sessions (e.g., from `config.py`) to perform CRUD operations.