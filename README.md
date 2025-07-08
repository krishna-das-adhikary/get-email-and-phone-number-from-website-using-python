# get-email-and-phone-number-from-website-using-python
get email and phone number from website using python


# Web Scraper

A simple web scraper using Python, BeautifulSoup, and pandas.

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt


CREATE TABLE crawled_data (
    id SERIAL PRIMARY KEY,
    website TEXT NOT NULL,
    email_array TEXT,
    phone_array TEXT,
    crawl_status INTEGER DEFAULT 0,
    send_email_status INTEGER DEFAULT 0,
    send_whatsapp_status INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
