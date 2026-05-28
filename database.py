import duckdb
import os

DB_FILE = "medical_lakehouse.db"

def initialize_data_mart():
    """
    Forcefully drops old tables and rebuilds the Star Schema.
    """
    conn = duckdb.connect(DB_FILE)
    
    # 1. FORCE DROP OLD TABLES (Must drop Fact table first due to foreign keys)
    print("Wiping old schema...")
    conn.execute("DROP TABLE IF EXISTS fact_billing_discrepancy;")
    conn.execute("DROP TABLE IF EXISTS dim_cpt_code;")
    conn.execute("DROP TABLE IF EXISTS dim_hospital;")
    conn.execute("DROP TABLE IF EXISTS dim_date;")
    
    # 2. Rebuild Dimension Tables (With the new 'benchmark_rate' column)
    print("Building new schema...")
    conn.execute("""
        CREATE TABLE dim_hospital (
            hospital_id VARCHAR PRIMARY KEY,
            hospital_name VARCHAR,
            state VARCHAR
        );
        
        CREATE TABLE dim_cpt_code (
            cpt_code VARCHAR PRIMARY KEY,
            description VARCHAR,
            benchmark_rate FLOAT
        );
        
        CREATE TABLE dim_date (
            date_id DATE PRIMARY KEY,
            year INTEGER,
            month INTEGER
        );
    """)
    
    # 3. Rebuild Fact Table
    conn.execute("""
        CREATE TABLE fact_billing_discrepancy (
            billing_id VARCHAR PRIMARY KEY,
            hospital_id VARCHAR,
            cpt_code VARCHAR,
            date_id DATE,
            amount_billed FLOAT,
            discrepancy_amount FLOAT,
            FOREIGN KEY (hospital_id) REFERENCES dim_hospital(hospital_id),
            FOREIGN KEY (cpt_code) REFERENCES dim_cpt_code(cpt_code),
            FOREIGN KEY (date_id) REFERENCES dim_date(date_id)
        );
    """)
    
    # 4. Insert INR Reference Data
    conn.execute("""
        INSERT INTO dim_cpt_code VALUES 
        ('99214', 'Specialist Consultation (Complex)', 1500.00),
        ('80053', 'Comprehensive Metabolic Panel (Bloodwork)', 1200.00),
        ('71045', 'Chest X-Ray (Single View)', 800.00);
    """)
    
    print(f"[SUCCESS] Dimensional Data Mart forcefully rebuilt in {DB_FILE}")
    conn.close()

if __name__ == "__main__":
    initialize_data_mart()