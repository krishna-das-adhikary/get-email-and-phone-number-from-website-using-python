import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse

# Global visited set
visited_urls = set()

# Regex patterns
EMAIL_REGEX = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
PHONE_REGEX = r'''(?x)
(?:\+?\d{1,3})?                           # country code
[\s\-\.]?\(?\d{2,5}\)?                   # area code
(?:[\s\-\.]?\d{2,5}){1,3}                # phone blocks
'''

# Clean phone numbers
def clean_phones(phone_matches):
    cleaned = set()
    for number in phone_matches:
        number = re.sub(r'[^\d+]', '', number)  # digits and + only
        if number.startswith("+91") and 10 <= len(number) <= 15:
            cleaned.add(number)
        # stop if we already have 2
        if len(cleaned) >= 2:
            break
    return cleaned

# Extract emails and phones from raw HTML
def extract_contacts(html):
    emails = re.findall(EMAIL_REGEX, html)
    phones_raw = re.findall(PHONE_REGEX, html)
    phones = clean_phones(phones_raw)
    return set(emails), phones

# Check if a URL is internal
def is_internal(url, base):
    return urlparse(url).netloc == urlparse(base).netloc

# Recursive web crawler
def crawl_website(base_url, max_depth=2):
    contacts = {
        "emails": set(),
        "phones": set()
    }

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
            for phone in phones:
                contacts["phones"].add(phone)
                if len(contacts["phones"]) == 2:
                    break

        for link in soup.find_all('a', href=True):
            next_url = urljoin(url, link['href'])
            if is_internal(next_url, base_url):
                crawl(next_url, depth + 1)

    crawl(base_url, 0)
    return contacts

# ---------------- Main Script ---------------- #

websites = [
    # 'https://www.sparity.com/',
    'https://www.ibaseit.com/',
    # Add more websites here
]

for site in websites:
    print(f'Crawling: {site}')
    visited_urls.clear()
    data = crawl_website(site)
    print(f"Emails: {data['emails']}")
    print(f"Phones: {data['phones']}")
    print('-' * 60)
