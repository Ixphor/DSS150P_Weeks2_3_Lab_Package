1. Why should source profiling occur before implementation of ingestion?
To discover anomalies, determine accurate data types, and understand the data volume. This prevents unexpected pipeline crashes and ensures you design an accurate schema and data contract from the start.

2. What is the difference between source event time/updated_at and ingestion time?
updated_at is the exact moment the data was created or modified in the source system. ingested_at is the moment your pipeline actually read and saved that data.

3. Why is event_id alone insufficient to decide which duplicate API record to keep in this exercise?
An event_id only tells you it is the same event, but not which version of the event is the newest. You must use updated_at to ensure you keep the most recent state and discard the older, outdated duplicates.

4. Why must watermark state advance only after successful persistence?
If you update the watermark first and the pipeline crashes before writing the data to disk, the pipeline will think it processed those records. On the next run, it will skip them entirely, resulting in permanent data loss.

5. What limitation does updated_after > watermark have when multiple source records can share exactly the same timestamp?
If your watermark is saved as 10:00:00, and a brand-new record arrives in the source system a minute later but is somehow stamped with that exact same 10:00:00 timestamp, a strict greater-than query will ignore it, causing data loss.

6. How is duplicate prevention related to idempotency?
Idempotency means running a pipeline 100 times produces the exact same final state as running it once. Duplicate prevention is the mechanism that makes idempotency possible.

7. Why should the raw area preserve source values instead of applying business transformations?
It provides a perfect historical audit trail. If a business transformation rule changes or has a bug, you can simply reprocess the raw data. If you transform data before landing it, the original state is lost forever.

8. How could querying a production OLTP source for profiling or extraction degrade the application?
Analytical queries often scan entire tables. This consumes massive amounts of CPU and memory, which can slow down or completely crash the live application for actual customers.

9. What would you change if the API had a rate limit of 60 requests per minute?
I would implement a rate-limiter or a simple sleep delay between pagination loops to pace the requests, alongside an exponential delay strategy if the pipeline receives a Too Many Requests error.

10. How would you extend this pipeline from a local raw area to PostgreSQL while preserving rerun safety?
Instead of writing to JSONL files, I would write to PostgreSQL using an UPSERT pattern (like INSERT ON CONFLICT DO UPDATE). This guarantees that rerunning the pipeline simply overwrites existing rows rather than creating duplicates.