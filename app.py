from flask import Flask, render_template, request, jsonify
import json
import pyautogui
import os
import time
import logging
from datetime import datetime
from PIL import Image

app = Flask(__name__)

# Configure PyAutoGUI
pyautogui.FAILSAFE = True  # Move mouse to top-left corner to stop
pyautogui.PAUSE = 0.5  # Pause between actions

# Hardcoded image paths (you can modify these)
IMAGE_PATHS = {
    'button': 'images/button.png',
    'icon': 'images/icon.png',
    'logo': 'images/logo.png'
}

# Configure logging
def setup_logging():
    """Setup file logging for console logs"""
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Create a custom logger
    logger = logging.getLogger('console_logs')
    logger.setLevel(logging.INFO)
    
    # Create file handler with timestamp
    log_filename = f"logs/console_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    file_handler = logging.FileHandler(log_filename)
    file_handler.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(file_handler)
    
    return logger

# Initialize logging
console_logger = setup_logging()

@app.route('/')
def index():
    """Serve the main HTML page"""
    return render_template('index.html')

@app.route('/api/permissions', methods=['POST'])
def handle_permissions():
    """Handle permission data from JavaScript"""
    try:
        data = request.get_json()
        print(f"Received permission data: {json.dumps(data, indent=2)}")
        
        # Here you can process the permission data
        # For example, save to database, log, etc.
        
        return jsonify({
            'status': 'success',
            'message': 'Permissions received successfully',
            'data': data
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

@app.route('/api/location', methods=['POST'])
def handle_location():
    """Handle location data"""
    try:
        data = request.get_json()
        print(f"Location data: {json.dumps(data, indent=2)}")
        
        return jsonify({
            'status': 'success',
            'message': 'Location received successfully'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

@app.route('/api/console-logs', methods=['POST'])
def handle_console_logs():
    """Handle console logs from JavaScript and save to file"""
    try:
        data = request.get_json()
        logs = data.get('logs', [])
        session_id = data.get('sessionId', 'unknown')
        
        print(f"Received {len(logs)} console logs from session: {session_id}")
        
        # Log each console entry to file
        for log_entry in logs:
            log_message = f"[{session_id}] {log_entry.get('level', 'info').upper()}: {log_entry.get('message', '')}"
            console_logger.info(log_message)
            
            # Also print to server console for debugging
            print(f"Console Log [{log_entry.get('level', 'info')}]: {log_entry.get('message', '')}")
        
        return jsonify({
            'status': 'success',
            'message': f'Successfully logged {len(logs)} console entries',
            'sessionId': session_id,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"Error handling console logs: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

# Background PyAutoGUI functions (no frontend interface)
def background_image_detection():
    """Background function to continuously detect and click images"""
    try:
        # Check if we're in a headless environment (like Render)
        if os.environ.get('RENDER') or not os.environ.get('DISPLAY'):
            print("Running in headless environment - PyAutoGUI disabled")
            console_logger.info("Running in headless environment - PyAutoGUI disabled")
            return
            
        while True:
            for image_name, image_path in IMAGE_PATHS.items():
                if os.path.exists(image_path):
                    try:
                        # Look for the image with high confidence
                        location = pyautogui.locateOnScreen(image_path, confidence=0.9)
                        if location:
                            center = pyautogui.center(location)
                            pyautogui.click(center.x, center.y)
                            print(f"Background: Clicked on {image_name} at ({center.x}, {center.y})")
                            
                            # Log to file
                            console_logger.info(f"Background PyAutoGUI: Clicked on {image_name} at ({center.x}, {center.y})")
                            
                    except Exception as e:
                        # Silently continue if image not found
                        pass
            
            # Wait before next check
            time.sleep(2)
            
    except Exception as e:
        print(f"Background image detection error: {str(e)}")
        console_logger.error(f"Background PyAutoGUI error: {str(e)}")

# Start background PyAutoGUI in a separate thread (only if not in headless environment)
import threading
if not os.environ.get('RENDER'):
    background_thread = threading.Thread(target=background_image_detection, daemon=True)
    background_thread.start()
else:
    print("Render environment detected - PyAutoGUI background thread disabled")

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=debug, host='0.0.0.0', port=port)
