# crawler.py
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse
import psycopg2
import json

DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'user': 'postgres',
    'password': 'password',
    'dbname': 'crud_nestjs'
}

EMAIL_REGEX = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
PHONE_REGEX = r'''(?x)
(?:\+?\d{1,3})?[\s\-\.]?\(?\d{2,5}\)?(?:[\s\-\.]?\d{2,5}){1,3}
'''

def clean_phones(phone_matches):
    cleaned = set()
    for number in phone_matches:
        number = re.sub(r'[^\d+]', '', number)
        if number.startswith("+91") and 10 <= len(number) <= 15:
            cleaned.add(number)
        if len(cleaned) >= 2:
            break
    return cleaned

def extract_contacts(html):
    emails = re.findall(EMAIL_REGEX, html)
    phones_raw = re.findall(PHONE_REGEX, html)
    phones = clean_phones(phones_raw)
    return set(emails), phones

def is_internal(url, base):
    return urlparse(url).netloc == urlparse(base).netloc

def crawl_website(base_url, max_depth=2):
    visited_urls = set()
    contacts = {"emails": set(), "phones": set()}

    def crawl(url, depth):
        if depth > max_depth or url in visited_urls:
            return
        visited_urls.add(url)

        try:
            response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            if not response.ok or 'text/html' not in response.headers.get('Content-Type', ''):
                return
        except:
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        emails, phones = extract_contacts(response.text)

        contacts["emails"].update(emails)
        if len(contacts["phones"]) < 2:
            contacts["phones"].update(phones)

        for link in soup.find_all('a', href=True):
            next_url = urljoin(url, link['href'])
            if is_internal(next_url, base_url):
                crawl(next_url, depth + 1)

    crawl(base_url, 0)
    return contacts

def crawl_pending_websites():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("SELECT id, website FROM crawled_data WHERE crawl_status = 0 LIMIT 1")
    rows = cur.fetchall()

    for id, website in rows:
        result = crawl_website(website)
        emails = json.dumps(list(result['emails']))
        phones = json.dumps(list(result['phones']))

        cur.execute("""
            UPDATE crawled_data 
            SET email_array = %s, phone_array = %s, crawl_status = 1 
            WHERE id = %s
        """, (emails, phones, id))
        print(f"Crawled: {website}")

    conn.commit()
    cur.close()
    conn.close()
