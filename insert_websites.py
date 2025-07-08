# insert_websites.py
import psycopg2
from crawler import DB_CONFIG

def insert_websites(websites):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    for site in websites:
        site = site.strip()
        if site == "":
            continue
        # Check if already exists
        cur.execute("SELECT 1 FROM crawled_data WHERE website = %s", (site,))
        if cur.fetchone():
            print(f"Already exists: {site}")
            continue

        cur.execute("""
            INSERT INTO crawled_data (website, crawl_status)
            VALUES (%s, 0)
        """, (site,))
        print(f"Inserted: {site}")

    conn.commit()
    cur.close()
    conn.close()
