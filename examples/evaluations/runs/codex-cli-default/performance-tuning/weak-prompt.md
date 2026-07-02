You are completing a software-engineering task. Use only the context below.
If the task is underspecified, say what is missing instead of inventing facts.
Keep the answer under 450 words.

TASK CONTEXT:
A report endpoint now takes 9 seconds for large accounts. It fetches projects, tasks, comments, and users from PostgreSQL, then builds a nested JSON response. There is no profile yet. The team suspects Python loops, but database query count may have changed.

USER REQUEST:
Make this faster.
