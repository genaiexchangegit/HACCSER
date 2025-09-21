#!/usr/bin/env python3
"""
Setup script for the local PyAutoGUI client
This script helps users set up the local client easily
"""

import os
import subprocess
import sys

def install_requirements():
    """Install required packages for the local client"""
    print("Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyautogui", "pillow", "requests"])
        print("✅ Packages installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing packages: {e}")
        return False

def create_images_directory():
    """Create images directory if it doesn't exist"""
    if not os.path.exists('images'):
        os.makedirs('images')
        print("✅ Created images directory")
        
        # Create placeholder files
        with open('images/button.png', 'w') as f:
            f.write("# Placeholder for button.png - replace with your actual image")
        with open('images/logo.png', 'w') as f:
            f.write("# Placeholder for logo.png - replace with your actual image")
        
        print("✅ Created placeholder image files")
        print("📝 Please replace images/button.png and images/logo.png with your actual images")
    else:
        print("✅ Images directory already exists")

def update_client_url():
    """Update the client URL in local_client.py"""
    print("\n🌐 Please enter your Render app URL:")
    print("   Example: https://your-app-name.onrender.com")
    
    url = input("URL: ").strip()
    
    if not url:
        print("❌ No URL provided")
        return False
    
    if not url.startswith('http'):
        url = f"https://{url}"
    
    try:
        # Read the current file
        with open('local_client.py', 'r') as f:
            content = f.read()
        
        # Replace the URL
        content = content.replace('RENDER_APP_URL = "https://your-app-name.onrender.com"', f'RENDER_APP_URL = "{url}"')
        
        # Write back
        with open('local_client.py', 'w') as f:
            f.write(content)
        
        print(f"✅ Updated local_client.py with URL: {url}")
        return True
    except Exception as e:
        print(f"❌ Error updating URL: {e}")
        return False

def main():
    """Main setup function"""
    print("🤖 PyAutoGUI Local Client Setup")
    print("=" * 40)
    
    # Install requirements
    if not install_requirements():
        return
    
    # Create images directory
    create_images_directory()
    
    # Update client URL
    if not update_client_url():
        return
    
    print("\n🎉 Setup complete!")
    print("\n📋 Next steps:")
    print("1. Replace images/button.png and images/logo.png with your actual images")
    print("2. Run: python local_client.py")
    print("3. Open your web app and start controlling your local screen!")
    print("\n⚠️  Note: The local client will control your mouse and keyboard.")
    print("   Move your mouse to the top-left corner to stop PyAutoGUI if needed.")

if __name__ == "__main__":
    main()
