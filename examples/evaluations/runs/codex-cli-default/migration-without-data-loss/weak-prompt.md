You are completing a software-engineering task. Use only the context below.
If the task is underspecified, say what is missing instead of inventing facts.
Keep the answer under 450 words.

TASK CONTEXT:
A production PostgreSQL `users` table has `birthdate_text VARCHAR`. Values include `1990-04-12`, `04/12/1990`, `unknown`, empty strings, and nulls. The app has old and new versions live during deploy. The table has 40 million rows and receives writes all day.

USER REQUEST:
Migrate users.birthdate from string to date.
