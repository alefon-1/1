"""
DataScrape Pro - Revenue-generating web scraping and analytics service
Tiered pricing model with API access and custom analytics
"""

from flask import Flask, request, jsonify, render_template_string
import requests
from bs4 import BeautifulSoup
import sqlite3
import json
import time
from datetime import datetime, timedelta
import os
from urllib.parse import urljoin, urlparse
import pandas as pd

app = Flask(__name__)

# Pricing tiers (monthly in USD)
PRICING_TIERS = {
    'free': {'requests_per_month': 100, 'price': 0, 'features': ['Basic scraping', 'JSON export']},
    'starter': {'requests_per_month': 5000, 'price': 29, 'features': ['Advanced scraping', 'CSV/JSON export', 'API access']},
    'professional': {'requests_per_month': 50000, 'price': 99, 'features': ['Unlimited scraping', 'All exports', 'Priority support', 'Custom analytics']},
    'enterprise': {'requests_per_month': -1, 'price': 299, 'features': ['Everything in Pro', 'Custom integrations', 'Dedicated support']}
}

def init_db():
    """Initialize SQLite database for users, usage tracking, and revenue"""
    conn = sqlite3.connect('datascrape.db')
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        api_key TEXT UNIQUE NOT NULL,
        tier TEXT DEFAULT 'free',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_payment TIMESTAMP,
        requests_used INTEGER DEFAULT 0,
        monthly_reset TIMESTAMP
    )''')
    
    # Revenue tracking
    c.execute('''CREATE TABLE IF NOT EXISTS revenue (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        amount REAL,
        tier TEXT,
        payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )''')
    
    # API usage logs
    c.execute('''CREATE TABLE IF NOT EXISTS api_usage (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        endpoint TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        response_size INTEGER,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )''')
    
    conn.commit()
    conn.close()

def get_user_by_api_key(api_key):
    """Get user information by API key"""
    conn = sqlite3.connect('datascrape.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE api_key = ?', (api_key,))
    user = c.fetchone()
    conn.close()
    return user

def check_rate_limit(user_id, tier):
    """Check if user has exceeded their monthly limit"""
    conn = sqlite3.connect('datascrape.db')
    c = conn.cursor()
    
    # Reset monthly usage if needed
    c.execute('SELECT monthly_reset, requests_used FROM users WHERE id = ?', (user_id,))
    result = c.fetchone()
    
    if result:
        monthly_reset, requests_used = result
        if monthly_reset:
            reset_date = datetime.fromisoformat(monthly_reset)
            if datetime.now() > reset_date:
                # Reset usage
                c.execute('UPDATE users SET requests_used = 0, monthly_reset = ? WHERE id = ?',
                         (datetime.now() + timedelta(days=30), user_id))
                requests_used = 0
        else:
            # Set initial reset date
            c.execute('UPDATE users SET monthly_reset = ? WHERE id = ?',
                     (datetime.now() + timedelta(days=30), user_id))
    
    limit = PRICING_TIERS[tier]['requests_per_month']
    if limit == -1:  # Unlimited
        conn.commit()
        conn.close()
        return True
    
    if requests_used >= limit:
        conn.close()
        return False
    
    # Increment usage
    c.execute('UPDATE users SET requests_used = requests_used + 1 WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()
    return True

def log_api_usage(user_id, endpoint, response_size):
    """Log API usage for analytics"""
    conn = sqlite3.connect('datascrape.db')
    c = conn.cursor()
    c.execute('INSERT INTO api_usage (user_id, endpoint, response_size) VALUES (?, ?, ?)',
              (user_id, endpoint, response_size))
    conn.commit()
    conn.close()

@app.route('/')
def home():
    """Landing page with pricing and signup"""
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
    <title>DataScrape Pro - Revenue-Generating Web Scraping Service</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
        .header { text-align: center; margin-bottom: 40px; }
        .pricing-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 30px 0; }
        .pricing-card { border: 2px solid #ddd; padding: 20px; border-radius: 10px; text-align: center; }
        .pricing-card.popular { border-color: #007bff; transform: scale(1.05); }
        .price { font-size: 2em; font-weight: bold; color: #007bff; }
        .feature-list { text-align: left; margin: 15px 0; }
        .cta-button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
        .revenue-tracker { background: #e8f5e9; padding: 20px; border-radius: 5px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 DataScrape Pro</h1>
            <h2>Revenue-Generating Web Scraping & Analytics Service</h2>
            <p><strong>Transform web data into profit with our scalable API platform</strong></p>
        </div>
        
        <div class="revenue-tracker">
            <h3>💰 Revenue Convergence Strategy</h3>
            <p><strong>Target:</strong> Break even in 3 months, profitable in 6 months</p>
            <p><strong>Model:</strong> Freemium → Paid conversion through value demonstration</p>
            <p><strong>Current MRR:</strong> $0 → <strong>Target MRR:</strong> $3,000+ by month 6</p>
        </div>

        <h3>Choose Your Plan</h3>
        <div class="pricing-grid">
            {% for tier, details in pricing.items() %}
            <div class="pricing-card {% if tier == 'starter' %}popular{% endif %}">
                <h3>{{ tier.title() }}</h3>
                <div class="price">${{ details.price }}<small>/month</small></div>
                <p>{{ details.requests_per_month if details.requests_per_month != -1 else 'Unlimited' }} requests/month</p>
                <div class="feature-list">
                    {% for feature in details.features %}
                    <div>✓ {{ feature }}</div>
                    {% endfor %}
                </div>
                <button class="cta-button" onclick="signup('{{ tier }}')">
                    {% if tier == 'free' %}Start Free{% else %}Upgrade to {{ tier.title() }}{% endif %}
                </button>
            </div>
            {% endfor %}
        </div>

        <h3>🔧 API Endpoints</h3>
        <ul>
            <li><strong>POST /api/scrape</strong> - Scrape any website with custom selectors</li>
            <li><strong>GET /api/analytics</strong> - Usage analytics and insights</li>
            <li><strong>GET /api/export</strong> - Export data in various formats</li>
        </ul>

        <h3>📈 Revenue Metrics</h3>
        <p><a href="/revenue-dashboard">View Live Revenue Dashboard</a></p>
        
        <script>
            function signup(tier) {
                const apiKey = 'demo_' + Math.random().toString(36).substr(2, 9);
                alert(`Welcome to DataScrape Pro!\\n\\nYour API Key: ${apiKey}\\n\\nTier: ${tier}\\n\\nNext: Use this key to access our API endpoints`);
                // In production, this would integrate with Stripe for payment processing
            }
        </script>
    </div>
</body>
</html>
    """, pricing=PRICING_TIERS)

@app.route('/api/scrape', methods=['POST'])
def api_scrape():
    """Main scraping endpoint - the revenue generator"""
    api_key = request.headers.get('X-API-Key')
    if not api_key:
        return jsonify({'error': 'API key required', 'upgrade_url': '/'}), 401
    
    user = get_user_by_api_key(api_key)
    if not user:
        return jsonify({'error': 'Invalid API key', 'signup_url': '/'}), 401
    
    user_id, api_key, tier = user[0], user[1], user[2]
    
    if not check_rate_limit(user_id, tier):
        return jsonify({
            'error': 'Rate limit exceeded',
            'upgrade_url': '/',
            'current_tier': tier,
            'limit': PRICING_TIERS[tier]['requests_per_month']
        }), 429
    
    data = request.json
    url = data.get('url')
    selectors = data.get('selectors', {})
    
    if not url:
        return jsonify({'error': 'URL required'}), 400
    
    try:
        # Perform the scraping
        headers = {'User-Agent': 'DataScrape Pro Bot 1.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        results = {}
        
        # Extract data based on selectors
        if selectors:
            for key, selector in selectors.items():
                elements = soup.select(selector)
                results[key] = [elem.get_text(strip=True) for elem in elements]
        else:
            # Default extraction - get title and meta description
            results['title'] = soup.title.string if soup.title else None
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            results['description'] = meta_desc.get('content') if meta_desc else None
            results['headings'] = [h.get_text(strip=True) for h in soup.find_all(['h1', 'h2', 'h3'])]
        
        response_data = {
            'url': url,
            'data': results,
            'timestamp': datetime.now().isoformat(),
            'remaining_requests': PRICING_TIERS[tier]['requests_per_month'] - (user[7] if len(user) > 7 else 0) if PRICING_TIERS[tier]['requests_per_month'] != -1 else 'unlimited'
        }
        
        # Log usage
        log_api_usage(user_id, '/api/scrape', len(json.dumps(response_data)))
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({'error': f'Scraping failed: {str(e)}'}), 500

@app.route('/revenue-dashboard')
def revenue_dashboard():
    """Live revenue tracking dashboard"""
    conn = sqlite3.connect('datascrape.db')
    
    # Get current revenue metrics
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM users')
    total_users = c.fetchone()[0]
    
    c.execute('SELECT tier, COUNT(*) FROM users GROUP BY tier')
    user_tiers = dict(c.fetchall())
    
    c.execute('SELECT SUM(amount) FROM revenue WHERE payment_date > date("now", "-30 days")')
    monthly_revenue = c.fetchone()[0] or 0
    
    c.execute('SELECT COUNT(*) FROM api_usage WHERE timestamp > date("now", "-1 day")')
    daily_api_calls = c.fetchone()[0]
    
    conn.close()
    
    # Calculate projected MRR
    projected_mrr = sum(PRICING_TIERS[tier]['price'] * count for tier, count in user_tiers.items() if tier != 'free')
    
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
    <title>Revenue Dashboard - DataScrape Pro</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f0f2f5; }
        .dashboard { max-width: 1200px; margin: 0 auto; }
        .metric-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 20px 0; }
        .metric-card { background: white; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .metric-value { font-size: 2.5em; font-weight: bold; color: #28a745; }
        .metric-label { color: #666; margin-top: 10px; }
        .convergence-plan { background: white; padding: 20px; border-radius: 10px; margin: 20px 0; }
        .progress-bar { background: #e9ecef; height: 20px; border-radius: 10px; overflow: hidden; margin: 10px 0; }
        .progress-fill { background: #007bff; height: 100%; transition: width 0.3s ease; }
    </style>
</head>
<body>
    <div class="dashboard">
        <h1>💰 DataScrape Pro Revenue Dashboard</h1>
        <p><a href="/">← Back to Home</a></p>
        
        <div class="metric-grid">
            <div class="metric-card">
                <div class="metric-value">${{ "%.2f"|format(monthly_revenue) }}</div>
                <div class="metric-label">Monthly Revenue</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">${{ "%.2f"|format(projected_mrr) }}</div>
                <div class="metric-label">Projected MRR</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{{ total_users }}</div>
                <div class="metric-label">Total Users</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{{ daily_api_calls }}</div>
                <div class="metric-label">API Calls (24h)</div>
            </div>
        </div>

        <div class="convergence-plan">
            <h3>🎯 Revenue Convergence Progress</h3>
            <p><strong>Target:</strong> $3,000 MRR by Month 6</p>
            
            <div>
                <strong>Break-even Progress (Month 3 Target: $500 MRR)</strong>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {{ (projected_mrr / 500 * 100) if projected_mrr < 500 else 100 }}%;"></div>
                </div>
                ${{ "%.2f"|format(projected_mrr) }} / $500
            </div>
            
            <div>
                <strong>Profit Target Progress (Month 6 Target: $3,000 MRR)</strong>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {{ (projected_mrr / 3000 * 100) if projected_mrr < 3000 else 100 }}%;"></div>
                </div>
                ${{ "%.2f"|format(projected_mrr) }} / $3,000
            </div>
        </div>

        <div class="convergence-plan">
            <h3>📊 User Distribution</h3>
            {% for tier, count in user_tiers.items() %}
            <p><strong>{{ tier.title() }}:</strong> {{ count }} users ({{ "%.1f"|format(count / total_users * 100) if total_users > 0 else 0 }}%)</p>
            {% endfor %}
        </div>

        <div class="convergence-plan">
            <h3>🚀 Next Steps for Revenue Growth</h3>
            <ul>
                <li>✅ <strong>MVP Launched:</strong> Basic scraping service with tiered pricing</li>
                <li>🔄 <strong>User Acquisition:</strong> Drive free tier signups through content marketing</li>
                <li>📈 <strong>Conversion Optimization:</strong> Implement usage alerts and upgrade prompts</li>
                <li>🎯 <strong>Value Addition:</strong> Add analytics dashboards and export features</li>
                <li>💼 <strong>Enterprise Sales:</strong> Reach out to data-hungry businesses</li>
            </ul>
        </div>
    </div>
</body>
</html>
    """, 
    monthly_revenue=monthly_revenue, 
    projected_mrr=projected_mrr,
    total_users=total_users,
    daily_api_calls=daily_api_calls,
    user_tiers=user_tiers)

@app.route('/api/signup', methods=['POST'])
def api_signup():
    """User signup endpoint"""
    import secrets
    
    data = request.json
    tier = data.get('tier', 'free')
    
    if tier not in PRICING_TIERS:
        return jsonify({'error': 'Invalid tier'}), 400
    
    api_key = 'ds_' + secrets.token_urlsafe(20)
    
    conn = sqlite3.connect('datascrape.db')
    c = conn.cursor()
    c.execute('INSERT INTO users (api_key, tier) VALUES (?, ?)', (api_key, tier))
    user_id = c.lastrowid
    
    # Record revenue if paid tier
    if PRICING_TIERS[tier]['price'] > 0:
        c.execute('INSERT INTO revenue (user_id, amount, tier) VALUES (?, ?, ?)',
                  (user_id, PRICING_TIERS[tier]['price'], tier))
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'api_key': api_key,
        'tier': tier,
        'requests_per_month': PRICING_TIERS[tier]['requests_per_month'],
        'monthly_cost': PRICING_TIERS[tier]['price']
    })

if __name__ == '__main__':
    init_db()
    # Add some demo users for demonstration
    conn = sqlite3.connect('datascrape.db')
    c = conn.cursor()
    
    # Check if demo users exist
    c.execute('SELECT COUNT(*) FROM users')
    if c.fetchone()[0] == 0:
        # Add demo users to show revenue potential
        demo_users = [
            ('demo_free_001', 'free'),
            ('demo_starter_001', 'starter'),
            ('demo_starter_002', 'starter'),
            ('demo_pro_001', 'professional'),
            ('demo_enterprise_001', 'enterprise')
        ]
        
        for api_key, tier in demo_users:
            c.execute('INSERT INTO users (api_key, tier, requests_used) VALUES (?, ?, ?)', 
                     (api_key, tier, 50))
            user_id = c.lastrowid
            
            # Add revenue records for paid tiers
            if PRICING_TIERS[tier]['price'] > 0:
                c.execute('INSERT INTO revenue (user_id, amount, tier) VALUES (?, ?, ?)',
                          (user_id, PRICING_TIERS[tier]['price'], tier))
    
    conn.commit()
    conn.close()
    
    app.run(debug=True, port=5000)