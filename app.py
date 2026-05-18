from flask import Flask, render_template, send_file, jsonify
import qrcode
import json
from io import BytesIO
import os
from datetime import datetime

app = Flask(__name__)

# ========== THÔNG TIN SÁCH ==========
BOOK_INFO = {
    "title": "Những Đứa Trẻ Không Gia Đình",
    "author": "Hector Malot",
    "year": 1878,
    "description": "Tiểu thuyết cảm động về những đứa trẻ bất hạnh",
    "isbn": "978-6-04-009-099-9",
    "language": "Vietnamese"
}


# ========== ROUTE 1: Trang Chính ==========
@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>📚 QR Book Scanner</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }
            .container {
                background: white;
                border-radius: 15px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.3);
                max-width: 600px;
                width: 100%;
                padding: 40px;
                text-align: center;
            }
            h1 {
                color: #333;
                margin-bottom: 10px;
                font-size: 28px;
            }
            .subtitle {
                color: #999;
                margin-bottom: 30px;
                font-size: 14px;
            }
            .qr-section {
                background: #f5f5f5;
                border-radius: 10px;
                padding: 30px;
                margin-bottom: 30px;
            }
            #qr-image {
                max-width: 300px;
                height: auto;
                margin: 20px auto;
                display: block;
                border: 3px solid #667eea;
                border-radius: 8px;
                padding: 10px;
                background: white;
            }
            .book-info {
                background: #f9f9f9;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 20px;
                text-align: left;
            }
            .info-row {
                display: flex;
                justify-content: space-between;
                padding: 10px 0;
                border-bottom: 1px solid #eee;
            }
            .info-row:last-child {
                border-bottom: none;
            }
            .info-label {
                font-weight: bold;
                color: #333;
                min-width: 80px;
            }
            .info-value {
                color: #666;
                text-align: right;
                flex: 1;
            }
            .button {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 15px 40px;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                cursor: pointer;
                transition: 0.3s;
                width: 100%;
                margin-bottom: 10px;
            }
            .button:hover {
                transform: scale(1.02);
                box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
            }
            .button:active {
                transform: scale(0.98);
            }
            .download-button {
                background: #4ECDC4;
                color: white;
                padding: 12px 30px;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                cursor: pointer;
                transition: 0.3s;
                margin-top: 10px;
                width: 100%;
            }
            .download-button:hover {
                background: #45B7B0;
            }
            .scanner-container {
                display: none;
                margin-top: 30px;
                padding: 20px;
                background: #f9f9f9;
                border-radius: 10px;
            }
            .scanner-container.active {
                display: block;
            }
            video {
                width: 100%;
                max-width: 100%;
                border-radius: 8px;
                margin: 15px 0;
                background: #000;
                display: block;
            }
            #canvas {
                display: none;
            }
            .result {
                display: none;
                background: #d4edda;
                color: #155724;
                padding: 15px;
                border-radius: 8px;
                margin-top: 10px;
                border: 1px solid #c3e6cb;
            }
            .result.active {
                display: block;
            }
            .result-content {
                text-align: left;
            }
            .result-content strong {
                display: block;
                margin-bottom: 10px;
                font-size: 16px;
            }
            .status {
                padding: 10px;
                border-radius: 8px;
                text-align: center;
                font-weight: bold;
                margin-top: 10px;
            }
            .status.loading {
                background: #fff3cd;
                color: #856404;
            }
            .status.error {
                background: #f8d7da;
                color: #721c24;
            }
            .status.success {
                background: #d4edda;
                color: #155724;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📚 QR Book Scanner</h1>
            <p class="subtitle">Test QR code camera scanning</p>

            <!-- QR Code Section -->
            <div class="qr-section">
                <h2 style="margin-bottom: 15px;">Step 1: View QR Code</h2>
                <img id="qr-image" src="/generate-qr" alt="QR Code">
                <button class="download-button" onclick="downloadQR()">⬇️ Download QR Code</button>
            </div>

            <!-- Book Info Section -->
            <div class="book-info">
                <h3 style="margin-bottom: 15px;">📖 Book Information</h3>
                <div class="info-row">
                    <span class="info-label">Title:</span>
                    <span class="info-value">Những Đứa Trẻ Không Gia Đình</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Author:</span>
                    <span class="info-value">Hector Malot</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Year:</span>
                    <span class="info-value">1878</span>
                </div>
                <div class="info-row">
                    <span class="info-label">ISBN:</span>
                    <span class="info-value">978-6-04-009-099-9</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Description:</span>
                    <span class="info-value">Tiểu thuyết cảm động về những đứa trẻ bất hạnh</span>
                </div>
            </div>

            <!-- Scanner Section -->
            <button class="button" onclick="toggleScanner()">
                📱 Step 2: Scan QR Code
            </button>

            <div id="scanner-container" class="scanner-container">
                <h3 style="margin-bottom: 15px;">Camera Scanner</h3>
                <p style="margin-bottom: 15px; color: #666;">
                    Click "Start Scanning" to open your device's camera
                </p>

                <button class="button" id="start-button" onclick="startScanning()" style="margin-bottom: 15px;">
                    🎥 Start Scanning
                </button>

                <button class="button" id="stop-button" onclick="stopScanning()" style="display: none; background: #ff6b6b; margin-bottom: 15px;">
                    ⏹ Stop Scanning
                </button>

                <video id="video" width="100%" playsinline></video>
                <canvas id="canvas"></canvas>

                <div id="status" class="status loading" style="display: none;">
                    ⏳ Initializing camera...
                </div>

                <div id="result" class="result">
                    <div class="result-content">
                        <strong>✅ QR Code Scanned Successfully!</strong>
                        <div id="result-text" style="margin-top: 10px;"></div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Thư viện QR Scanner -->
        <script src="https://cdn.jsdelivr.net/npm/jsqr@1.4.0/dist/jsQR.min.js"></script>
        <script>
            let isScanning = false;
            let videoStream = null;

            function toggleScanner() {
                const container = document.getElementById('scanner-container');
                const result = document.getElementById('result');

                container.classList.toggle('active');
                result.classList.remove('active');

                if (!container.classList.contains('active')) {
                    stopScanning();
                }
            }

            async function startScanning() {
                const startBtn = document.getElementById('start-button');
                const stopBtn = document.getElementById('stop-button');
                const status = document.getElementById('status');
                const result = document.getElementById('result');

                try {
                    status.style.display = 'block';
                    status.textContent = '⏳ Requesting camera access...';
                    status.className = 'status loading';

                    // Request camera
                    videoStream = await navigator.mediaDevices.getUserMedia({
                        video: { 
                            facingMode: 'environment',
                            width: { ideal: 1280 },
                            height: { ideal: 720 }
                        },
                        audio: false
                    });

                    const video = document.getElementById('video');
                    video.srcObject = videoStream;

                    // Wait for video to be ready
                    video.addEventListener('loadedmetadata', () => {
                        status.textContent = '✅ Camera ready! Point at QR code...';
                        status.className = 'status success';
                        isScanning = true;
                        startBtn.style.display = 'none';
                        stopBtn.style.display = 'block';
                        scan();
                    }, { once: true });

                } catch (error) {
                    console.error('Camera error:', error);
                    status.textContent = '❌ Camera Error: ' + error.message;
                    status.className = 'status error';
                    status.style.display = 'block';
                }
            }

            function stopScanning() {
                isScanning = false;

                if (videoStream) {
                    videoStream.getTracks().forEach(track => track.stop());
                    videoStream = null;
                }

                document.getElementById('start-button').style.display = 'block';
                document.getElementById('stop-button').style.display = 'none';
                document.getElementById('status').style.display = 'none';
            }

            function scan() {
                if (!isScanning) return;

                const video = document.getElementById('video');
                const canvas = document.getElementById('canvas');
                const canvasContext = canvas.getContext('2d');

                // Check if video is ready
                if (!video.videoWidth || !video.videoHeight) {
                    requestAnimationFrame(scan);
                    return;
                }

                // Set canvas size
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;

                // Draw video frame to canvas
                try {
                    canvasContext.drawImage(video, 0, 0, canvas.width, canvas.height);
                } catch (e) {
                    requestAnimationFrame(scan);
                    return;
                }

                // Get image data and scan for QR
                const imageData = canvasContext.getImageData(0, 0, canvas.width, canvas.height);
                const code = jsQR(imageData.data, imageData.width, imageData.height);

                if (code) {
                    // QR found!
                    isScanning = false;
                    stopScanning();

                    try {
                        const data = JSON.parse(code.data);
                        displayResult(data);
                    } catch (e) {
                        console.error('Invalid QR data:', e);
                    }
                } else {
                    // Continue scanning
                    requestAnimationFrame(scan);
                }
            }

            function displayResult(data) {
                const result = document.getElementById('result');
                const resultText = document.getElementById('result-text');

                resultText.innerHTML = `
                    <div style="line-height: 1.8;">
                        <strong style="font-size: 18px; color: #155724;">${data.title}</strong>
                        <br><br>
                        <strong>Author:</strong> ${data.author}<br>
                        <strong>Year:</strong> ${data.year}<br>
                        <strong>ISBN:</strong> ${data.isbn}<br>
                        <strong>Description:</strong> ${data.description}
                    </div>
                `;
                result.classList.add('active');
            }

            function downloadQR() {
                const link = document.createElement('a');
                link.href = '/generate-qr?download=true';
                link.download = 'book_qr_code.png';
                link.click();
            }
        </script>
    </body>
    </html>
    '''


# ========== ROUTE 2: Generate QR Code ==========
@app.route('/generate-qr')
def generate_qr():
    # Convert book info to JSON
    qr_data = json.dumps(BOOK_INFO)

    # Create QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)

    # Create image
    img = qr.make_image(fill_color="black", back_color="white")

    # Save to memory
    img_io = BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)

    return send_file(img_io, mimetype='image/png')


# ========== ROUTE 3: Book Info API ==========
@app.route('/book-info')
def book_info():
    return jsonify(BOOK_INFO)


# ========== Health Check ==========
@app.route('/health')
def health():
    return {'status': 'OK', 'timestamp': datetime.now().isoformat()}


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)