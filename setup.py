#!/usr/bin/env python3
"""
Setup script for MacBook Deal Tracker
"""

import os
import subprocess
import sys

def install_requirements():
    """Install required packages"""
    print("📦 Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing requirements: {e}")
        sys.exit(1)

def setup_environment():
    """Set up environment file"""
    if not os.path.exists('.env'):
        print("🔧 Creating .env file...")
        with open('.env.example', 'r') as example:
            with open('.env', 'w') as env_file:
                env_file.write(example.read())
        print("✅ .env file created! Please edit it with your email configuration.")
    else:
        print("ℹ️  .env file already exists.")

def make_executable():
    """Make scripts executable"""
    scripts = ['macbook_deal_tracker.py', 'test_tracker.py']
    for script in scripts:
        if os.path.exists(script):
            os.chmod(script, 0o755)
            print(f"✅ Made {script} executable")

def main():
    """Main setup function"""
    print("🍎 MacBook Deal Tracker Setup")
    print("=" * 30)
    
    install_requirements()
    setup_environment()
    make_executable()
    
    print("\n🎉 Setup complete!")
    print("\nNext steps:")
    print("1. Edit .env file with your email credentials")
    print("2. Test the tracker: python test_tracker.py")
    print("3. Run the tracker: python macbook_deal_tracker.py")
    print("4. Set up cron job for daily runs (see README.md)")

if __name__ == "__main__":
    main()