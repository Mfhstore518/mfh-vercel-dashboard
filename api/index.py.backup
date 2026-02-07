from http.server import BaseHTTPRequestHandler
import json
import sqlite3
import hashlib
from datetime import datetime
import random
import os
import urllib.parse

# In-memory database untuk demo
orders_db = []
users_db = [
    {"username": "admin", "password": "admin123", "role": "admin"},
    {"username": "seller1", "password": "seller123", "role": "seller", "shop": "Toko Digital 1"},
    {"username": "seller2", "password": "seller123", "role": "seller", "shop": "Toko Digital 2"}
]

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path
        
        # API Routes
        if path == '/api/ping':
            self.send_json({
                "status": "online",
                "service": "MFH Store Cloud Dashboard",
                "version": "2.0",
                "timestamp": datetime.now().isoformat(),
                "url": "mfh-vercel-dashboard.vercel.app"
            })
        
        elif path == '/api/stats':
            self.send_json({
                "total_orders": len(orders_db),
                "pending_orders": len([o for o in orders_db if o.get('status') == 'pending']),
                "completed_orders": len([o for o in orders_db if o.get('status') == 'completed']),
                "total_sellers": len([u for u in users_db if u.get('role') == 'seller']),
                "revenue_today": sum([o.get('amount', 0) for o in orders_db if o.get('date', '').startswith(datetime.now().strftime('%Y-%m-%d'))])
            })
        
        elif path == '/api/orders':
            self.send_json(orders_db)
        
        elif path == '/api/sellers':
            sellers = [u for u in users_db if u.get('role') == 'seller']
            self.send_json(sellers)
        
        # HTML Pages
        elif path == '/':
            self.send_html(self.get_homepage())
        
        elif path == '/dashboard':
            self.send_html(self.get_dashboard_page())
        
        elif path == '/seller':
            self.send_html(self.get_seller_login())
        
        elif path == '/seller/dashboard':
            self.send_html(self.get_seller_dashboard())
        
        elif path == '/admin':
            self.send_html(self.get_admin_login())
        
        elif path == '/admin/panel':
            self.send_html(self.get_admin_panel())
        
        else:
            self.send_json({"error": "Not found"}, 404)
    
    def do_POST(self):
        path = self.path
        
        if path == '/api/login':
            content_length = int(self.headers['Content-Length'])
            data = json.loads(self.rfile.read(content_length).decode())
            
            username = data.get('username')
            password = data.get('password')
            
            user = next((u for u in users_db if u['username'] == username and u['password'] == password), None)
            
            if user:
                self.send_json({
                    "success": True,
                    "user": {
                        "username": user['username'],
                        "role": user['role'],
                        "shop": user.get('shop', '')
                    },
                    "token": hashlib.md5(f"{username}{datetime.now()}".encode()).hexdigest()
                })
            else:
                self.send_json({"success": False, "error": "Invalid credentials"}, 401)
        
        elif path == '/api/webhook':
            content_length = int(self.headers['Content-Length'])
            data = json.loads(self.rfile.read(content_length).decode())
            
            order_id = f"MFH{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(100,999)}"
            
            order = {
                "order_id": order_id,
                "product": data.get('product', 'Unknown'),
                "customer": data.get('customer', 'Unknown'),
                "phone": data.get('phone', ''),
                "email": data.get('email', ''),
                "amount": data.get('amount', 0),
                "status": "pending",
                "notes": data.get('notes', ''),
                "seller": data.get('seller', 'seller1'),
                "date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "location": "Indonesia"
            }
            
            orders_db.append(order)
            
            self.send_json({
                "success": True,
                "order_id": order_id,
                "message": f"Order diterima oleh {order['seller']}",
                "data": order
            })
        
        elif path == '/api/order/update':
            content_length = int(self.headers['Content-Length'])
            data = json.loads(self.rfile.read(content_length).decode())
            
            order_id = data.get('order_id')
            status = data.get('status')
            
            for order in orders_db:
                if order['order_id'] == order_id:
                    order['status'] = status
                    break
            
            self.send_json({"success": True, "message": f"Order {order_id} updated to {status}"})
        
        else:
            self.send_json({"error": "Not found"}, 404)
    
    # ========== HTML PAGES ==========
    def get_homepage(self):
        return '''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MFH Store Cloud Dashboard</title>
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
            margin: 50px auto;
        }
        h1 {
            color: #0066ff;
            font-size: 2.5rem;
            margin-bottom: 10px;
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
            font-size: 1.1rem;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin: 30px 0;
        }
        .stat-card {
            background: rgba(255,255,255,0.05);
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #0066ff;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌐 MFH STORE CLOUD DASHBOARD</h1>
        <p>Dashboard Online untuk Semua Seller - Akses dari HP Manapun</p>
        
        <div class="stats" id="stats">
            <!-- Stats will be loaded by JS -->
        </div>
        
        <div style="margin: 40px 0;">
            <a href="/seller" class="btn">👨‍💼 Login Seller</a>
            <a href="/admin" class="btn">🔐 Login Admin</a>
            <a href="/dashboard" class="btn">📊 Live Dashboard</a>
            <a href="/api/ping" class="btn">🔧 Test API</a>
        </div>
        
        <div style="color: #aaa; margin-top: 50px;">
            <p>📞 Support: 0819-9859-3873 | 🕐 24/7 Online</p>
            <p>🔗 URL: mfh-vercel-dashboard.vercel.app</p>
        </div>
    </div>
    
    <script>
        // Load stats
        fetch('/api/stats')
            .then(r => r.json())
            .then(stats => {
                document.getElementById('stats').innerHTML = `
                    <div class="stat-card">
                        <h3>Total Orders</h3>
                        <h2>${stats.total_orders}</h2>
                    </div>
                    <div class="stat-card">
                        <h3>Pending</h3>
                        <h2 style="color: #ffcc00;">${stats.pending_orders}</h2>
                    </div>
                    <div class="stat-card">
                        <h3>Completed</h3>
                        <h2 style="color: #00ffaa;">${stats.completed_orders}</h2>
                    </div>
                    <div class="stat-card">
                        <h3>Active Sellers</h3>
                        <h2>${stats.total_sellers}</h2>
                    </div>
                `;
            });
    </script>
</body>
</html>'''
    
    def get_seller_login(self):
        return '''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Seller Login - MFH Store</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #0a0a1a, #1a1a2e);
            color: white;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }
        .login-box {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 40px;
            width: 90%;
            max-width: 400px;
            border: 1px solid rgba(255,255,255,0.2);
        }
        input {
            width: 100%;
            padding: 15px;
            margin: 10px 0;
            background: rgba(255,255,255,0.1);
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 10px;
            color: white;
            font-size: 1rem;
        }
        button {
            width: 100%;
            padding: 15px;
            background: linear-gradient(45deg, #0066ff, #8a2be2);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 1rem;
            font-weight: bold;
            cursor: pointer;
            margin-top: 20px;
        }
        .seller-info {
            margin-top: 20px;
            padding: 15px;
            background: rgba(0,102,255,0.1);
            border-radius: 10px;
            font-size: 0.9rem;
        }
    </style>
</head>
<body>
    <div class="login-box">
        <h2 style="text-align: center; color: #0066ff;">SELLER LOGIN</h2>
        <form id="loginForm">
            <input type="text" id="username" placeholder="Username" required>
            <input type="password" id="password" placeholder="Password" required>
            <button type="submit">LOGIN</button>
        </form>
        
        <div class="seller-info">
            <p><strong>Demo Seller Accounts:</strong></p>
            <p>👤 seller1 / seller123</p>
            <p>👤 seller2 / seller123</p>
            <p>👤 admin / admin123</p>
        </div>
    </div>
    
    <script>
        document.getElementById('loginForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            
            const response = await fetch('/api/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username, password})
            });
            
            const data = await response.json();
            
            if(data.success) {
                localStorage.setItem('mfh_user', JSON.stringify(data.user));
                localStorage.setItem('mfh_token', data.token);
                
                if(data.user.role === 'seller') {
                    window.location.href = '/seller/dashboard';
                } else {
                    window.location.href = '/admin/panel';
                }
            } else {
                alert('Login gagal! Cek username/password.');
            }
        });
        
        // Auto-fill for testing
        document.getElementById('username').value = 'seller1';
        document.getElementById('password').value = 'seller123';
    </script>
</body>
</html>'''
    
    def get_seller_dashboard(self):
        return '''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Seller Dashboard - MFH Store</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #0a0a1a;
            color: white;
            margin: 0;
            padding: 20px;
        }
        .header {
            background: linear-gradient(90deg, #0066ff, #8a2be2);
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .order-card {
            background: rgba(255,255,255,0.05);
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 10px;
            border-left: 4px solid #0066ff;
        }
        .status-pending { color: #ffcc00; }
        .status-completed { color: #00ffaa; }
        .btn {
            background: #0066ff;
            color: white;
            border: none;
            padding: 8px 15px;
            border-radius: 5px;
            cursor: pointer;
            margin: 5px;
        }
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1>📊 Seller Dashboard</h1>
            <p id="seller-name">Loading...</p>
        </div>
        <button class="btn" onclick="logout()">Logout</button>
    </div>
    
    <div id="orders-container">
        <p>Loading orders...</p>
    </div>
    
    <script>
        // Check login
        const user = JSON.parse(localStorage.getItem('mfh_user') || 'null');
        if(!user || user.role !== 'seller') {
            window.location.href = '/seller';
        }
        
        document.getElementById('seller-name').textContent = `${user.shop} (${user.username})`;
        
        async function loadOrders() {
            const response = await fetch('/api/orders');
            const orders = await response.json();
            
            // Filter orders for this seller
            const sellerOrders = orders.filter(o => o.seller === user.username);
            
            let html = '<h2>📦 Your Orders</h2>';
            
            if(sellerOrders.length === 0) {
                html += '<p>No orders yet</p>';
            } else {
                sellerOrders.forEach(order => {
                    html += `
                    <div class="order-card">
                        <strong>${order.product}</strong>
                        <p>👤 ${order.customer} | 📱 ${order.phone}</p>
                        <p>🆔 ${order.order_id} | 📅 ${order.date}</p>
                        <p>Status: <span class="status-${order.status}">${order.status}</span></p>
                        <button class="btn" onclick="updateStatus('${order.order_id}', 'processing')">Process</button>
                        <button class="btn" onclick="updateStatus('${order.order_id}', 'completed')">Complete</button>
                    </div>
                    `;
                });
            }
            
            document.getElementById('orders-container').innerHTML = html;
        }
        
        async function updateStatus(orderId, status) {
            await fetch('/api/order/update', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({order_id: orderId, status: status})
            });
            
            loadOrders();
        }
        
        function logout() {
            localStorage.clear();
            window.location.href = '/';
        }
        
        // Auto refresh every 30 seconds
        setInterval(loadOrders, 30000);
        
        loadOrders();
    </script>
</body>
</html>'''
    
    def get_admin_panel(self):
        return '''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Panel - MFH Store</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #0a0a1a;
            color: white;
            margin: 0;
            padding: 20px;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .stat-card {
            background: rgba(255,255,255,0.05);
            padding: 20px;
            border-radius: 10px;
        }
        .order-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        .order-table th, .order-table td {
            padding: 10px;
            border: 1px solid rgba(255,255,255,0.1);
            text-align: left;
        }
    </style>
</head>
<body>
    <h1>🔐 Admin Panel</h1>
    
    <div class="stats-grid" id="stats-grid">
        <!-- Stats loaded by JS -->
    </div>
    
    <h2>📋 All Orders</h2>
    <div id="orders-table">
        Loading...
    </div>
    
    <script>
        async function loadStats() {
            const response = await fetch('/api/stats');
            const stats = await response.json();
            
            document.getElementById('stats-grid').innerHTML = `
                <div class="stat-card">
                    <h3>Total Orders</h3>
                    <h2>${stats.total_orders}</h2>
                </div>
                <div class="stat-card">
                    <h3>Pending</h3>
                    <h2 style="color: #ffcc00;">${stats.pending_orders}</h2>
                </div>
                <div class="stat-card">
                    <h3>Completed</h3>
                    <h2 style="color: #00ffaa;">${stats.completed_orders}</h2>
                </div>
                <div class="stat-card">
                    <h3>Revenue Today</h3>
                    <h2 style="color: #ff66ff;">Rp ${stats.revenue_today.toLocaleString()}</h2>
                </div>
            `;
        }
        
        async function loadOrders() {
            const response = await fetch('/api/orders');
            const orders = await response.json();
            
            let html = '<table class="order-table">';
            html += '<tr><th>Order ID</th><th>Product</th><th>Customer</th><th>Seller</th><th>Status</th><th>Date</th></tr>';
            
            orders.forEach(order => {
                html += `
                <tr>
                    <td>${order.order_id}</td>
                    <td>${order.product}</td>
                    <td>${order.customer}</td>
                    <td>${order.seller}</td>
                    <td>${order.status}</td>
                    <td>${order.date}</td>
                </tr>
                `;
            });
            
            html += '</table>';
            document.getElementById('orders-table').innerHTML = html;
        }
        
        loadStats();
        loadOrders();
        setInterval(() => {
            loadStats();
            loadOrders();
        }, 10000);
    </script>
</body>
</html>'''
    
    def get_dashboard_page(self):
        return self.get_homepage()
    
    def get_admin_login(self):
        return self.get_seller_login().replace("SELLER LOGIN", "ADMIN LOGIN")
    
    # ========== HELPER METHODS ==========
    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def send_html(self, html):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())

def main():
    pass

if __name__ == "__main__":
    main()
