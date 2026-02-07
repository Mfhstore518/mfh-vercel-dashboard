from http.server import BaseHTTPRequestHandler
import json
import hashlib
from datetime import datetime
import random

# Import user management module
import sys
sys.path.insert(0, '/tmp')
from users import *

# Orders database
orders_db = []

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path
        
        # ========== API ROUTES ==========
        if path == '/api/ping':
            self.send_json({
                "status": "online",
                "service": "MFH Store Cloud Dashboard v3.0",
                "timestamp": datetime.now().isoformat(),
                "users_count": len(get_all_users()),
                "orders_count": len(orders_db)
            })
        
        elif path == '/api/stats':
            active_users = [u for u in get_all_users() if u["status"] == "active"]
            sellers = [u for u in active_users if u["role"] == "seller"]
            
            self.send_json({
                "total_orders": len(orders_db),
                "pending_orders": len([o for o in orders_db if o.get('status') == 'pending']),
                "completed_orders": len([o for o in orders_db if o.get('status') == 'completed']),
                "total_users": len(active_users),
                "total_sellers": len(sellers),
                "total_admins": len([u for u in active_users if u["role"] == "admin"]),
                "revenue_today": sum([o.get('amount', 0) for o in orders_db if o.get('date', '').startswith(datetime.now().strftime('%Y-%m-%d'))])
            })
        
        elif path == '/api/orders':
            self.send_json(orders_db)
        
        elif path == '/api/users':
            # Only admin can access
            self.send_json([u for u in get_all_users() if u["status"] == "active"])
        
        elif path == '/api/users/sellers':
            sellers = [u for u in get_all_users() if u["role"] == "seller" and u["status"] == "active"]
            self.send_json(sellers)
        
        # ========== HTML PAGES ==========
        elif path == '/':
            self.send_html(self.get_homepage())
        
        elif path == '/admin/users':
            self.send_html(self.get_user_management_page())
        
        elif path == '/admin/create-user':
            self.send_html(self.get_create_user_page())
        
        elif path.startswith('/admin/edit-user/'):
            self.send_html(self.get_edit_user_page())
        
        else:
            # Fallback to previous routes
            self.handle_legacy_routes(path)
    
    def do_POST(self):
        path = self.path
        
        if path == '/api/login':
            content_length = int(self.headers['Content-Length'])
            data = json.loads(self.rfile.read(content_length).decode())
            
            user = authenticate_user(data.get('username'), data.get('password'))
            
            if user and user["status"] == "active":
                self.send_json({
                    "success": True,
                    "user": {
                        "id": user["id"],
                        "username": user["username"],
                        "role": user["role"],
                        "shop_name": user.get("shop_name", ""),
                        "phone": user.get("phone", ""),
                        "email": user.get("email", "")
                    },
                    "token": user["token"]
                })
            else:
                self.send_json({"success": False, "error": "Invalid credentials or inactive account"}, 401)
        
        elif path == '/api/users/create':
            content_length = int(self.headers['Content-Length'])
            data = json.loads(self.rfile.read(content_length).decode())
            
            # Check if username exists
            if get_user_by_username(data.get('username')):
                self.send_json({"success": False, "error": "Username already exists"}, 400)
                return
            
            new_user = create_user(data)
            self.send_json({"success": True, "user": new_user})
        
        elif path == '/api/users/update':
            content_length = int(self.headers['Content-Length'])
            data = json.loads(self.rfile.read(content_length).decode())
            
            user_id = data.get('id')
            updated_user = update_user(user_id, data)
            
            if updated_user:
                self.send_json({"success": True, "user": updated_user})
            else:
                self.send_json({"success": False, "error": "User not found"}, 404)
        
        elif path == '/api/users/delete':
            content_length = int(self.headers['Content-Length'])
            data = json.loads(self.rfile.read(content_length).decode())
            
            user_id = data.get('id')
            if delete_user(user_id):
                self.send_json({"success": True, "message": "User deactivated"})
            else:
                self.send_json({"success": False, "error": "User not found"}, 404)
        
        elif path == '/api/webhook':
            self.handle_webhook()
        
        elif path == '/api/order/update':
            self.handle_order_update()
        
        else:
            self.send_json({"error": "Not found"}, 404)
    
    # ========== HTML PAGES ==========
    def get_user_management_page(self):
        return '''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>User Management - MFH Store</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #0a0a1a;
            color: white;
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
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
        .btn {
            background: #0066ff;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            margin: 5px;
        }
        .btn-danger { background: #ff4444; }
        .btn-success { background: #00aa00; }
        .user-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            background: rgba(255,255,255,0.05);
        }
        .user-table th, .user-table td {
            padding: 12px;
            border: 1px solid rgba(255,255,255,0.1);
            text-align: left;
        }
        .user-table tr:hover {
            background: rgba(255,255,255,0.1);
        }
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.8);
            justify-content: center;
            align-items: center;
            z-index: 1000;
        }
        .modal-content {
            background: #1a1a2e;
            padding: 30px;
            border-radius: 15px;
            width: 90%;
            max-width: 500px;
            border: 1px solid #0066ff;
        }
        .form-group {
            margin-bottom: 15px;
        }
        .form-group label {
            display: block;
            margin-bottom: 5px;
            color: #aaa;
        }
        .form-group input, .form-group select {
            width: 100%;
            padding: 10px;
            background: rgba(255,255,255,0.1);
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 5px;
            color: white;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <h1>👥 User Management</h1>
                <p>Manage admin & seller accounts</p>
            </div>
            <div>
                <a href="/" class="btn">🏠 Home</a>
                <a href="/admin/create-user" class="btn btn-success">➕ Add New User</a>
            </div>
        </div>
        
        <div id="users-container">
            <p>Loading users...</p>
        </div>
    </div>
    
    <!-- Edit User Modal -->
    <div id="editModal" class="modal">
        <div class="modal-content">
            <h2>✏️ Edit User</h2>
            <form id="editUserForm">
                <input type="hidden" id="editUserId">
                
                <div class="form-group">
                    <label>Username</label>
                    <input type="text" id="editUsername" readonly>
                </div>
                
                <div class="form-group">
                    <label>Role</label>
                    <select id="editRole">
                        <option value="admin">Admin</option>
                        <option value="seller">Seller</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label>Shop Name</label>
                    <input type="text" id="editShopName" placeholder="Shop name (for sellers)">
                </div>
                
                <div class="form-group">
                    <label>Phone</label>
                    <input type="text" id="editPhone" placeholder="0812xxxxxxx">
                </div>
                
                <div class="form-group">
                    <label>Email</label>
                    <input type="email" id="editEmail" placeholder="user@example.com">
                </div>
                
                <div class="form-group">
                    <label>New Password (leave empty to keep current)</label>
                    <input type="password" id="editPassword" placeholder="New password">
                </div>
                
                <div class="form-group">
                    <label>Status</label>
                    <select id="editStatus">
                        <option value="active">Active</option>
                        <option value="inactive">Inactive</option>
                    </select>
                </div>
                
                <div style="margin-top: 20px; display: flex; gap: 10px;">
                    <button type="submit" class="btn">💾 Save Changes</button>
                    <button type="button" class="btn btn-danger" onclick="closeModal()">❌ Cancel</button>
                </div>
            </form>
        </div>
    </div>
    
    <script>
        async function loadUsers() {
            try {
                const response = await fetch('/api/users');
                const users = await response.json();
                
                let html = `
                <table class="user-table">
                    <tr>
                        <th>ID</th>
                        <th>Username</th>
                        <th>Role</th>
                        <th>Shop Name</th>
                        <th>Phone</th>
                        <th>Status</th>
                        <th>Created</th>
                        <th>Actions</th>
                    </tr>
                `;
                
                users.forEach(user => {
                    html += `
                    <tr>
                        <td>${user.id}</td>
                        <td><strong>${user.username}</strong></td>
                        <td><span style="padding: 3px 8px; border-radius: 10px; background: ${user.role === 'admin' ? '#0066ff40' : '#00ffaa40'}; color: ${user.role === 'admin' ? '#0066ff' : '#00ffaa'}">${user.role}</span></td>
                        <td>${user.shop_name || '-'}</td>
                        <td>${user.phone || '-'}</td>
                        <td><span style="color: ${user.status === 'active' ? '#00ffaa' : '#ff4444'}">${user.status}</span></td>
                        <td>${user.created_at}</td>
                        <td>
                            <button class="btn" onclick="editUser(${user.id})">✏️ Edit</button>
                            <button class="btn btn-danger" onclick="deleteUser(${user.id}, '${user.username}')">🗑️ Delete</button>
                        </td>
                    </tr>
                    `;
                });
                
                html += '</table>';
                document.getElementById('users-container').innerHTML = html;
            } catch (error) {
                document.getElementById('users-container').innerHTML = '<p style="color: #ff4444;">Error loading users</p>';
            }
        }
        
        function editUser(userId) {
            fetch(`/api/users`)
                .then(r => r.json())
                .then(users => {
                    const user = users.find(u => u.id === userId);
                    if (user) {
                        document.getElementById('editUserId').value = user.id;
                        document.getElementById('editUsername').value = user.username;
                        document.getElementById('editRole').value = user.role;
                        document.getElementById('editShopName').value = user.shop_name || '';
                        document.getElementById('editPhone').value = user.phone || '';
                        document.getElementById('editEmail').value = user.email || '';
                        document.getElementById('editStatus').value = user.status;
                        
                        document.getElementById('editModal').style.display = 'flex';
                    }
                });
        }
        
        function deleteUser(userId, username) {
            if (confirm(`Are you sure you want to delete user "${username}"?`)) {
                fetch('/api/users/delete', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({id: userId})
                })
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        alert('User deleted successfully!');
                        loadUsers();
                    }
                });
            }
        }
        
        function closeModal() {
            document.getElementById('editModal').style.display = 'none';
        }
        
        document.getElementById('editUserForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const userData = {
                id: parseInt(document.getElementById('editUserId').value),
                role: document.getElementById('editRole').value,
                shop_name: document.getElementById('editShopName').value,
                phone: document.getElementById('editPhone').value,
                email: document.getElementById('editEmail').value,
                status: document.getElementById('editStatus').value
            };
            
            const password = document.getElementById('editPassword').value;
            if (password) {
                userData.password = password;
            }
            
            fetch('/api/users/update', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(userData)
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    alert('User updated successfully!');
                    closeModal();
                    loadUsers();
                }
            });
        });
        
        // Close modal when clicking outside
        document.getElementById('editModal').addEventListener('click', function(e) {
            if (e.target === this) {
                closeModal();
            }
        });
        
        // Load users on page load
        loadUsers();
        // Auto refresh every 30 seconds
        setInterval(loadUsers, 30000);
    </script>
</body>
</html>'''
    
    def get_create_user_page(self):
        return '''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Create User - MFH Store</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #0a0a1a;
            color: white;
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 600px;
            margin: 50px auto;
            background: rgba(255,255,255,0.05);
            padding: 30px;
            border-radius: 15px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        .form-group {
            margin-bottom: 20px;
        }
        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: #aaa;
            font-weight: bold;
        }
        .form-group input, .form-group select {
            width: 100%;
            padding: 12px;
            background: rgba(255,255,255,0.1);
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 8px;
            color: white;
            font-size: 1rem;
        }
        .btn {
            background: #0066ff;
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1rem;
            font-weight: bold;
            width: 100%;
            margin-top: 10px;
        }
        .btn:hover {
            background: #0055dd;
        }
        .btn-back {
            background: #666;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>👤 Create New User</h1>
        <p>Create new admin or seller account</p>
        
        <form id="createUserForm">
            <div class="form-group">
                <label>Username *</label>
                <input type="text" id="username" placeholder="Enter username" required>
            </div>
            
            <div class="form-group">
                <label>Password *</label>
                <input type="password" id="password" placeholder="Enter password" required>
            </div>
            
            <div class="form-group">
                <label>Confirm Password *</label>
                <input type="password" id="confirmPassword" placeholder="Confirm password" required>
            </div>
            
            <div class="form-group">
                <label>Role *</label>
                <select id="role" required>
                    <option value="">Select role</option>
                    <option value="admin">Admin</option>
                    <option value="seller">Seller</option>
                </select>
            </div>
            
            <div class="form-group">
                <label>Shop Name (for sellers)</label>
                <input type="text" id="shopName" placeholder="Enter shop name">
            </div>
            
            <div class="form-group">
                <label>Phone Number</label>
                <input type="text" id="phone" placeholder="0812xxxxxxx">
            </div>
            
            <div class="form-group">
                <label>Email</label>
                <input type="email" id="email" placeholder="user@example.com">
            </div>
            
            <button type="submit" class="btn">➕ Create User</button>
        </form>
        
        <a href="/admin/users" class="btn btn-back">⬅️ Back to User Management</a>
        
        <div id="message" style="margin-top: 20px;"></div>
    </div>
    
    <script>
        document.getElementById('createUserForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirmPassword').value;
            
            if (password !== confirmPassword) {
                showMessage('Passwords do not match!', 'error');
                return;
            }
            
            if (password.length < 6) {
                showMessage('Password must be at least 6 characters', 'error');
                return;
            }
            
            const userData = {
                username: username,
                password: password,
                role: document.getElementById('role').value,
                shop_name: document.getElementById('shopName').value || '',
                phone: document.getElementById('phone').value || '',
                email: document.getElementById('email').value || ''
            };
            
            try {
                const response = await fetch('/api/users/create', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(userData)
                });
                
                const data = await response.json();
                
                if (data.success) {
                    showMessage(`✅ User "${username}" created successfully! Default password: ${password}`, 'success');
                    document.getElementById('createUserForm').reset();
                    
                    // Auto generate random password suggestion
                    setTimeout(() => {
                        document.getElementById('password').value = generatePassword();
                        document.getElementById('confirmPassword').value = document.getElementById('password').value;
                    }, 2000);
                } else {
                    showMessage(`❌ Error: ${data.error}`, 'error');
                }
            } catch (error) {
                showMessage('Network error. Please try again.', 'error');
            }
        });
        
        function generatePassword() {
            const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
            let password = '';
            for (let i = 0; i < 8; i++) {
                password += chars.charAt(Math.floor(Math.random() * chars.length));
            }
            return password;
        }
        
        function showMessage(text, type) {
            const messageDiv = document.getElementById('message');
            messageDiv.innerHTML = text;
            messageDiv.style.color = type === 'success' ? '#00ffaa' : '#ff4444';
            messageDiv.style.padding = '10px';
            messageDiv.style.borderRadius = '5px';
            messageDiv.style.background = type === 'success' ? '#00ffaa20' : '#ff444420';
            
            if (type === 'success') {
                setTimeout(() => {
                    messageDiv.innerHTML = '';
                }, 5000);
            }
        }
        
        // Auto generate password on page load
        document.getElementById('password').value = generatePassword();
        document.getElementById('confirmPassword').value = document.getElementById('password').value;
        document.getElementById('role').value = 'seller';
        document.getElementById('shopName').value = 'Toko Digital';
    </script>
</body>
</html>'''
    
    def get_edit_user_page(self):
        return self.get_create_user_page().replace("Create New User", "Edit User")
    
    def get_homepage(self):
        return '''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MFH Store Cloud Dashboard</title>
    <style>
        body { font-family: Arial; background: #0a0a1a; color: white; margin: 0; padding: 20px; text-align: center; }
        .container { max-width: 800px; margin: 50px auto; }
        h1 { color: #0066ff; font-size: 2.5rem; }
        .btn { display: inline-block; background: linear-gradient(45deg, #0066ff, #8a2be2); color: white; padding: 15px 30px; border-radius: 50px; text-decoration: none; font-weight: bold; margin: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌐 MFH STORE CLOUD DASHBOARD v3.0</h1>
        <p>Complete User Management System</p>
        
        <div style="margin: 40px 0;">
            <a href="/seller" class="btn">👨‍💼 Seller Login</a>
            <a href="/admin/users" class="btn">👥 User Management</a>
            <a href="/admin/create-user" class="btn">➕ Create User</a>
            <a href="/api/ping" class="btn">🔧 Test API</a>
        </div>
        
        <div style="color: #aaa; margin-top: 50px;">
            <p>🔗 URL: mfh-vercel-dashboard.vercel.app</p>
            <p>📞 Support: 0819-9859-3873</p>
        </div>
    </div>
</body>
</html>'''
    
    def handle_legacy_routes(self, path):
        """Handle legacy routes from previous version"""
        if path == '/dashboard':
            self.send_html(self.get_homepage())
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
    
    def get_seller_login(self):
        return '''<html><body><h1>Seller Login</h1><p>Redirecting...</p><script>window.location.href = '/seller';</script></body></html>'''
    
    def get_seller_dashboard(self):
        return '''<html><body><h1>Seller Dashboard</h1><p>Redirecting...</p><script>window.location.href = '/';</script></body></html>'''
    
    def get_admin_login(self):
        return '''<html><body><h1>Admin Login</h1><p>Use main login page</p><a href="/">Go to Home</a></body></html>'''
    
    def get_admin_panel(self):
        return '''<html><body><h1>Admin Panel</h1><p>Redirecting to User Management...</p><script>window.location.href = '/admin/users';</script></body></html>'''
    
    def handle_webhook(self):
        """Handle order webhook"""
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
            "seller": "seller1",  # Default seller
            "date": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        orders_db.append(order)
        
        self.send_json({
            "success": True,
            "order_id": order_id,
            "message": f"Order received by {order['seller']}",
            "data": order
        })
    
    def handle_order_update(self):
        """Handle order status update"""
        content_length = int(self.headers['Content-Length'])
        data = json.loads(self.rfile.read(content_length).decode())
        
        order_id = data.get('order_id')
        status = data.get('status')
        
        for order in orders_db:
            if order['order_id'] == order_id:
                order['status'] = status
                break
        
        self.send_json({"success": True, "message": f"Order {order_id} updated to {status}"})
    
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
