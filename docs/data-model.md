# Data model

Draft. This describes the tables of Apprentice Clock: each column with its type and constraints. Types are PostgreSQL types.

## `users`

One row per person who uses the app.

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `uuid` | primary key | Not guessable, can be generated outside the database. |
| `first_name` | `text` | `NOT NULL` | |
| `last_name` | `text` | `NOT NULL` | |
| `email` | `text` | `NOT NULL`, `UNIQUE` | Used to log in. |
| `password_hash` | `text` | `NOT NULL` | Never the password itself, only a hash of it. |
| `created_at` | `timestamptz` | `NOT NULL` | Set when the row is created. |
| `updated_at` | `timestamptz` | `NOT NULL` | Changes every time the row is updated. |

### Why a password hash

The server never stores the password, only a hash of it. At login it hashes what the user typed and compares the two hashes. If the database leaks, attackers get hashes, not the passwords. A hash is one-way, so attackers can only guess and hash each guess. A slow, salted algorithm (bcrypt or argon2) makes that guessing expensive. The algorithm is chosen when login is built.

### Open points

- Decided: the application generates the `id` (`uuid4`) and sets `created_at` and `updated_at` (in UTC), like learnOS does. `updated_at` is set again by the ORM on every update. Rows inserted by hand in `psql` are not a use case, so no database defaults are needed. Consequence: a manual `UPDATE` in `psql` does not change `updated_at`.
- Decided: all timestamps use `timestamptz`, not `timestamp`. `timestamptz` stores a precise moment (converted to UTC), so it means the same thing in every time zone. A plain `timestamp` only stores the clock time without a zone, so it is unclear which moment it means. The same applies to `clock_in` and `clock_out`: hours worked is the difference between two moments, and with `timestamptz` that stays correct across time zones and summer time changes.
- Decided: emails are compared case-insensitively by lowercasing (and trimming whitespace) in the application before saving. Postgres does not do this itself, so every code path that saves an email must do it, otherwise the `UNIQUE` constraint would treat `Anna@example.com` and `anna@example.com` as different users.

### Possible later columns

- `email_confirmed_at` (`timestamptz`, nullable): when the address was confirmed. Planned as the second migration.

## `time_entries` (planned, not part of week 3)

One row per work session: one clock-in and, later, one clock-out with its daily report.

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `id` | `uuid` | primary key | |
| `user_id` | `uuid` | `NOT NULL`, foreign key to `users.id` with `ON DELETE RESTRICT` | Whose entry this is. |
| `clock_in` | `timestamptz` | `NOT NULL` | |
| `clock_out` | `timestamptz` | nullable | `NULL` while the entry is open. |
| `report` | `text` | nullable | `NULL` while the entry is open. |
| `created_at` | `timestamptz` | `NOT NULL` | Set when the row is created. |
| `updated_at` | `timestamptz` | `NOT NULL` | Changes every time the row is updated. |

### Why `created_at` and `updated_at` here

Hours worked are calculated from `clock_in` and `clock_out`, not from these two columns. They record when the row was created and last changed. They match the `users` table (and the shared mixin), and `updated_at` gives an audit trail if an entry is corrected later, for example to fix a forgotten clock-in.

### Rules

- One user has many entries (one-to-many). Each entry belongs to exactly one user.
- An entry can only be clocked out together with a report. The API enforces this.

### Open points

- Decided: the foreign key `user_id` uses `ON DELETE RESTRICT`. Entries must not vanish when a user is deleted, because the entries are the training log and must stay complete. With `RESTRICT`, Postgres refuses to delete a user who still has entries, so a wrong `DELETE` cannot wipe someone's hours and reports. `CASCADE` would delete the entries, and `SET NULL` does not work with `NOT NULL`.
- Idea for later: a soft delete (for example a `deleted_at` column on `users`) instead of really deleting users.
- Decided: no `CHECK` constraint for "clock-out requires a report" for now. `time_entries` is not built in week 3, and the API enforces the rule first. What counts as a valid report (for example a minimum length) is a product decision that belongs in the API. A `CHECK` constraint can be added later through a migration, as long as the existing data already follows the rule.
