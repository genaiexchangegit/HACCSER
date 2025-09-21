from flask import Flask, render_template, request, jsonify
import json
import os
import time
import logging
from datetime import datetime

# Set up virtual display for headless environments (like Render)
try:
    from pyvirtualdisplay import Display
    # Check if we're in a headless environment
    if not os.environ.get('DISPLAY'):
        print("Setting up virtual display for PyAutoGUI...")
        display = Display(visible=0, size=(1920, 1080))
        display.start()
        os.environ['DISPLAY'] = ':99'
        print("Virtual display started successfully")
except ImportError:
    print("pyvirtualdisplay not available - PyAutoGUI may not work in headless environment")
except Exception as e:
    print(f"Error setting up virtual display: {e}")

# Now import PyAutoGUI after setting up display
import pyautogui
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

@app.route('/api/test-pyautogui', methods=['GET'])
def test_pyautogui():
    """Test if PyAutoGUI is working properly"""
    try:
        # Test screen size
        screen_size = pyautogui.size()
        
        # Test screenshot capability
        screenshot = pyautogui.screenshot()
        
        return jsonify({
            'status': 'success',
            'message': 'PyAutoGUI is working properly',
            'screen_size': {'width': screen_size.width, 'height': screen_size.height},
            'screenshot_size': {'width': screenshot.width, 'height': screenshot.height},
            'display': os.environ.get('DISPLAY', 'Not set')
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'PyAutoGUI test failed: {str(e)}',
            'display': os.environ.get('DISPLAY', 'Not set')
        }), 400

# Remote PyAutoGUI control system
connected_clients = {}
command_queue = {}
command_results = {}

@app.route('/api/register-client', methods=['POST'])
def register_client():
    """Register a local PyAutoGUI client"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        client_type = data.get('client_type')
        
        connected_clients[session_id] = {
            'type': client_type,
            'connected_at': datetime.now().isoformat(),
            'last_seen': datetime.now().isoformat()
        }
        
        print(f"Client registered: {session_id} ({client_type})")
        
        return jsonify({
            'status': 'success',
            'message': 'Client registered successfully',
            'session_id': session_id
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

@app.route('/api/send-command', methods=['POST'])
def send_command():
    """Send a command to a local PyAutoGUI client"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        action = data.get('action')
        
        if session_id not in connected_clients:
            return jsonify({
                'status': 'error',
                'message': 'Client not connected'
            }), 400
        
        command = {
            'id': len(command_queue.get(session_id, [])) + 1,
            'action': action,
            'image_name': data.get('image_name'),
            'x': data.get('x'),
            'y': data.get('y'),
            'text': data.get('text'),
            'timestamp': datetime.now().isoformat()
        }
        
        if session_id not in command_queue:
            command_queue[session_id] = []
        
        command_queue[session_id].append(command)
        
        print(f"Command queued for {session_id}: {command}")
        
        return jsonify({
            'status': 'success',
            'message': 'Command sent to local client',
            'command_id': command['id']
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

@app.route('/api/get-commands/<session_id>', methods=['GET'])
def get_commands(session_id):
    """Get pending commands for a client"""
    try:
        if session_id in connected_clients:
            connected_clients[session_id]['last_seen'] = datetime.now().isoformat()
        
        commands = command_queue.get(session_id, [])
        # Clear the queue after sending
        if session_id in command_queue:
            command_queue[session_id] = []
        
        return jsonify({
            'commands': commands
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

@app.route('/api/command-result', methods=['POST'])
def handle_command_result():
    """Handle command results from local clients"""
    try:
        data = request.get_json()
        command_id = data.get('command_id')
        session_id = data.get('session_id')
        success = data.get('success')
        message = data.get('message', '')
        
        command_results[command_id] = {
            'session_id': session_id,
            'success': success,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"Command {command_id} result: {'Success' if success else 'Failed'} - {message}")
        
        return jsonify({'status': 'success'})
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

@app.route('/api/connected-clients', methods=['GET'])
def get_connected_clients():
    """Get list of connected clients"""
    return jsonify({
        'clients': connected_clients,
        'count': len(connected_clients)
    })

# Background PyAutoGUI functions (no frontend interface)
def background_image_detection():
    """Background function to continuously detect and click images"""
    try:
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

# Start background PyAutoGUI in a separate thread
import threading
background_thread = threading.Thread(target=background_image_detection, daemon=True)
background_thread.start()

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=debug, host='0.0.0.0', port=port)
    