from http.server import BaseHTTPRequestHandler
import json
import sqlite3
import hashlib
from datetime import datetime
import random

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>MFH Store Dashboard</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #0a0a1a, #1a1a2e);
            color: white;
            margin: 0;
            padding: 20px;
            text-align: center;
        }
        .container {
            max-width: 800px;
            margin: 100px auto;
        }
        h1 {
            color: #0066ff;
            font-size: 2.5rem;
        }
        .btn {
            display: inline-block;
            background: linear-gradient(45deg, #0066ff, #8a2be2);
            color: white;
            padding: 15px 30px;
            border-radius: 50px;
            text-decoration: none;
            font-weight: bold;
            margin: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 MFH STORE DASHBOARD</h1>
        <p>Dashboard online untuk semua seller</p>
        
        <div style="margin: 40px 0;">
            <a href="/dashboard" class="btn">📊 Seller Login</a>
            <a href="/admin" class="btn">🔐 Admin Login</a>
            <a href="/api/ping" class="btn">🔧 Test API</a>
        </div>
        
        <div style="color: #aaa; margin-top: 50px;">
            <p>Domain: mfhstoreid.vercel.app</p>
            <p>Support: 0819-9859-3873</p>
        </div>
    </div>
</body>
</html>'''
            
            self.wfile.write(html.encode())
        
        elif self.path == '/api/ping':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                'status': 'online',
                'service': 'MFH Store Dashboard',
                'timestamp': datetime.now().isoformat(),
                'url': 'mfhstoreid.vercel.app'
            }
            self.wfile.write(json.dumps(response).encode())
        
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')
    
    def do_POST(self):
        if self.path == '/api/webhook':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode())
                order_id = f"MFH{datetime.now().strftime('%Y%m%d%H%M%S')}"
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                
                response = {
                    'success': True,
                    'order_id': order_id,
                    'message': 'Order diterima di cloud dashboard',
                    'data': data
                }
                self.wfile.write(json.dumps(response).encode())
            except Exception as e:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode())

def main():
    pass

if __name__ == "__main__":
    main()
