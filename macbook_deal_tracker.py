#!/usr/bin/env python3
"""
eBay MacBook Deal Tracker
Scrapes eBay for refurbished MacBooks and sends email alerts for best deals
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import os
from datetime import datetime, timedelta
import time
import random
import re
from dotenv import load_dotenv
import schedule
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('macbook_tracker.log'),
        logging.StreamHandler()
    ]
)

class MacBookDealTracker:
    def __init__(self):
        self.base_url = "https://www.ebay.com/sch/i.html"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.deals_file = 'macbook_deals.json'
        self.email_config = {
            'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
            'smtp_port': int(os.getenv('SMTP_PORT', '587')),
            'email': os.getenv('EMAIL_ADDRESS'),
            'password': os.getenv('EMAIL_PASSWORD'),
            'recipient': os.getenv('RECIPIENT_EMAIL')
        }
        
    def search_macbooks(self, search_term="refurbished macbook", max_pages=3):
        """Search eBay for refurbished MacBooks"""
        all_listings = []
        
        for page in range(1, max_pages + 1):
            params = {
                '_nkw': search_term,
                '_sacat': '0',
                'rt': 'nc',
                'LH_ItemCondition': '2000',  # Used condition
                'LH_BIN': '1',  # Buy It Now only
                '_pgn': page,
                '_skc': '50'  # 50 items per page
            }
            
            try:
                response = requests.get(self.base_url, params=params, headers=self.headers)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                
                listings = self.parse_listings(soup)
                all_listings.extend(listings)
                
                # Add delay to be respectful
                time.sleep(random.uniform(1, 3))
                
            except requests.RequestException as e:
                logging.error(f"Error fetching page {page}: {e}")
                continue
                
        return all_listings
    
    def parse_listings(self, soup):
        """Parse eBay listings from HTML"""
        listings = []
        items = soup.find_all('div', class_='s-item')
        
        for item in items:
            try:
                # Skip ads and sponsored listings
                if item.find('span', class_='SPONSORED'):
                    continue
                    
                title_elem = item.find('h3', class_='s-item__title')
                price_elem = item.find('span', class_='s-item__price')
                link_elem = item.find('a', class_='s-item__link')
                shipping_elem = item.find('span', class_='s-item__shipping')
                location_elem = item.find('span', class_='s-item__location')
                
                if not all([title_elem, price_elem, link_elem]):
                    continue
                
                title = title_elem.get_text(strip=True)
                price_text = price_elem.get_text(strip=True)
                link = link_elem['href']
                
                # Extract numeric price
                price_match = re.search(r'\$?(\d+(?:,\d+)?(?:\.\d{2})?)', price_text)
                if not price_match:
                    continue
                    
                price = float(price_match.group(1).replace(',', ''))
                
                # Extract MacBook model and specifications
                model_info = self.extract_model_info(title)
                
                listing = {
                    'title': title,
                    'price': price,
                    'link': link,
                    'shipping': shipping_elem.get_text(strip=True) if shipping_elem else 'N/A',
                    'location': location_elem.get_text(strip=True) if location_elem else 'N/A',
                    'model': model_info['model'],
                    'year': model_info['year'],
                    'screen_size': model_info['screen_size'],
                    'memory': model_info['memory'],
                    'storage': model_info['storage'],
                    'found_date': datetime.now().isoformat()
                }
                
                listings.append(listing)
                
            except Exception as e:
                logging.error(f"Error parsing listing: {e}")
                continue
                
        return listings
    
    def extract_model_info(self, title):
        """Extract MacBook model information from title"""
        title_lower = title.lower()
        
        # Extract model
        model = 'Unknown'
        if 'macbook pro' in title_lower:
            model = 'MacBook Pro'
        elif 'macbook air' in title_lower:
            model = 'MacBook Air'
        elif 'macbook' in title_lower:
            model = 'MacBook'
            
        # Extract year
        year_match = re.search(r'(20\d{2})', title)
        year = int(year_match.group(1)) if year_match else 0
        
        # Extract screen size
        screen_match = re.search(r'(\d{2})"', title)
        screen_size = int(screen_match.group(1)) if screen_match else 0
        
        # Extract memory (RAM)
        memory_match = re.search(r'(\d+)GB.*RAM|(\d+)GB.*Memory', title, re.IGNORECASE)
        memory = int(memory_match.group(1) or memory_match.group(2)) if memory_match else 0
        
        # Extract storage
        storage_match = re.search(r'(\d+)GB.*SSD|(\d+)TB.*SSD', title, re.IGNORECASE)
        storage = 0
        if storage_match:
            if storage_match.group(1):
                storage = int(storage_match.group(1))
            elif storage_match.group(2):
                storage = int(storage_match.group(2)) * 1024
        
        return {
            'model': model,
            'year': year,
            'screen_size': screen_size,
            'memory': memory,
            'storage': storage
        }
    
    def load_previous_deals(self):
        """Load previously found deals from file"""
        if os.path.exists(self.deals_file):
            try:
                with open(self.deals_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return []
        return []
    
    def save_deals(self, deals):
        """Save deals to file"""
        with open(self.deals_file, 'w') as f:
            json.dump(deals, f, indent=2)
    
    def find_best_deals(self, listings, top_n=10):
        """Identify the best deals based on price, specifications, and value"""
        if not listings:
            return []
            
        # Create DataFrame for analysis
        df = pd.DataFrame(listings)
        
        # Filter out listings with missing critical info
        df = df[df['price'] > 0]
        df = df[df['year'] > 2015]  # Focus on relatively recent models
        
        # Calculate value score (higher is better)
        df['value_score'] = self.calculate_value_score(df)
        
        # Sort by value score and get top deals
        best_deals = df.nlargest(top_n, 'value_score')
        
        return best_deals.to_dict('records')
    
    def calculate_value_score(self, df):
        """Calculate value score for each listing"""
        score = pd.Series(0, index=df.index)
        
        # Base score from specs
        score += df['year'] * 10  # Newer is better
        score += df['memory'] * 2  # More RAM is better
        score += df['storage'] / 100  # More storage is better
        score += df['screen_size'] * 5  # Larger screen bonus
        
        # Model preference
        model_bonus = df['model'].map({
            'MacBook Pro': 50,
            'MacBook Air': 30,
            'MacBook': 20
        }).fillna(0)
        score += model_bonus
        
        # Price consideration (lower price increases score)
        max_price = df['price'].max()
        price_score = (max_price - df['price']) / max_price * 100
        score += price_score
        
        return score
    
    def send_email_alert(self, best_deals):
        """Send email alert with best deals"""
        if not self.email_config['email'] or not self.email_config['recipient']:
            logging.warning("Email configuration missing, skipping email alert")
            return
            
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_config['email']
            msg['To'] = self.email_config['recipient']
            msg['Subject'] = f"🍎 Best MacBook Deals - {datetime.now().strftime('%Y-%m-%d')}"
            
            body = self.create_email_body(best_deals)
            msg.attach(MIMEText(body, 'html'))
            
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['email'], self.email_config['password'])
            
            text = msg.as_string()
            server.sendmail(self.email_config['email'], self.email_config['recipient'], text)
            server.quit()
            
            logging.info(f"Email sent successfully to {self.email_config['recipient']}")
            
        except Exception as e:
            logging.error(f"Failed to send email: {e}")
    
    def create_email_body(self, deals):
        """Create HTML email body with deal information"""
        html = """
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
                .header { background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
                .deal { border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px; }
                .deal-title { font-weight: bold; color: #333; margin-bottom: 5px; }
                .deal-price { color: #28a745; font-size: 18px; font-weight: bold; }
                .deal-specs { color: #666; font-size: 14px; margin: 5px 0; }
                .deal-link { color: #007bff; text-decoration: none; }
                .deal-link:hover { text-decoration: underline; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🍎 Best MacBook Deals Found</h1>
                <p>Here are the top refurbished MacBook deals found on eBay:</p>
            </div>
        """
        
        for i, deal in enumerate(deals, 1):
            html += f"""
            <div class="deal">
                <div class="deal-title">#{i}. {deal['title'][:100]}...</div>
                <div class="deal-price">${deal['price']:.2f}</div>
                <div class="deal-specs">
                    {deal['model']} ({deal['year']}) | {deal['screen_size']}" | 
                    {deal['memory']}GB RAM | {deal['storage']}GB Storage
                </div>
                <div class="deal-specs">📍 {deal['location']} | 🚚 {deal['shipping']}</div>
                <a href="{deal['link']}" class="deal-link">View on eBay</a>
            </div>
            """
        
        html += """
        </body>
        </html>
        """
        
        return html
    
    def run_daily_check(self):
        """Run the daily check for deals"""
        logging.info("Starting daily MacBook deal check...")
        
        # Search for different MacBook types
        search_terms = [
            "refurbished macbook pro",
            "refurbished macbook air",
            "used macbook pro",
            "used macbook air"
        ]
        
        all_listings = []
        for term in search_terms:
            listings = self.search_macbooks(term, max_pages=2)
            all_listings.extend(listings)
            time.sleep(random.uniform(2, 4))  # Respectful delay
        
        logging.info(f"Found {len(all_listings)} total listings")
        
        # Remove duplicates based on title and price
        unique_listings = []
        seen = set()
        for listing in all_listings:
            key = (listing['title'], listing['price'])
            if key not in seen:
                seen.add(key)
                unique_listings.append(listing)
        
        logging.info(f"Found {len(unique_listings)} unique listings")
        
        # Find best deals
        best_deals = self.find_best_deals(unique_listings, top_n=15)
        
        if best_deals:
            logging.info(f"Found {len(best_deals)} best deals")
            
            # Save deals
            previous_deals = self.load_previous_deals()
            previous_deals.extend(best_deals)
            
            # Keep only recent deals (last 30 days)
            cutoff_date = datetime.now() - timedelta(days=30)
            recent_deals = [
                deal for deal in previous_deals
                if datetime.fromisoformat(deal['found_date']) > cutoff_date
            ]
            
            self.save_deals(recent_deals)
            
            # Send email alert
            self.send_email_alert(best_deals)
            
        else:
            logging.info("No good deals found today")

def main():
    """Main function to run the deal tracker"""
    tracker = MacBookDealTracker()
    
    # Run immediately
    tracker.run_daily_check()
    
    # Schedule daily runs
    schedule.every().day.at("09:00").do(tracker.run_daily_check)
    
    logging.info("MacBook Deal Tracker started. Press Ctrl+C to stop.")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        logging.info("MacBook Deal Tracker stopped.")

if __name__ == "__main__":
    main()