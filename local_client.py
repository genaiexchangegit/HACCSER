#!/usr/bin/env python3
"""
Local PyAutoGUI Client
Connects to your Render web app and executes automation commands on the user's local screen
"""

import requests
import pyautogui
import time
import json
import os
from PIL import Image
import threading

# Configuration
RENDER_APP_URL = "https://your-app-name.onrender.com"  # Replace with your actual Render URL
LOCAL_IMAGES = {
    'button': 'images/button.png',
    'logo': 'images/logo.png'
}

class PyAutoGUIClient:
    def __init__(self, server_url):
        self.server_url = server_url
        self.running = False
        self.session_id = f"client_{int(time.time())}"
        
        # Configure PyAutoGUI
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.5
        
        print(f"PyAutoGUI Client started with session ID: {self.session_id}")
        print(f"Connecting to server: {server_url}")
    
    def register_with_server(self):
        """Register this client with the server"""
        try:
            response = requests.post(f"{self.server_url}/api/register-client", 
                                   json={'session_id': self.session_id, 'client_type': 'pyautogui'})
            if response.status_code == 200:
                print("Successfully registered with server")
                return True
            else:
                print(f"Failed to register: {response.text}")
                return False
        except Exception as e:
            print(f"Error registering with server: {e}")
            return False
    
    def check_for_commands(self):
        """Check the server for automation commands"""
        try:
            response = requests.get(f"{self.server_url}/api/get-commands/{self.session_id}")
            if response.status_code == 200:
                data = response.json()
                return data.get('commands', [])
        except Exception as e:
            print(f"Error checking commands: {e}")
        return []
    
    def execute_command(self, command):
        """Execute a PyAutoGUI command locally"""
        try:
            action = command.get('action')
            command_id = command.get('id')
            
            print(f"Executing command {command_id}: {action}")
            
            if action == 'click_image':
                image_name = command.get('image_name')
                image_path = LOCAL_IMAGES.get(image_name)
                
                if image_path and os.path.exists(image_path):
                    location = pyautogui.locateOnScreen(image_path, confidence=0.9)
                    if location:
                        center = pyautogui.center(location)
                        pyautogui.click(center.x, center.y)
                        print(f"✅ Clicked {image_name} at ({center.x}, {center.y})")
                        return True
                    else:
                        print(f"❌ Image {image_name} not found on screen")
                        return False
                else:
                    print(f"❌ Image file not found: {image_path}")
                    return False
                    
            elif action == 'click_coordinates':
                x = command.get('x')
                y = command.get('y')
                pyautogui.click(x, y)
                print(f"✅ Clicked at coordinates ({x}, {y})")
                return True
                
            elif action == 'type_text':
                text = command.get('text')
                pyautogui.typewrite(text)
                print(f"✅ Typed: {text}")
                return True
                
            elif action == 'screenshot':
                screenshot = pyautogui.screenshot()
                # Save screenshot locally
                filename = f"screenshot_{int(time.time())}.png"
                screenshot.save(filename)
                print(f"✅ Screenshot saved as {filename}")
                return True
                
            elif action == 'get_screen_size':
                size = pyautogui.size()
                print(f"✅ Screen size: {size.width}x{size.height}")
                return True
                
        except Exception as e:
            print(f"❌ Error executing command: {e}")
        return False
    
    def send_result(self, command_id, success, message=""):
        """Send command result back to server"""
        try:
            requests.post(f"{self.server_url}/api/command-result", 
                         json={
                             'command_id': command_id,
                             'session_id': self.session_id,
                             'success': success,
                             'message': message
                         })
        except Exception as e:
            print(f"Error sending result: {e}")
    
    def run(self):
        """Main client loop"""
        self.running = True
        
        # Register with server
        if not self.register_with_server():
            print("Failed to register with server. Exiting.")
            return
        
        print("Client is running. Waiting for commands from web interface...")
        print("Open your web app and send commands to control this local screen!")
        
        while self.running:
            try:
                commands = self.check_for_commands()
                
                for command in commands:
                    success = self.execute_command(command)
                    self.send_result(command['id'], success)
                
                time.sleep(1)  # Check every second
                
            except KeyboardInterrupt:
                print("\nShutting down client...")
                self.running = False
            except Exception as e:
                print(f"Error in main loop: {e}")
                time.sleep(5)  # Wait before retrying

def main():
    """Main function"""
    print("🤖 PyAutoGUI Remote Control Client")
    print("=" * 50)
    
    # Get server URL from user or use default
    server_url = input("Enter your Render app URL (or press Enter for default): ").strip()
    if not server_url:
        server_url = RENDER_APP_URL
    
    if not server_url.startswith('http'):
        server_url = f"https://{server_url}"
    
    # Create and run client
    client = PyAutoGUIClient(server_url)
    client.run()

if __name__ == "__main__":
    main()
