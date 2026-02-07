from http.server import BaseHTTPRequestHandler
import json
import hashlib
from datetime import datetime
import random
import string

# ========== USER DATABASE (IN-MEMORY) ==========
users_db = [
    {
        "id": 1,
        "username": "admin",
        "password": hashlib.sha256("admin123".encode()).hexdigest(),
        "role": "admin",
        "shop_name": "MFH Store Admin",
        "phone": "081998593873",
        "email": "admin@mfhstore.id",
        "status": "active",
        "created_at": "2025-02-01",
        "token": "admin_token_001"
    },
    {
        "id": 2,
        "username": "seller1",
        "password": hashlib.sha256("seller123".encode()).hexdigest(),
        "role": "seller",
        "shop_name": "Toko Digital 1",
        "phone": "081234567890",
        "email": "seller1@mfhstore.id",
        "status": "active",
        "created_at": "2025-02-01",
        "token": "seller_token_001"
    },
    {
        "id": 3,
        "username": "seller2",
        "password": hashlib.sha256("seller123".encode()).hexdigest(),
        "role": "seller",
        "shop_name": "Toko Digital 2",
        "phone": "081234567891",
        "email": "seller2@mfhstore.id",
        "status": "active",
        "created_at": "2025-02-01",
        "token": "seller_token_002"
    }
]

orders_db = []

# ========== USER FUNCTIONS ==========
def get_all_users():
    """Get all active users"""
    return [u for u in users_db if u["status"] == "active"]

def get_user_by_id(user_id):
    """Get user by ID"""
    for user in users_db:
        if user["id"] == user_id and user["status"] == "active":
            return user
    return None

def get_user_by_username(username):
    """Get user by username"""
    for user in users_db:
        if user["username"] == username and user["status"] == "active":
            return user
    return None

def authenticate_user(username, password):
    """Authenticate user"""
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()
    for user in users_db:
        if user["username"] == username and user["password"] == hashed_pw and user["status"] == "active":
            return user
    return None

def create_user(user_data):
    """Create new user"""
    # Check if username exists
    for user in users_db:
        if user["username"] == user_data["username"]:
            return None
    
    # Generate new ID
    new_id = max([u["id"] for u in users_db]) + 1 if users_db else 1
    
    new_user = {
        "id": new_id,
        "username": user_data["username"],
        "password": hashlib.sha256(user_data["password"].encode()).hexdigest(),
        "role": user_data.get("role", "seller"),
        "shop_name": user_data.get("shop_name", f"Toko {user_data['username']}"),
        "phone": user_data.get("phone", ""),
        "email": user_data.get("email", ""),
        "status": "active",
        "created_at": datetime.now().strftime("%Y-%m-%d"),
        "token": hashlib.md5(f"{user_data['username']}{datetime.now()}".encode()).hexdigest()
    }
    
    users_db.append(new_user)
    return new_user

def update_user(user_id, update_data):
    """Update user data"""
    for i, user in enumerate(users_db):
        if user["id"] == user_id:
            # Update password if provided
            if "password" in update_data and update_data["password"]:
                users_db[i]["password"] = hashlib.sha256(update_data["password"].encode()).hexdigest()
            
            # Update other fields
            if "role" in update_data:
                users_db[i]["role"] = update_data["role"]
            
            if "shop_name" in update_data:
                users_db[i]["shop_name"] = update_data["shop_name"]
            
            if "phone" in update_data:
                users_db[i]["phone"] = update_data["phone"]
            
            if "email" in update_data:
                users_db[i]["email"] = update_data["email"]
            
            if "status" in update_data:
                users_db[i]["status"] = update_data["status"]
            
            return users_db[i]
    return None

def delete_user(user_id):
    """Soft delete user (change status to inactive)"""
    for i, user in enumerate(users_db):
        if user["id"] == user_id:
            users_db[i]["status"] = "inactive"
            return True
    return False

def generate_password(length=8):
    """Generate random password"""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

