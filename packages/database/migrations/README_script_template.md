# Alembic Migration Script Template (`script.py.mako`)

## Purpose
This Mako template file (`script.py.mako`) is used by Alembic to generate new migration scripts. It defines the standard structure for all database schema migration files that will be created in the `versions/` directory.

## Template Variables
- `${message}`: Migration description provided via `alembic revision -m`
- `${up_revision}`: Unique identifier for this migration
- `${down_revision}`: Identifier of previous migration (for rollback)
- `${create_date}`: Timestamp when migration was created
- `${imports}`: Additional imports needed for specific migrations
- `${upgrades}`: Schema upgrade operations
- `${downgrades}`: Schema downgrade operations

## Generated Migration Structure
```python
"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}

def upgrade():
    ${upgrades if upgrades else "pass"}

def downgrade():
    ${downgrades if downgrades else "pass"}
```

## Usage
1. Run `alembic revision -m "your message"` to generate new migration
2. Edit the generated file in `versions/` directory
3. Use `alembic upgrade head` to apply migrations

## Best Practices
- Keep migration messages clear and descriptive
- Test both upgrade and downgrade paths
- For complex migrations, consider splitting into multiple steps
- Document any data migration logic in the migration file

## Example Output
```python
"""Add user table

Revision ID: 4b100924591d
Revises: 
Create Date: 2023-10-27 10:00:00.000000
"""
from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('users')
```