## Task 2.4: Define Ingestion Design (PostgreSQL)

**Discussion of Timestamp/CDC Strategy for PostgreSQL:**
Since pulling the entire support_tickets table every time is inefficient, we can use one of two incremental extraction strategies:

1. **Timestamp-Based Extraction (Query-Based):** 
   If the table has an updated_at column, the pipeline can save the maximum updated_at timestamp from the previous run as a watermark. On the next run, we simply execute a query like: 
   `SELECT * FROM support_tickets WHERE updated_at > 'last_watermark'`. 
   *Limitation:* This misses hard-deleted rows because the record is entirely gone from the table.

2. **Change Data Capture (CDC / Log-Based):**
   Instead of querying the table directly, we can read the PostgreSQL Write-Ahead Log. This captures every insert, update, and delete event in real-time. 
   *Advantage:* It is highly efficient, puts almost zero analytical load on the operational database, and perfectly captures deleted records.