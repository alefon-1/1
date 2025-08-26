#!/bin/bash
# Production deployment script for DataScrape Pro

echo "🚀 Deploying DataScrape Pro - Revenue Generation Service"

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Initialize database
echo "🗄️ Initializing database..."
python3 -c "from app import init_db; init_db()"

# Start the service
echo "🌐 Starting DataScrape Pro service..."
echo "💰 Revenue target: $3,000 MRR in 6 months"
echo "🎯 Break-even target: $500 MRR in 3 months"

# In production, use gunicorn
if [ "$ENVIRONMENT" = "production" ]; then
    gunicorn -w 4 -b 0.0.0.0:5000 app:app
else
    python3 app.py
fi