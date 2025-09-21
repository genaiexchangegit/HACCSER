// Permission handling JavaScript
class PermissionManager {
    constructor() {
        this.permissions = {
            location: 'unknown',
            clipboard: 'unknown',
            camera: 'unknown'
        };
        this.initializeEventListeners();
        this.updatePermissionStatus();
    }

    initializeEventListeners() {
        document.getElementById('locationBtn').addEventListener('click', () => this.requestLocation());
        document.getElementById('clipboardBtn').addEventListener('click', () => this.requestClipboard());
        document.getElementById('cameraBtn').addEventListener('click', () => this.requestCamera());
        
        // Initialize console logging
        this.initializeConsoleLogging();
    }

    async requestLocation() {
        const btn = document.getElementById('locationBtn');
        const result = document.getElementById('locationResult');
        
        btn.disabled = true;
        btn.textContent = 'Requesting...';
        result.innerHTML = 'Requesting location permission...';
        result.className = 'result info';

        try {
            if (!navigator.geolocation) {
                throw new Error('Geolocation is not supported by this browser.');
            }

            // Request location permission
            const position = await new Promise((resolve, reject) => {
                navigator.geolocation.getCurrentPosition(resolve, reject, {
                    enableHighAccuracy: true,
                    timeout: 10000,
                    maximumAge: 60000
                });
            });

            this.permissions.location = 'granted';
            
            const locationData = {
                latitude: position.coords.latitude,
                longitude: position.coords.longitude,
                accuracy: position.coords.accuracy,
                timestamp: new Date().toISOString()
            };

            result.innerHTML = `
                <strong>✅ Location Access Granted!</strong><br>
                Latitude: ${locationData.latitude.toFixed(6)}<br>
                Longitude: ${locationData.longitude.toFixed(6)}<br>
                Accuracy: ${locationData.accuracy} meters<br>
                Time: ${new Date(locationData.timestamp).toLocaleString()}
            `;
            result.className = 'result success';

            // Send location data to server
            await this.sendToServer('/api/location', locationData);

        } catch (error) {
            this.permissions.location = 'denied';
            result.innerHTML = `<strong>❌ Location Access Denied:</strong><br>${error.message}`;
            result.className = 'result error';
            console.error('Location error:', error);
        }

        btn.disabled = false;
        btn.textContent = 'Request Location';
        this.updatePermissionStatus();
    }

    async requestClipboard() {
        const btn = document.getElementById('clipboardBtn');
        const result = document.getElementById('clipboardResult');
        
        btn.disabled = true;
        btn.textContent = 'Requesting...';
        result.innerHTML = 'Requesting clipboard permission...';
        result.className = 'result info';

        try {
            // Check if clipboard API is available
            if (!navigator.clipboard) {
                throw new Error('Clipboard API is not supported by this browser.');
            }

            // Try to read clipboard content
            const clipboardText = await navigator.clipboard.readText();
            
            this.permissions.clipboard = 'granted';
            
            result.innerHTML = `
                <strong>✅ Clipboard Access Granted!</strong><br>
                Current clipboard content: "${clipboardText.substring(0, 100)}${clipboardText.length > 100 ? '...' : ''}"
            `;
            result.className = 'result success';

            // Test writing to clipboard
            const testText = `Clipboard test - ${new Date().toLocaleString()}`;
            await navigator.clipboard.writeText(testText);
            
            result.innerHTML += `<br><br><strong>✅ Write Test Successful!</strong><br>Wrote: "${testText}"`;

        } catch (error) {
            this.permissions.clipboard = 'denied';
            result.innerHTML = `<strong>❌ Clipboard Access Denied:</strong><br>${error.message}`;
            result.className = 'result error';
            console.error('Clipboard error:', error);
        }

        btn.disabled = false;
        btn.textContent = 'Request Clipboard Access';
        this.updatePermissionStatus();
    }

