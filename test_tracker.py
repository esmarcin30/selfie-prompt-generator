#!/usr/bin/env python3
"""
Test script to run the MacBook Deal Tracker once
"""

from macbook_deal_tracker import MacBookDealTracker
import logging

def test_tracker():
    """Test the MacBook Deal Tracker"""
    print("🍎 Testing MacBook Deal Tracker...")
    
    # Configure logging for testing
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Create tracker instance
    tracker = MacBookDealTracker()
    
    # Run a single check
    tracker.run_daily_check()
    
    print("✅ Test completed! Check the logs above for results.")
    print("📧 If email configuration is set up, you should receive an email alert.")

if __name__ == "__main__":
    test_tracker()