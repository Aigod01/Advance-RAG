"""
Seed script to populate realistic non-sensitive corporate data for Multi-Agent RAG.
Covers: companies, products, customers, regions, and multi-quarter sales records.
"""
import random
from datetime import date, timedelta
from sqlalchemy.orm import Session
from backend.database.postgres import db_manager
from backend.database.models import Company, Region, Product, Customer, Sale


def seed_database():
    """Seeds tables with realistic corporate enterprise data."""
    db_manager.init_db()
    session = db_manager.SessionLocal()

    try:
        # Check if already seeded
        if session.query(Company).first():
            print("Database already contains data. Skipping seed.")
            return

        print("Seeding database with enterprise business data...")

        # 1. Company
        company = Company(
            id=1,
            name="Apex Technologies Global",
            industry="Consumer Electronics & Enterprise Hardware",
            ticker="APEX",
        )
        session.add(company)

        # 2. Regions
        regions_data = [
            Region(id=1, name="North America"),
            Region(id=2, name="EMEA"),
            Region(id=3, name="APAC"),
            Region(id=4, name="Latin America"),
        ]
        session.add_all(regions_data)

        # 3. Products
        products_data = [
            # Laptops
            Product(id=1, name="ApexBook Pro 16", category="Laptops", unit_price=2499.0),
            Product(id=2, name="ApexBook Air 14", category="Laptops", unit_price=1299.0),
            Product(id=3, name="ApexBook Ultra 13", category="Laptops", unit_price=999.0),
            Product(id=4, name="ApexStudio Max 16", category="Laptops", unit_price=3199.0),
            # Desktops
            Product(id=5, name="ApexStation Pro", category="Desktops", unit_price=1899.0),
            Product(id=6, name="ApexMini Workstation", category="Desktops", unit_price=899.0),
            # Tablets & Accessories
            Product(id=7, name="ApexPad Pro 11", category="Tablets", unit_price=799.0),
            Product(id=8, name="ApexPad Air", category="Tablets", unit_price=549.0),
            Product(id=9, name="ApexDisplay 4K HDR", category="Accessories", unit_price=699.0),
            Product(id=10, name="ApexDock Pro Thunderbolt", category="Accessories", unit_price=249.0),
        ]
        session.add_all(products_data)

        # 4. Customers
        customer_names = [
            ("CyberDyne Systems", "North America", 1, "Enterprise"),
            ("Wayne Enterprises", "North America", 1, "Enterprise"),
            ("Stark Industries", "North America", 1, "Enterprise"),
            ("Acme Corporation", "North America", 1, "SMB"),
            ("Hooli Global", "North America", 1, "Enterprise"),
            ("Globex Corp", "EMEA", 2, "Enterprise"),
            ("Initech Solutions", "EMEA", 2, "SMB"),
            ("Massive Dynamic", "EMEA", 2, "Enterprise"),
            ("Omni Consumer Products", "EMEA", 2, "Enterprise"),
            ("Nakatomi Trading", "APAC", 3, "Enterprise"),
            ("Tetsuo Dynamics", "APAC", 3, "SMB"),
            ("Shinra Electric", "APAC", 3, "Enterprise"),
            ("Vandelay Industries", "Latin America", 4, "SMB"),
            ("Soylent Logistics", "Latin America", 4, "Enterprise"),
            ("Tyrell BioTech", "APAC", 3, "Enterprise"),
        ]
        customers = []
        for i, (cname, rname, rid, segment) in enumerate(customer_names, start=1):
            customers.append(
                Customer(id=i, name=cname, region=rname, region_id=rid, segment=segment)
            )
        session.add_all(customers)
        session.commit()

        # 5. Sales Data generation across quarters:
        # 2025 Q1 (Jan-Mar), 2025 Q2 (Apr-Jun), 2025 Q3 (Jul-Sep - Laptop slump), 2025 Q4 (Oct-Dec), 2026 Q1, 2026 Q2
        random.seed(42)
        sales_records = []
        sale_id = 1

        start_date = date(2025, 1, 1)
        end_date = date(2026, 7, 1)
        current_date = start_date

        laptop_pids = [1, 2, 3, 4]
        other_pids = [5, 6, 7, 8, 9, 10]

        prod_map = {p.id: p for p in products_data}

        while current_date < end_date:
            month = current_date.month
            year = current_date.year

            # Determine quarter
            quarter = (month - 1) // 3 + 1

            # Number of sales per day: between 2 and 6
            num_sales_today = random.randint(2, 5)

            for _ in range(num_sales_today):
                # Choose product category
                if random.random() < 0.65:
                    pid = random.choice(laptop_pids)
                    prod = prod_map[pid]

                    # Specifically create the Q3 2025 slump in laptop sales:
                    # In Q2 2025: high quantity (5-15 units per order)
                    # In Q3 2025: drop in quantity & volume due to component shortage and delayed Enterprise refresh cycles
                    if year == 2025 and quarter == 3:
                        qty = random.randint(1, 4)
                        discount = 0.05
                    elif year == 2025 and quarter == 2:
                        qty = random.randint(4, 14)
                        discount = 0.0
                    elif year == 2025 and quarter == 4:
                        qty = random.randint(3, 8)
                        discount = 0.08
                    else:
                        qty = random.randint(2, 9)
                        discount = 0.02
                else:
                    pid = random.choice(other_pids)
                    prod = prod_map[pid]
                    qty = random.randint(2, 10)
                    discount = 0.0

                cid = random.randint(1, len(customers))
                sale = Sale(
                    id=sale_id,
                    product_id=pid,
                    customer_id=cid,
                    company_id=1,
                    sale_date=current_date,
                    quantity=qty,
                    unit_price=prod.unit_price,
                    discount=discount,
                )
                sales_records.append(sale)
                sale_id += 1

            current_date += timedelta(days=1)

        session.add_all(sales_records)
        session.commit()
        print(f"Successfully seeded {len(sales_records)} sales records into database.")

    except Exception as e:
        session.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    seed_database()