    async requestCamera() {
        const btn = document.getElementById('cameraBtn');
        const result = document.getElementById('cameraResult');
        const video = document.getElementById('video');
        
        btn.disabled = true;
        btn.textContent = 'Requesting...';
        result.innerHTML = 'Requesting camera permission...';
        result.className = 'result info';

        try {
            // Check if getUserMedia is available
            if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                throw new Error('Camera API is not supported by this browser.');
            }

            // Request camera access
            const stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    width: { ideal: 640 },
                    height: { ideal: 480 },
                    facingMode: 'user'
                },
                audio: false
            });

            this.permissions.camera = 'granted';
            
            // Display video stream
            video.srcObject = stream;
            video.style.display = 'block';
            
            result.innerHTML = `
                <strong>✅ Camera Access Granted!</strong><br>
                Video stream started successfully.<br>
                Resolution: ${stream.getVideoTracks()[0].getSettings().width}x${stream.getVideoTracks()[0].getSettings().height}
            `;
            result.className = 'result success';

            // Get camera capabilities
            const track = stream.getVideoTracks()[0];
            const capabilities = track.getCapabilities();
            console.log('Camera capabilities:', capabilities);

        } catch (error) {
            this.permissions.camera = 'denied';
            result.innerHTML = `<strong>❌ Camera Access Denied:</strong><br>${error.message}`;
            result.className = 'result error';
            console.error('Camera error:', error);
        }

        btn.disabled = false;
        btn.textContent = 'Request Camera Access';
        this.updatePermissionStatus();
    }

    updatePermissionStatus() {
        const statusContainer = document.getElementById('permissionStatus');
        statusContainer.innerHTML = '';

        Object.entries(this.permissions).forEach(([permission, status]) => {
            const statusItem = document.createElement('div');
            statusItem.className = `status-item ${status}`;
            
            const icon = this.getStatusIcon(status);
            const label = this.getPermissionLabel(permission);
            
            statusItem.innerHTML = `
                <div style="font-size: 1.5rem; margin-bottom: 5px;">${icon}</div>
                <div>${label}</div>
                <div style="font-size: 0.9rem; text-transform: capitalize;">${status}</div>
            `;
            
            statusContainer.appendChild(statusItem);
        });

        // Send permission status to server
        this.sendToServer('/api/permissions', this.permissions);
    }

    getStatusIcon(status) {
        switch (status) {
            case 'granted': return '✅';
            case 'denied': return '❌';
            case 'prompt': return '⚠️';
            default: return '❓';
        }
    }

    getPermissionLabel(permission) {
        switch (permission) {
            case 'location': return 'Location';
            case 'clipboard': return 'Clipboard';
            case 'camera': return 'Camera';
            default: return permission;
        }
    }

    async sendToServer(endpoint, data) {
        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();
            console.log(`Server response for ${endpoint}:`, result);
            
            if (!response.ok) {
                throw new Error(result.message || 'Server error');
            }
            
            return result;
        } catch (error) {
            console.error(`Error sending data to ${endpoint}:`, error);
        }
    }

    initializeConsoleLogging() {
        // Override console methods to capture logs
        const originalLog = console.log;
        const originalError = console.error;
        const originalWarn = console.warn;
        const originalInfo = console.info;
        
        // Store logs to send to server
        this.consoleLogs = [];
        
        // Override console.log
        console.log = (...args) => {
            originalLog.apply(console, args);
            this.logToServer('log', args);
        };
        
        // Override console.error
        console.error = (...args) => {
            originalError.apply(console, args);
            this.logToServer('error', args);
        };
        
        // Override console.warn
        console.warn = (...args) => {
            originalWarn.apply(console, args);
            this.logToServer('warn', args);
        };
        
        // Override console.info
        console.info = (...args) => {
            originalInfo.apply(console, args);
            this.logToServer('info', args);
        };
        
        // Log initial page load
        console.log('Page loaded - Console logging initialized');
        console.log('Browser capabilities:', {
            userAgent: navigator.userAgent,
            platform: navigator.platform,
            language: navigator.language,
            cookieEnabled: navigator.cookieEnabled,
            onLine: navigator.onLine
        });
    }
    
    async logToServer(level, args) {
        try {
            const logEntry = {
                timestamp: new Date().toISOString(),
                level: level,
                message: args.map(arg => 
                    typeof arg === 'object' ? JSON.stringify(arg, null, 2) : String(arg)
                ).join(' '),
                url: window.location.href,
                userAgent: navigator.userAgent
            };
            
            this.consoleLogs.push(logEntry);
            
            // Send logs to server (batch every 5 logs or every 10 seconds)
            if (this.consoleLogs.length >= 5 || !this.logTimer) {
                await this.sendLogsToServer();
            }
            
            // Set timer for periodic sending
            if (!this.logTimer) {
                this.logTimer = setTimeout(() => {
                    this.sendLogsToServer();
                }, 10000); // 10 seconds
            }
            
        } catch (error) {
            // Don't use console.error here to avoid infinite loop
            originalError.call(console, 'Error logging to server:', error);
        }
    }
    
    async sendLogsToServer() {
        if (this.consoleLogs.length === 0) return;
        
        try {
            const logsToSend = [...this.consoleLogs];
            this.consoleLogs = []; // Clear the array
            
            await fetch('/api/console-logs', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    logs: logsToSend,
                    sessionId: this.getSessionId()
                })
            });
            
            // Clear timer
            if (this.logTimer) {
                clearTimeout(this.logTimer);
                this.logTimer = null;
            }
            
        } catch (error) {
            // Put logs back if sending failed
            this.consoleLogs.unshift(...logsToSend);
        }
    }
    
    getSessionId() {
        if (!this.sessionId) {
            this.sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        }
        return this.sessionId;
    }

    // Check existing permissions (if supported)
    async checkExistingPermissions() {
        try {
            // Check geolocation permission
            if (navigator.permissions) {
                const locationPermission = await navigator.permissions.query({ name: 'geolocation' });
                this.permissions.location = locationPermission.state;
                
                const cameraPermission = await navigator.permissions.query({ name: 'camera' });
                this.permissions.camera = cameraPermission.state;
            }
        } catch (error) {
            console.log('Permission query not fully supported:', error);
        }
        
        this.updatePermissionStatus();
    }
}

