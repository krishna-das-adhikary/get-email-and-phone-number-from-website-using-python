# app.py Preeti
from flask import Flask, render_template, redirect, url_for, request, flash
import psycopg2
import psycopg2.extras
import json
from crawler import crawl_pending_websites, DB_CONFIG
from insert_websites import insert_websites

app = Flask(__name__)
app.secret_key = 'your-secret-key'

# Custom Jinja filter to parse JSON safely
@app.template_filter('from_json')
def from_json_filter(s):
    try:
        return json.loads(s)
    except Exception:
        return []

@app.route('/')
def index():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("""
        SELECT id, website, email_array, phone_array, crawl_status, send_email_status, send_whatsapp_status, created_at 
        FROM crawled_data 
        ORDER BY created_at ASC
    """)
    data = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html', data=data)

@app.route('/crawl')
def crawl_now():
    crawl_pending_websites()
    return redirect(url_for('index'))

@app.route('/add-websites', methods=['GET', 'POST'])
def add_websites():
    if request.method == 'POST':
        text = request.form.get('websites', '')
        # Split by newlines and commas to be flexible
        sites = [line.strip() for line in text.splitlines() if line.strip()]
        insert_websites(sites)
        flash(f'Successfully inserted {len(sites)} websites.', 'success')
        return redirect(url_for('add_websites'))

    return render_template('add_websites.html')

if __name__ == '__main__':
    app.run(debug=True)
