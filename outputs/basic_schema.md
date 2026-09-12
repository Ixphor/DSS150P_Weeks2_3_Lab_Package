## Task 2.2: Basic Schemas

**Customers Logical Schema (customers.csv)**

| Field Name | Source Type | Logical Type | Nullability | Key Role | Semantic Definition |
| :--- | :--- | :--- | :--- | :--- | :--- |
| customer_id | String | UUID / String | Not Null | Candidate Key | Unique identifier for a customer. |
| first_name | String | String | Not Null | None | Customer's given name. |
| last_name | String | String | Not Null | None | Customer's family name. |
| email | String | String | Nullable | None | Customer's email address. |
| city | String | String | Nullable | None | Customer's city of residence. |
| signup_date | String | Date | Not Null | None | The date the customer registered. |
| customer_segment | String | Categorical | Not Null | None | Marketing classification for the customer. |

**API Events Logical Schema (REST API)**

| Field Name | Source Type | Logical Type | Nullability | Key Role | Semantic Definition |
| :--- | :--- | :--- | :--- | :--- | :--- |
| event_id | String | UUID / String | Not Null | Candidate Key | Unique identifier for the event transaction. |
| updated_at | String | Timestamp | Not Null | Watermark Key | The exact date and time the event was last modified. |
| amount | Float | Decimal / Float | Not Null | None | The numeric value or transaction amount of the event. |
| metadata | Object | JSON / Struct | Nullable | None | Nested dictionary containing flexible, event-specific details. |