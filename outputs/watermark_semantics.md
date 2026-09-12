## Task 2.5: Explain Watermark Semantics

**1. What could go wrong if the watermark is saved before the raw file is successfully written?**
If the pipeline updates the watermark state file first, but the raw file write fails (e.g., due to a disk space error or sudden crash), the pipeline "believes" it successfully processed those records. On the next run, it will use the advanced watermark and skip those records entirely, resulting in permanent data loss downstream.

**2. What could go wrong if the source allows multiple records with exactly the same timestamp?**
If the pipeline processes a batch of records and sets the watermark to `2026-09-12 10:00:00`, and seconds later the source system saves *more* records exactly at `2026-09-12 10:00:00`, those new records will be permanently missed. Because the next API call asks for records `> 2026-09-12 10:00:00`, anything sharing that exact boundary timestamp is skipped.

**3. Limitation and Production-Grade Mitigation:**
*   **Limitation:** This simplified `>` watermark strictly assumes that records always arrive in perfect chronological order and that timestamps are infinitely precise. It breaks down when transactions share the exact same millisecond or arrive slightly out-of-sequence.
*   **Mitigation:** Use an overlap window combined with downstream deduplication. Instead of querying `> watermark`, query `>= (watermark - 1 hour)`. This intentionally pulls a small amount of overlapping duplicate data to ensure nothing is missed, and the pipeline relies on code (like a MERGE statement or primary key constraint) to safely deduplicate the overlapping records in the database.