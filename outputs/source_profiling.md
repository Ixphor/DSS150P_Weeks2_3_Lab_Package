# Source Profiling and Source-System Inspection

## Task 1.2: Profile customers.csv
* **File Size:** 18,183 bytes
* **Row Count:** 250
* **Column Count:** 7
* **Columns & Logical Types:** 
  * customer_id (String/UUID)
  * first_name (String)
  * last_name (String)
  * email (String)
  * city (String)
  * signup_date (Date/Timestamp)
  * customer_segment (String/Categorical)
* **Missing Values:** email (3), city (2)
* **Exact Duplicate Rows:** 2
* **Is customer_id unique?** False
* **Candidate Validation Rules:**
  1. customer_id must be unique and non-null.
  2. email (if present) must conform to a standard email format.
  3. signup_date must not be in the future.

## Task 1.3: Profile orders.json
* **Root Structure:** Confirmed it is a list of records (True).
* **Total Records:** 250
* **Top-Level Keys:** order_id, customer_id, order_timestamp, status, item_count, subtotal, shipping_fee, total_amount, shipping.
* **Nested Field:** shipping
* **Timestamp Fields:** order_timestamp, status 
* **Numeric Fields:** item_count, subtotal, shipping_fee, total_amount
* **Missing Keys/Nulls:** 0 missing keys or nulls across all fields.
* **Downstream Representations for the nested shipping object:**
  1. **Flattened columns:** Extracting nested fields as distinct columns into the same table
  2. **Normalized table:** Loading the nested dictionary into a separate related table  and joining it back via a foreign key.

## Task 1.4: Profile products.parquet
* **File Size:** 14,652 bytes
* **Shape:** 200 rows, 7 columns 
* **Data Types:** 
  * product_id            str
  * product_name          str
  * category              str
  * brand                 str
  * unit_price        float64
  * stock_quantity      int32
  * weight_kg         float64
* **Schema Behavior Comparison:** Unlike CSV or JSON, Parquet strictly enforces the schema and embeds the exact data types directly within the file metadata.
* **File Size/Preservation:** Parquet yields much smaller file sizes than plain text equivalents due to columnar compression, and it preserves complex data types natively.
* **Why it's not a common operational (OLTP) source:** Parquet is heavily optimized for analytical reads (OLAP) across entire columns. It is rarely used as an operational source format because appending single records or updating/deleting existing rows is computationally expensive and requires rewriting files.

## Task 1.5: Retrieve and inspect the REST API
* **Pagination Fields Identified:** page, per_page, total, has_more, next_page, items.
* **Incomplete Ingestion Explanation:** Processing only page 1 is incomplete because the payload structure (has_more: true, next_page, total) explicitly indicates that more records exist on subsequent pages. Stopping at page 1 effectively abandons the rest of the dataset and causes massive data loss in the ingestion pipeline.

## Task 1.6: Inspect PostgreSQL source table

```
dss150p=# \d support_tickets
     Column     |            Type             | Collation | Nullable | Default 
----------------+-----------------------------+-----------+----------+---------
 ticket_id      | integer                     |           | not null | 
 customer_id    | character varying(10)       |           | not null | 
 category       | character varying(40)       |           | not null | 
 priority       | character varying(10)       |           | not null | 
 assigned_agent | character varying(80)       |           |          | 
 opened_at      | timestamp without time zone |           | not null | 
 resolved_at    | timestamp without time zone |           |          | 
 status         | character varying(20)       |           | not null | 
Indexes:
    "support_tickets_pkey" PRIMARY KEY, btree (ticket_id)

dss150p=# SELECT COUNT(*) FROM support_tickets;
 count
-------
   250
(1 row)

dss150p=# SELECT * FROM support_tickets ORDER BY ticket_id LIMIT 10;
 ticket_id | customer_id | category  | priority | assigned_agent |      opened_at      |     resolved_at     |   status    
-----------+-------------+-----------+----------+----------------+---------------------+---------------------+-------------
         1 | C0246       | Technical | High     | J. Reyes       | 2026-06-19 04:00:00 | 2026-06-21 13:00:00 | Resolved
         2 | C0130       | Product   | Medium   | J. Reyes       | 2026-05-26 07:00:00 | 2026-05-26 23:00:00 | Closed
         3 | C0094       | Delivery  | Medium   | J. Reyes       | 2026-03-28 09:00:00 | 2026-03-31 17:00:00 | Closed
         4 | C0057       | Technical | High     | L. Tan         | 2026-04-25 19:00:00 |                     | In Progress
         5 | C0120       | Delivery  | High     | R. Cruz        | 2026-01-20 02:00:00 | 2026-01-22 21:00:00 | Resolved
         6 | C0211       | Product   | Medium   | P. Lim         | 2026-02-26 13:00:00 |                     | Open
         7 | C0041       | Delivery  | Low      | P. Lim         | 2026-03-11 23:00:00 |                     | Open
         8 | C0040       | Billing   | Low      | L. Tan         | 2026-02-14 05:00:00 | 2026-02-16 08:00:00 | Resolved
         9 | C0155       | Technical | Low      | R. Cruz        | 2026-02-09 04:00:00 | 2026-02-11 08:00:00 | Resolved
        10 | C0094       | Account   | Low      | J. Reyes       | 2026-04-12 19:00:00 |                     | In Progress
(10 rows)

dss150p=# SELECT COUNT(*) FROM support_tickets WHERE assigned_agent IS NULL;
 count 
-------
     4
(1 row)