# ========== HTTP HANDLER ==========
class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path
        
        # ========== API ENDPOINTS ==========
        if path == '/api/ping':
            self.send_json({
                "status": "online",
                "service": "MFH Store Dashboard v3.1",
                "timestamp": datetime.now().isoformat(),
                "users": len(get_all_users()),
                "orders": len(orders_db)
            })
        
        elif path == '/api/stats':
            active_users = get_all_users()
            sellers = [u for u in active_users if u["role"] == "seller"]
            
            self.send_json({
                "total_orders": len(orders_db),
                "pending_orders": len([o for o in orders_db if o.get('status') == 'pending']),
                "completed_orders": len([o for o in orders_db if o.get('status') == 'completed']),
                "total_users": len(active_users),
                "total_sellers": len(sellers),
                "total_admins": len([u for u in active_users if u["role"] == "admin"]),
                "revenue_today": 0
            })
        
        elif path == '/api/orders':
            self.send_json(orders_db)
        
        elif path == '/api/users':
            self.send_json(get_all_users())
        
        elif path == '/api/users/sellers':
            sellers = [u for u in get_all_users() if u["role"] == "seller"]
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
        
        elif path == '/seller':
            self.send_html(self.get_seller_login_page())
        
        elif path == '/seller/dashboard':
            self.send_html(self.get_seller_dashboard_page())
        
        elif path == '/admin/login':
            self.send_html(self.get_admin_login_page())
        
        elif path == '/admin/dashboard':
            self.send_html(self.get_admin_dashboard_page())
        
        elif path == '/change-password':
            self.send_html(self.get_change_password_page())
        
        else:
            self.send_error(404, "Not Found")
    
    def do_POST(self):
        path = self.path
        
        if path == '/api/login':
            content_length = int(self.headers['Content-Length'])
            data = json.loads(self.rfile.read(content_length).decode())
            
            user = authenticate_user(data.get('username'), data.get('password'))
            
            if user:
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
                self.send_json({"success": False, "error": "Invalid credentials"}, 401)
        
        elif path == '/api/users/create':
            content_length = int(self.headers['Content-Length'])
            data = json.loads(self.rfile.read(content_length).decode())
            
            # Validate
            if not data.get('username') or not data.get('password'):
                self.send_json({"success": False, "error": "Username and password required"}, 400)
                return
            
            if get_user_by_username(data['username']):
                self.send_json({"success": False, "error": "Username already exists"}, 400)
                return
            
            new_user = create_user(data)
            
            if new_user:
                self.send_json({
                    "success": True, 
                    "user": {
                        "id": new_user["id"],
                        "username": new_user["username"],
                        "role": new_user["role"],
                        "shop_name": new_user["shop_name"]
                    },
                    "password": data['password']  # Return plain password for display
                })
            else:
                self.send_json({"success": False, "error": "Failed to create user"}, 500)
        
        elif path == '/api/users/update':
            content_length = int(self.headers['Content-Length'])
            data = json.loads(self.rfile.read(content_length).decode())
            
            user_id = data.get('id')
            if not user_id:
                self.send_json({"success": False, "error": "User ID required"}, 400)
                return
            
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
        
        elif path == '/api/change-password':
            content_length = int(self.headers['Content-Length'])
            data = json.loads(self.rfile.read(content_length).decode())
            
            username = data.get('username')
            old_password = data.get('old_password')
            new_password = data.get('new_password')
            
            # Authenticate first
            user = authenticate_user(username, old_password)
            if not user:
                self.send_json({"success": False, "error": "Current password incorrect"}, 401)
                return
            
            # Update password
            if update_user(user['id'], {"password": new_password}):
                self.send_json({"success": True, "message": "Password updated successfully"})
            else:
                self.send_json({"success": False, "error": "Failed to update password"}, 500)
        
        elif path == '/api/webhook':
            self.handle_webhook()
        
        elif path == '/api/order/update':
            self.handle_order_update()
        
        else:
            self.send_json({"error": "Not found"}, 404)
    
    # ========== HTML PAGES ==========
    def get_homepage(self):
        return '''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
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
        .btn-admin {
            background: linear-gradient(45deg, #ff4444, #ff00ff);
        }
        .btn-password {
            background: linear-gradient(45deg, #00aa00, #00ffaa);
        }
        .demo-info {
            background: rgba(255,255,255,0.05);
            padding: 20px;
            border-radius: 10px;
            margin: 30px 0;
            text-align: left;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔐 MFH STORE DASHBOARD</h1>
        <p>Complete User Management System</p>
        
        <div style="margin: 40px 0;">
            <a href="/seller" class="btn">👨‍💼 Seller Login</a>
            <a href="/admin/users" class="btn btn-admin">👥 User Management</a>
            <a href="/admin/create-user" class="btn">➕ Create User</a>
            <a href="/change-password" class="btn btn-password">🔑 Change Password</a>
            <a href="/api/ping" class="btn">🔧 Test API</a>
        </div>
        
        <div class="demo-info">
            <h3>📋 Demo Accounts:</h3>
            <p><strong>Admin:</strong> admin / admin123</p>
            <p><strong>Seller 1:</strong> seller1 / seller123</p>
            <p><strong>Seller 2:</strong> seller2 / seller123</p>
            <p>🔗 URL: <strong>mfh-vercel-dashboard.vercel.app</strong></p>
            <p>📞 Support: <strong>0819-9859-3873</strong></p>
        </div>
    </div>
</body>
</html>'''
    
    def get_user_management_page(self):
        # Return simple user management page
        users = get_all_users()
        html = '''<!DOCTYPE html>
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
        .user-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        .user-table th, .user-table td {
            padding: 12px;
            border: 1px solid rgba(255,255,255,0.1);
            text-align: left;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>👥 User Management</h1>
            <p>Manage admin & seller accounts | <a href="/" class="btn">🏠 Home</a> | <a href="/admin/create-user" class="btn">➕ Add User</a></p>
        </div>
        
        <table class="user-table">
            <tr>
                <th>ID</th>
                <th>Username</th>
                <th>Role</th>
                <th>Shop Name</th>
                <th>Phone</th>
                <th>Status</th>
                <th>Actions</th>
            </tr>'''
        
        for user in users:
            html += f'''
            <tr>
                <td>{user['id']}</td>
                <td><strong>{user['username']}</strong></td>
                <td><span style="color: {'#0066ff' if user['role'] == 'admin' else '#00ffaa'}">{user['role']}</span></td>
                <td>{user.get('shop_name', '-')}</td>
                <td>{user.get('phone', '-')}</td>
                <td><span style="color: {'#00ffaa' if user['status'] == 'active' else '#ff4444'}">{user['status']}</span></td>
                <td>
                    <button class="btn" onclick="editUser({user['id']})">✏️ Edit</button>
                    <button class="btn" onclick="changePassword('{user['username']}')">🔑 Password</button>
                </td>
            </tr>'''
        
        html += '''
        </table>
        
        <div style="margin-top: 30px;">
            <a href="/change-password" class="btn">🔑 Change My Password</a>
        </div>
    </div>
    
    <script>
        function editUser(userId) {
            alert('Edit user ' + userId + ' - Coming soon!');
        }
        
        function changePassword(username) {
            const newPassword = prompt('Enter new password for ' + username + ':', 'newpassword123');
            if (newPassword && newPassword.length >= 6) {
                fetch('/api/users/update', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        username: username,
                        password: newPassword
                    })
                })
                .then(r => r.json())
                .then(data => {
                    if(data.success) {
                        alert('Password updated for ' + username + '\\nNew password: ' + newPassword);
                    } else {
                        alert('Error: ' + data.error);
                    }
                });
            }
        }
    </script>
</body>
</html>'''
        
        return html
    
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
            max-width: 500px;
            margin: 50px auto;
            background: rgba(255,255,255,0.05);
            padding: 30px;
            border-radius: 15px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        input, select {
            width: 100%;
            padding: 12px;
            background: rgba(255,255,255,0.1);
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 8px;
            color: white;
            font-size: 1rem;
            margin-top: 5px;
        }
        button {
            background: #0066ff;
            color: white;
            border: none;
            padding: 15px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1rem;
            font-weight: bold;
            width: 100%;
            margin-top: 10px;
        }
        .password-display {
            background: rgba(0,255,170,0.1);
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
            font-family: monospace;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>➕ Create New User</h1>
        
        <form id="createForm">
            <div class="form-group">
                <label>Username *</label>
                <input type="text" id="username" placeholder="seller3" required>
            </div>
            
            <div class="form-group">
                <label>Role *</label>
                <select id="role" required>
                    <option value="seller">Seller</option>
                    <option value="admin">Admin</option>
                </select>
            </div>
            
            <div class="form-group">
                <label>Shop Name (for sellers)</label>
                <input type="text" id="shopName" placeholder="Toko Digital Baru">
            </div>
            
            <div class="form-group">
                <label>Phone</label>
                <input type="text" id="phone" placeholder="0812xxxxxxx">
            </div>
            
            <div class="form-group">
                <label>Generated Password</label>
                <div class="password-display" id="generatedPassword">seller123</div>
                <button type="button" onclick="generatePassword()">🔄 Generate New Password</button>
            </div>
            
            <button type="submit">➕ Create User</button>
        </form>
        
        <div id="result" style="margin-top: 20px;"></div>
        
        <div style="margin-top: 30px;">
            <a href="/admin/users" style="color: #aaa;">← Back to User Management</a>
        </div>
    </div>
    
    <script>
        function generatePassword() {
            const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
            let password = '';
            for (let i = 0; i < 8; i++) {
                password += chars.charAt(Math.floor(Math.random() * chars.length));
            }
            document.getElementById('generatedPassword').textContent = password;
        }
        
        document.getElementById('createForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const userData = {
                username: document.getElementById('username').value,
                password: document.getElementById('generatedPassword').textContent,
                role: document.getElementById('role').value,
                shop_name: document.getElementById('shopName').value || '',
                phone: document.getElementById('phone').value || ''
            };
            
            fetch('/api/users/create', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(userData)
            })
            .then(r => r.json())
            .then(data => {
                const resultDiv = document.getElementById('result');
                if(data.success) {
                    resultDiv.innerHTML = `
                        <div style="background: rgba(0,255,170,0.2); padding: 15px; border-radius: 10px;">
                            <h3 style="color: #00ffaa;">✅ User Created Successfully!</h3>
                            <p>Username: <strong>${data.user.username}</strong></p>
                            <p>Password: <strong>${data.password}</strong></p>
                            <p>Role: ${data.user.role}</p>
                            <p>Share this password with the user!</p>
                        </div>
                    `;
                    document.getElementById('createForm').reset();
                    generatePassword();
                } else {
                    resultDiv.innerHTML = `
                        <div style="background: rgba(255,68,68,0.2); padding: 15px; border-radius: 10px;">
                            <h3 style="color: #ff4444;">❌ Error</h3>
                            <p>${data.error}</p>
                        </div>
                    `;
                }
            });
        });
        
        // Generate initial password
        generatePassword();
    </script>
