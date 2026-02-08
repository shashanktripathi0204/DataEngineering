# Real-Time E-Commerce Order Processing Pipeline

## 1. Project Overview
Modern e-commerce businesses must maintain accurate, real-time inventory visibility across multiple sales channels — such as online stores, physical outlets, and supplier restocks.  
This project builds an **end-to-end real-time data pipeline** that ingests, processes, and stores order-related data to ensure consistent and reliable inventory tracking.

It demonstrates key data engineering concepts such as **stream processing, event-driven architecture, data modeling, batch orchestration, and cloud-readiness** — using fully open-source tools.

---

## 2. Objectives
- Build a **real-time streaming pipeline** using **Kafka** to process order events from multiple sources.
- Maintain an accurate **inventory database** that reflects all incoming events.
- Generate **daily batch reports** using **Airflow** for analytics and decision-making.
- Run the entire system locally via **Docker Compose**, with optional **cloud deployment** for production simulation.
- Follow **Object-Oriented Programming (OOP)** principles in Python to model producers, consumers, and data entities.

---

## 3. Business Use Case
A company sells products both online and in physical stores.  
They also receive restocks from multiple suppliers.  
All these activities affect product inventory in real-time.

The goal is to build a unified system that:
- Streams order, sale, and restock events into Kafka.
- Processes them to keep the inventory database consistent.
- Generates daily sales and low-stock reports for business insights.

---

## 4. System Architecture

### Components
| Component | Technology | Description |
|------------|-------------|--------------|
| **Producers** | Python + Kafka | Simulate multiple data sources: online orders, in-store sales, and supplier restocks. |
| **Kafka Broker** | Apache Kafka (Dockerized) | Acts as the real-time event backbone of the system. |
| **Stream Processor** | Python | Consumes Kafka messages, validates them, updates inventory in PostgreSQL, and emits processed events. |
| **Database** | PostgreSQL | Central relational database storing inventory, orders, and processed event logs. |
| **Scheduler (Batch Layer)** | Apache Airflow | Runs daily ETL/aggregation jobs to generate analytical reports. |
| **Storage (Optional Cloud)** | AWS S3 / GCP Cloud Storage | Stores daily reports and exports (optional for local demo). |
| **Containerization** | Docker & Docker Compose | Orchestrates all services locally for easy setup. |

---

## 5. Data Flow Overview
1. **Producers** emit simulated events → Kafka topics:
   - `online_orders`
   - `store_sales`
   - `supplier_restocks`
2. **Kafka Broker** stores and distributes the events.
3. **Consumer/Processor** reads events:
   - Validates data schema.
   - Deduplicates events using `event_id`.
   - Updates PostgreSQL inventory and writes audit logs.
   - Produces `inventory_updates` topic messages.
4. **Airflow DAG** runs daily:
   - Queries PostgreSQL.
   - Aggregates daily sales, top sellers, low-stock alerts.
   - Exports results as CSV/JSON files (local or cloud).

---

## 6. Kafka Topics
| Topic | Description |
|--------|--------------|
| `online_orders` | Events from website purchases. |
| `store_sales` | Events from in-store purchases. |
| `supplier_restocks` | Inventory restock events from suppliers. |
| `inventory_updates` | Processed/validated events confirming DB updates. |
| `dlq` | Dead-letter queue for failed or invalid messages. |

---

## 7. Database Schema (Conceptual)
| Table | Key Fields | Description |
|--------|-------------|-------------|
| `products` | product_id, name, category, price | Master product catalog. |
| `inventory` | product_id, quantity_on_hand, last_updated | Current inventory levels. |
| `orders` | order_id, product_id, quantity, source, timestamp | Order and sales transactions. |
| `suppliers` | supplier_id, name, contact | Supplier reference data. |
| `events_log` | event_id, raw_event, processed_at, status | Event tracking for auditing and replay. |
| `reports` | report_date, total_sales, top_sellers, low_stock | Daily batch summary table. |

---

## 8. Tech Stack
- **Language**: Python (OOP-based services)
- **Stream Processing**: Apache Kafka
- **Storage**: PostgreSQL
- **Orchestration**: Apache Airflow
- **Infrastructure**: Docker & Docker Compose
- **Cloud (optional)**: AWS / GCP / Azure (for database or report storage)
- **Monitoring (optional)**: Prometheus + Grafana
- **CI/CD (optional)**: GitHub Actions

---

## 9. Demo Flow (End-to-End)
1. Start all containers using `docker-compose up`.
2. Run producers to generate events (orders, sales, restocks).
3. Kafka streams data → Consumer updates DB in real-time.
4. Airflow DAG triggers → generates daily report CSV.
5. Reports can be viewed locally or uploaded to S3/GCS.

---

## 10. Deliverables
- **Local pipeline demo** (Dockerized)
- **Airflow DAGs** for daily reports
- **ER diagram & architecture diagram**
- **Unit/integration tests**
- **Optional cloud-deployed version**
- **Documentation** for setup, demo, and design decisions

---

## 11. Learning Outcomes
By completing this project, you’ll gain hands-on experience in:
- Designing and building real-time streaming systems.
- Integrating batch + streaming architectures.
- Implementing OOP patterns in data engineering.
- Working with Dockerized multi-service environments.
- Creating production-style pipelines ready for cloud deployment.