# Permission Request Demo

A Python Flask server with HTML/JavaScript that demonstrates requesting browser permissions for location, clipboard, and camera access.

## Features

- **Location Permission**: Requests access to user's current location using the Geolocation API
- **Clipboard Permission**: Requests access to read and write clipboard data
- **Camera Permission**: Requests access to user's camera and displays video stream
- **Modern UI**: Beautiful, responsive design with real-time permission status updates
- **Server Integration**: Sends permission data to Python backend for processing

## Setup

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the server:**
   ```bash
   python app.py
   ```

3. **Open your browser:**
   Navigate to `http://localhost:5000`

## Browser Requirements

- **HTTPS Required**: For production use, serve over HTTPS as many permissions require secure context
- **Modern Browser**: Requires browsers that support:
  - Geolocation API
  - Clipboard API
  - MediaDevices API (getUserMedia)
  - Permissions API (optional)

## Security Notes

- Location, clipboard, and camera permissions are sensitive
- Always request permissions only when necessary
- Provide clear explanations for why permissions are needed
- Handle permission denials gracefully

## API Endpoints

- `GET /` - Serves the main HTML page
- `POST /api/permissions` - Receives permission status updates
- `POST /api/location` - Receives location data

## File Structure

```
project/
├── app.py                 # Flask server
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html        # Main HTML page
└── static/
    ├── style.css         # CSS styling
    └── script.js         # JavaScript permission handling
```

## Development

The server runs in debug mode by default. For production:

1. Set `debug=False` in `app.py`
2. Use a production WSGI server like Gunicorn
3. Serve over HTTPS
4. Configure proper security headers