// Initialize the permission manager when the page loads
document.addEventListener('DOMContentLoaded', () => {
    const permissionManager = new PermissionManager();
    
    // Check existing permissions
    permissionManager.checkExistingPermissions();
    
    // Log browser capabilities
    console.log('Browser capabilities:');
    console.log('- Geolocation:', !!navigator.geolocation);
    console.log('- Clipboard API:', !!navigator.clipboard);
    console.log('- MediaDevices:', !!navigator.mediaDevices);
    console.log('- getUserMedia:', !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia));
    console.log('- Permissions API:', !!navigator.permissions);
});

// Handle page visibility changes
document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible') {
        console.log('Page became visible - checking permissions...');
        // Re-check permissions when page becomes visible
        if (window.permissionManager) {
            window.permissionManager.checkExistingPermissions();
        }
    }

    // Remote PyAutoGUI Control
    let clientSessionId = null;
    let connectedClients = {};

    // Initialize remote control
    initializeRemoteControl();

    function initializeRemoteControl() {
        // Generate a unique session ID for this browser session
        clientSessionId = `web_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        
        // Set up event listeners
        document.getElementById('connectClientBtn').addEventListener('click', checkConnectedClients);
        document.getElementById('clickButtonBtn').addEventListener('click', () => sendCommand('click_image', {image_name: 'button'}));
        document.getElementById('clickLogoBtn').addEventListener('click', () => sendCommand('click_image', {image_name: 'logo'}));
        document.getElementById('clickCoordinatesBtn').addEventListener('click', () => sendCommand('click_coordinates', {x: 500, y: 300}));
        document.getElementById('typeTextBtn').addEventListener('click', () => sendCommand('type_text', {text: 'Hello World'}));
        document.getElementById('screenshotBtn').addEventListener('click', () => sendCommand('screenshot', {}));
        
        // Check for connected clients periodically
        setInterval(checkConnectedClients, 5000);
    }

    async function checkConnectedClients() {
        try {
            const response = await fetch('/api/connected-clients');
            const data = await response.json();
            
            connectedClients = data.clients;
            const clientCount = data.count;
            
            const statusDiv = document.getElementById('clientStatus');
            if (clientCount > 0) {
                statusDiv.innerHTML = `<div class="success">✅ ${clientCount} local PyAutoGUI client(s) connected</div>`;
                statusDiv.style.color = 'green';
            } else {
                statusDiv.innerHTML = `<div class="error">❌ No local PyAutoGUI clients connected. Run local_client.py on your machine.</div>`;
                statusDiv.style.color = 'red';
            }
        } catch (error) {
            console.error('Error checking connected clients:', error);
            document.getElementById('clientStatus').innerHTML = `<div class="error">Error checking client status</div>`;
        }
    }

    async function sendCommand(action, params = {}) {
        if (Object.keys(connectedClients).length === 0) {
            document.getElementById('automationResult').innerHTML = 
                '<div class="error">❌ No local clients connected. Please run local_client.py first.</div>';
            return;
        }

        try {
            // Send command to the first connected client
            const sessionId = Object.keys(connectedClients)[0];
            
            const response = await fetch('/api/send-command', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    session_id: sessionId,
                    action: action,
                    ...params
                })
            });

            const result = await response.json();
            
            if (result.status === 'success') {
                document.getElementById('automationResult').innerHTML = 
                    `<div class="success">✅ Command sent: ${action}</div>`;
                console.log('Command sent successfully:', result);
            } else {
                document.getElementById('automationResult').innerHTML = 
                    `<div class="error">❌ Failed to send command: ${result.message}</div>`;
            }
        } catch (error) {
            console.error('Error sending command:', error);
            document.getElementById('automationResult').innerHTML = 
                '<div class="error">❌ Error sending command</div>';
        }
    }
});
