# 🍎 MacBook Deal Tracker

An automated tool that checks eBay daily for refurbished MacBooks and sends email alerts about the best deals.

## Features

- 🔍 **Smart Search**: Searches eBay for refurbished MacBook Pro, MacBook Air, and MacBook listings
- 📊 **Deal Analysis**: Analyzes deals based on price, specifications, year, and model
- 📧 **Email Alerts**: Sends beautifully formatted HTML emails with the best deals
- 🗄️ **Data Persistence**: Tracks deals over time and avoids duplicates
- ⏰ **Daily Automation**: Runs automatically at 9 AM daily
- 🛡️ **Respectful Scraping**: Includes delays and rate limiting to be respectful to eBay

## Quick Start

### 1. Setup

Run the setup script to install dependencies and create configuration files:

```bash
python setup.py
```

### 2. Configure Email

Edit the `.env` file with your email credentials:

```env
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
RECIPIENT_EMAIL=recipient@example.com
```

**Important**: For Gmail, use an App Password instead of your regular password:
1. Enable 2-factor authentication on your Gmail account
2. Go to Google Account settings → Security → App passwords
3. Generate a new app password for "Mail"
4. Use this app password in the `.env` file

### 3. Test the Tracker

Run a one-time test to make sure everything works:

```bash
python test_tracker.py
```

### 4. Run the Tracker

Start the tracker with daily scheduling:

```bash
python macbook_deal_tracker.py
```

The tracker will:
- Run immediately on startup
- Schedule daily checks at 9:00 AM
- Continue running until stopped with Ctrl+C

## Advanced Setup

### Running as a Service (Linux)

Create a systemd service file `/etc/systemd/system/macbook-tracker.service`:

```ini
[Unit]
Description=MacBook Deal Tracker
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/macbook-tracker
ExecStart=/usr/bin/python3 /path/to/macbook-tracker/macbook_deal_tracker.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable macbook-tracker
sudo systemctl start macbook-tracker
```

### Running with Cron

Add a cron job to run the tracker daily:

```bash
# Edit crontab
crontab -e

# Add this line to run at 9 AM daily
0 9 * * * cd /path/to/macbook-tracker && python test_tracker.py >> /var/log/macbook-tracker.log 2>&1
```

### Docker Setup

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "macbook_deal_tracker.py"]
```

Build and run:

```bash
docker build -t macbook-tracker .
docker run -d --name macbook-tracker -v $(pwd)/.env:/app/.env macbook-tracker
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `EMAIL_ADDRESS` | Your email address | Required |
| `EMAIL_PASSWORD` | Your email password/app password | Required |
| `RECIPIENT_EMAIL` | Email to send alerts to | Required |
| `SMTP_SERVER` | SMTP server address | smtp.gmail.com |
| `SMTP_PORT` | SMTP server port | 587 |

### Customization

You can modify the search parameters in `macbook_deal_tracker.py`:

```python
# Search terms
search_terms = [
    "refurbished macbook pro",
    "refurbished macbook air",
    "used macbook pro",
    "used macbook air"
]

# Number of pages to search
max_pages = 2

# Number of top deals to report
top_n = 15
```

## How It Works

### 1. Search Strategy
- Searches eBay for various MacBook-related terms
- Filters for "Buy It Now" listings only
- Focuses on used/refurbished condition items
- Searches multiple pages for comprehensive coverage

### 2. Deal Analysis
The tracker uses a scoring algorithm that considers:
- **Year**: Newer models get higher scores
- **Memory**: More RAM increases score
- **Storage**: More storage increases score
- **Screen Size**: Larger screens get bonus points
- **Model**: MacBook Pro > MacBook Air > MacBook
- **Price**: Lower prices increase the value score

### 3. Email Alerts
- Sends HTML-formatted emails with deal details
- Includes price, specifications, location, and eBay links
- Only sends when good deals are found
- Includes deal ranking based on value score

### 4. Data Persistence
- Saves all deals to `macbook_deals.json`
- Tracks deals over time to identify trends
- Removes old deals (30+ days) to keep file size manageable
- Prevents duplicate notifications

## File Structure

```
macbook-tracker/
├── macbook_deal_tracker.py    # Main application
├── test_tracker.py            # Test script
├── setup.py                   # Setup script
├── requirements.txt           # Python dependencies
├── .env.example              # Example environment file
├── .env                      # Your environment config (created by setup)
├── README.md                 # This file
├── macbook_deals.json        # Deal data (created at runtime)
└── macbook_tracker.log       # Log file (created at runtime)
```

## Troubleshooting

### Common Issues

1. **Email not sending**
   - Check your email credentials in `.env`
   - Make sure you're using an App Password for Gmail
   - Verify SMTP settings for your email provider

2. **No deals found**
   - eBay may have changed their HTML structure
   - Check the log file for specific error messages
   - Try running with debug logging enabled

3. **Rate limiting**
   - The tracker includes delays between requests
   - If you get blocked, wait and try again later
   - Consider reducing the number of search pages

### Debug Mode

Enable debug logging by modifying the logging level in the script:

```python
logging.basicConfig(
    level=logging.DEBUG,  # Changed from INFO
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('macbook_tracker.log'),
        logging.StreamHandler()
    ]
)
```

### Logs

Check the log file for detailed information:

```bash
tail -f macbook_tracker.log
```

## Other Email Providers

### Yahoo Mail
```env
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
```

### Outlook/Hotmail
```env
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
```

### Custom SMTP
```env
SMTP_SERVER=your-smtp-server.com
SMTP_PORT=587
```

## Legal and Ethical Considerations

- This tool is for personal use only
- Respects eBay's terms of service with rate limiting
- Does not perform any automated purchasing
- Only scrapes publicly available information
- Includes delays to avoid overwhelming eBay's servers

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is open source and available under the MIT License.

---

**Happy deal hunting! 🍎💰**