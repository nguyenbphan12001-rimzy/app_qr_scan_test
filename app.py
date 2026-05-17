from flask import Flask, render_template, send_file
import qrcode
import json
from io import BytesIO
import os

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


# ========== ROUTE 1: Hiển thị trang chính ==========
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
            .info-label {
                font-weight: bold;
                color: #333;
            }
            .info-value {
                color: #666;
            }
            .scanner-button {
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
            .scanner-button:hover {
                transform: scale(1.05);
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
            }
            .download-button:hover {gi
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
                border-radius: 8px;
                margin-bottom: 10px;
            }
            .result {
                display: none;
                background: #d4edda;
                color: #155724;
                padding: 15px;
                border-radius: 8px;
                margin-top: 10px;
            }
            .result.active {
                display: block;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📚 QR Book Scanner</h1>
            <p class="subtitle">Scan the QR code below to see book information</p>

            <!-- QR Code Section -->
            <div class="qr-section">
                <h2>Step 1: View QR Code</h2>
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
            <button class="scanner-button" onclick="toggleScanner()">
                📱 Step 2: Scan QR Code on Phone
            </button>

            <div id="scanner-container" class="scanner-container">
                <p style="margin-bottom: 10px;">Open this page on your phone and click below</p>
                <button class="scanner-button" onclick="startScanning()" style="margin-bottom: 10px;">
                    🎥 Open Camera
                </button>
                <video id="video" width="100%"></video>
                <canvas id="canvas" style="display: none;"></canvas>
                <div id="result" class="result">
                    <strong>✅ Scanned Successfully!</strong>
                    <div id="result-text" style="margin-top: 10px;"></div>
                </div>
            </div>
        </div>

        <!-- Thư viện QR Scanner -->
        <script src="https://cdn.jsdelivr.net/npm/jsqr@1.4.0/dist/jsQR.min.js"></script>
        <script>
            let isScanning = false;

            function toggleScanner() {
                const container = document.getElementById('scanner-container');
                container.classList.toggle('active');
            }

            async function startScanning() {
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({
                        video: { facingMode: 'environment' }
                    });
                    const video = document.getElementById('video');
                    video.srcObject = stream;
                    isScanning = true;
                    scan();
                } catch (error) {
                    alert('Cannot access camera: ' + error.message);
                }
            }

            function scan() {
                if (!isScanning) return;

                const video = document.getElementById('video');
                const canvas = document.getElementById('canvas');
                const canvasContext = canvas.getContext('2d');

                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                canvasContext.drawImage(video, 0, 0, canvas.width, canvas.height);

                const imageData = canvasContext.getImageData(0, 0, canvas.width, canvas.height);
                const code = jsQR(imageData.data, imageData.width, imageData.height);

                if (code) {
                    isScanning = false;
                    video.srcObject.getTracks().forEach(track => track.stop());

                    // Parse QR data
                    const data = JSON.parse(code.data);

                    const result = document.getElementById('result');
                    const resultText = document.getElementById('result-text');

                    resultText.innerHTML = `
                        <strong>${data.title}</strong><br>
                        Author: ${data.author}<br>
                        Year: ${data.year}<br>
                        ISBN: ${data.isbn}<br>
                        <em>${data.description}</em>
                    `;
                    result.classList.add('active');
                }

                requestAnimationFrame(scan);
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


# ========== ROUTE 2: Tạo & Trả về QR Code ==========
@app.route('/generate-qr')
def generate_qr():
    # Chuyển thông tin sách thành JSON
    qr_data = json.dumps(BOOK_INFO)

    # Tạo QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)

    # Tạo image
    img = qr.make_image(fill_color="black", back_color="white")

    # Lưu vào memory (không cần save file)
    img_io = BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)

    # Return ảnh
    return send_file(img_io, mimetype='image/png')


# ========== ROUTE 3: Trang Book Info ==========
@app.route('/book-info')
def book_info():
    return {
        'title': BOOK_INFO['title'],
        'author': BOOK_INFO['author'],
        'year': BOOK_INFO['year'],
        'isbn': BOOK_INFO['isbn'],
        'description': BOOK_INFO['description'],
        'language': BOOK_INFO['language']
    }


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)