I can’t safely “make this faster” from the provided context alone. What’s missing is the endpoint code, ORM/query layer, schema/indexes, sample large-account sizes, and any query timing/query count data.

The first fix should be measurement, not guessing. Add temporary profiling around the endpoint:

- total request time
- number of PostgreSQL queries
- duration of each query
- rows returned per query
- time spent building JSON in Python

Given the symptoms, the most likely regression is an N+1 query pattern, not Python loops. The target shape should be something like:

1. Fetch all projects for the account.
2. Fetch all tasks for those project IDs in one query.
3. Fetch all comments for those task IDs in one query.
4. Fetch all referenced users in one query.
5. Build lookup maps in Python: `project_id -> tasks`, `task_id -> comments`, `user_id -> user`.

That keeps the endpoint at roughly 4 database queries instead of growing with project/task/comment count.

Also verify indexes exist on the foreign keys used by those batched queries:

- `projects.account_id`
- `tasks.project_id`
- `comments.task_id`
- any user reference column used by comments/tasks

If profiling shows JSON assembly is the bottleneck after query batching, optimize the nested build with dictionaries/lists and avoid repeated scans. But don’t start there until query count and SQL timings are known.

To actually implement this, I need the report endpoint file, the database models/query code, and permission to edit the workspace.
