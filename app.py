from flask import Flask, render_template, request, jsonify
import json

app = Flask(__name__)

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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
