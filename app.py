from flask import Flask, send_file, jsonify
import qrcode
import json
from io import BytesIO

app = Flask(__name__)

BOOK_INFO = {
    "title": "Không Gia Đình",
    "author": "Hector Malot",
    "year": 1878,
    "description": "Tiểu thuyết cảm động về những đứa trẻ bất hạnh",
    "isbn": "978-6-04-009-099-9",
    "language": "Vietnamese"
}


@app.route('/')
def index():
    return '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>QR Book Scanner</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        }
        h1 { text-align: center; margin-bottom: 30px; color: #333; }
        .qr-box {
            text-align: center;
            background: #f5f5f5;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
        }
        #qr-img {
            max-width: 250px;
            border: 3px solid #667eea;
            padding: 10px;
            border-radius: 8px;
            background: white;
        }
        .btn {
            width: 100%;
            padding: 15px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            margin-bottom: 10px;
            transition: 0.3s;
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .btn-danger {
            background: #ff6b6b;
            color: white;
            display: none;
        }
        .btn:hover { transform: scale(1.02); }

        video {
            width: 100%;
            max-width: 100%;
            background: #000;
            border-radius: 8px;
            margin: 20px 0;
            display: block;
        }

        canvas { display: none; }

        .status {
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
            text-align: center;
            font-weight: bold;
            display: none;
        }
        .status.info {
            background: #e7f3ff;
            color: #004085;
            display: block;
        }
        .status.success {
            background: #d4edda;
            color: #155724;
            display: block;
        }
        .status.error {
            background: #f8d7da;
            color: #721c24;
            display: block;
        }

        .result {
            background: #d4edda;
            color: #155724;
            padding: 15px;
            border-radius: 8px;
            margin-top: 15px;
            display: none;
            border: 1px solid #c3e6cb;
        }
        .result.show { display: block; }
        .result strong { display: block; margin-bottom: 10px; font-size: 16px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📚 QR Book Scanner</h1>

        <div class="qr-box">
            <h3>Step 1: QR Code</h3>
            <img id="qr-img" src="/qr" alt="QR Code">
        </div>

        <h3>Step 2: Scan QR</h3>
        <button class="btn btn-primary" id="btn-start" onclick="startCam()">📱 Start Camera</button>
        <button class="btn btn-danger" id="btn-stop" onclick="stopCam()">⏹ Stop Camera</button>

        <div id="status" class="status info">⏳ Ready to start</div>

        <video id="video" playsinline autoplay muted></video>
        <canvas id="canvas"></canvas>

        <div id="result" class="result">
            <strong>✅ Scanned!</strong>
            <div id="result-text"></div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/jsqr@1.4.0/dist/jsQR.min.js"></script>
    <script>
        let stream = null;
        let scanning = false;

        async function startCam() {
            try {
                document.getElementById('status').innerHTML = '⏳ Requesting camera...';
                document.getElementById('status').className = 'status info';

                // Get camera
                stream = await navigator.mediaDevices.getUserMedia({
                    video: { facingMode: 'environment' }
                });

                const video = document.getElementById('video');
                video.srcObject = stream;

                // Wait for video to play
                video.onplay = function() {
                    document.getElementById('status').innerHTML = '✅ Camera ready! Point at QR code';
                    document.getElementById('status').className = 'status success';
                    document.getElementById('btn-start').style.display = 'none';
                    document.getElementById('btn-stop').style.display = 'block';
                    scanning = true;
                    scan();
                };

            } catch(err) {
                document.getElementById('status').innerHTML = '❌ Camera error: ' + err.message;
                document.getElementById('status').className = 'status error';
                console.error('Camera error:', err);
            }
        }

        function stopCam() {
            scanning = false;
            if (stream) {
                stream.getTracks().forEach(track => track.stop());
                stream = null;
            }
            document.getElementById('btn-start').style.display = 'block';
            document.getElementById('btn-stop').style.display = 'none';
            document.getElementById('status').innerHTML = '⏹ Camera stopped';
            document.getElementById('status').className = 'status info';
        }

        function scan() {
            if (!scanning) return;

            const video = document.getElementById('video');
            const canvas = document.getElementById('canvas');
            const ctx = canvas.getContext('2d');

            if (video.readyState === video.HAVE_ENOUGH_DATA) {
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                ctx.drawImage(video, 0, 0);

                const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
                const code = jsQR(imageData.data, canvas.width, canvas.height);

                if (code) {
                    try {
                        const data = JSON.parse(code.data);
                        showResult(data);
                        return;
                    } catch (e) {
                        console.log('Invalid QR data');
                    }
                }
            }

            requestAnimationFrame(scan);
        }

        function showResult(data) {
            scanning = false;
            stopCam();

            const resultDiv = document.getElementById('result');
            const resultText = document.getElementById('result-text');

            resultText.innerHTML = `
                <strong style="font-size: 18px;">${data.title}</strong>
                <div style="margin-top: 10px; line-height: 1.8;">
                    Author: ${data.author}<br>
                    Year: ${data.year}<br>
                    ISBN: ${data.isbn}<br>
                    <em>${data.description}</em>
                </div>
            `;
            resultDiv.classList.add('show');
        }
    </script>
</body>
</html>
    '''


@app.route('/qr')
def qr():
    qr_data = json.dumps(BOOK_INFO)
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    img_io = BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)

    return send_file(img_io, mimetype='image/png')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)