</body>
</html>'''
    
    def get_change_password_page(self):
        return '''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Change Password - MFH Store</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #0a0a1a;
            color: white;
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 500px;
            margin: 50px auto;
            background: rgba(255,255,255,0.05);
            padding: 30px;
            border-radius: 15px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        input {
            width: 100%;
            padding: 12px;
            background: rgba(255,255,255,0.1);
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 8px;
            color: white;
            font-size: 1rem;
            margin-top: 5px;
        }
        button {
            background: #0066ff;
            color: white;
            border: none;
            padding: 15px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1rem;
            font-weight: bold;
            width: 100%;
        }
        .user-select {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        .user-btn {
            background: #333;
            padding: 10px 15px;
            border-radius: 5px;
            cursor: pointer;
        }
        .user-btn.active {
            background: #0066ff;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔑 Change Password</h1>
        
        <div class="user-select">
            <div class="user-btn active" onclick="selectUser('admin')">👑 Admin</div>
            <div class="user-btn" onclick="selectUser('seller1')">👨‍💼 Seller 1</div>
            <div class="user-btn" onclick="selectUser('seller2')">👨‍💼 Seller 2</div>
            <div class="user-btn" onclick="selectUser('other')">👤 Other</div>
        </div>
        
        <form id="passwordForm">
            <div class="form-group">
                <label>Username</label>
                <input type="text" id="username" value="admin" required>
            </div>
            
            <div class="form-group" id="currentPassGroup">
                <label>Current Password</label>
                <input type="password" id="old_password" placeholder="Enter current password" required>
            </div>
            
            <div class="form-group">
                <label>New Password</label>
                <input type="password" id="new_password" placeholder="Enter new password" required>
            </div>
            
            <div class="form-group">
                <label>Confirm New Password</label>
                <input type="password" id="confirm_password" placeholder="Confirm new password" required>
            </div>
            
            <button type="submit">🔑 Change Password</button>
        </form>
        
        <div id="result" style="margin-top: 20px;"></div>
        
        <div style="margin-top: 30px; color: #aaa;">
            <p><strong>Default Passwords:</strong></p>
            <p>• Admin: admin123</p>
            <p>• Seller 1: seller123</p>
            <p>• Seller 2: seller123</p>
        </div>
    </div>
    
    <script>
        function selectUser(username) {
            // Update buttons
            document.querySelectorAll('.user-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            event.target.classList.add('active');
            
            // Set username
            if(username === 'other') {
                document.getElementById('username').value = '';
                document.getElementById('username').placeholder = 'Enter username';
                document.getElementById('username').focus();
            } else {
                document.getElementById('username').value = username;
            }
            
            // Set default password hint
            const defaultPasswords = {
                'admin': 'admin123',
                'seller1': 'seller123',
                'seller2': 'seller123'
            };
            
            if(defaultPasswords[username]) {
                document.getElementById('old_password').placeholder = `Current: ${defaultPasswords[username]}`;
            }
        }
        
        document.getElementById('passwordForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const username = document.getElementById('username').value;
            const oldPassword = document.getElementById('old_password').value;
            const newPassword = document.getElementById('new_password').value;
            const confirmPassword = document.getElementById('confirm_password').value;
            
            if(newPassword !== confirmPassword) {
                showResult('❌ New passwords do not match!', 'error');
                return;
            }
            
            if(newPassword.length < 6) {
                showResult('❌ Password must be at least 6 characters', 'error');
                return;
            }
            
            fetch('/api/change-password', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    username: username,
                    old_password: oldPassword,
                    new_password: newPassword
                })
            })
            .then(r => r.json())
            .then(data => {
                if(data.success) {
                    showResult(`✅ Password updated successfully for ${username}!\nNew password: ${newPassword}`, 'success');
                    document.getElementById('passwordForm').reset();
                } else {
                    showResult(`❌ Error: ${data.error}`, 'error');
                }
            });
        });
        
        function showResult(message, type) {
            const resultDiv = document.getElementById('result');
            resultDiv.innerHTML = `
                <div style="background: ${type === 'success' ? 'rgba(0,255,170,0.2)' : 'rgba(255,68,68,0.2)'}; 
                           padding: 15px; 
                           border-radius: 10px;
                           color: ${type === 'success' ? '#00ffaa' : '#ff4444'};
                           white-space: pre-line;">
                    ${message}
                </div>
            `;
        }
    </script>
</body>
</html>'''
    
    def get_seller_login_page(self):
        return '''<html><body style="background: #0a0a1a; color: white; text-align: center; padding: 50px;">
            <h1>👨‍💼 Seller Login</h1>
            <p>Login page coming soon!</p>
            <p>Use: seller1 / seller123 or seller2 / seller123</p>
            <a href="/" style="color: #0066ff;">← Back to Home</a>
        </body></html>'''
    
    def get_seller_dashboard_page(self):
        return '''<html><body style="background: #0a0a1a; color: white; text-align: center; padding: 50px;">
            <h1>📊 Seller Dashboard</h1>
            <p>Seller dashboard coming soon!</p>
            <a href="/" style="color: #0066ff;">← Back to Home</a>
        </body></html>'''
    
    def get_admin_login_page(self):
        return '''<html><body style="background: #0a0a1a; color: white; text-align: center; padding: 50px;">
            <h1>🔐 Admin Login</h1>
            <p>Use: admin / admin123</p>
            <a href="/admin/users" style="color: #0066ff;">→ Go to User Management</a>
        </body></html>'''
    
    def get_admin_dashboard_page(self):
        return '''<html><body style="background: #0a0a1a; color: white; text-align: center; padding: 50px;">
            <h1>📊 Admin Dashboard</h1>
            <p>Admin dashboard coming soon!</p>
            <a href="/admin/users" style="color: #0066ff;">→ User Management</a>
        </body></html>'''
    
    def get_edit_user_page(self):
        return '''<html><body style="background: #0a0a1a; color: white; text-align: center; padding: 50px;">
            <h1>✏️ Edit User</h1>
            <p>Edit user page coming soon!</p>
            <a href="/admin/users" style="color: #0066ff;">← Back to User Management</a>
        </body></html>'''
    
    def handle_webhook(self):
        """Handle order webhook"""
        try:
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
                "seller": "seller1",
                "date": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            orders_db.append(order)
            
            self.send_json({
                "success": True,
                "order_id": order_id,
                "message": "Order received",
                "data": order
            })
        except Exception as e:
            self.send_json({"success": False, "error": str(e)}, 500)
    
    def handle_order_update(self):
        """Handle order status update"""
        try:
            content_length = int(self.headers['Content-Length'])
            data = json.loads(self.rfile.read(content_length).decode())
            
            order_id = data.get('order_id')
            status = data.get('status')
            
            for order in orders_db:
                if order['order_id'] == order_id:
                    order['status'] = status
                    break
            
            self.send_json({"success": True, "message": f"Order {order_id} updated"})
        except Exception as e:
            self.send_json({"success": False, "error": str(e)}, 500)
    
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
