import json
import hashlib
import random
import string
from datetime import datetime

# Database users (simpan di memory untuk demo)
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

# Fungsi-fungsi untuk manage users
def get_all_users():
    """Get all users"""
    return users_db

def get_user_by_id(user_id):
    """Get user by ID"""
    for user in users_db:
        if user["id"] == user_id:
            return user
    return None

def get_user_by_username(username):
    """Get user by username"""
    for user in users_db:
        if user["username"] == username:
            return user
    return None

def authenticate_user(username, password):
    """Authenticate user"""
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()
    for user in users_db:
        if user["username"] == username and user["password"] == hashed_pw:
            return user
    return None

def create_user(user_data):
    """Create new user"""
    # Generate new ID
    new_id = max([u["id"] for u in users_db]) + 1 if users_db else 1
    
    # Hash password
    hashed_pw = hashlib.sha256(user_data.get("password", "password123").encode()).hexdigest()
    
    # Generate token
    token = hashlib.md5(f"{user_data['username']}{datetime.now()}".encode()).hexdigest()
    
    new_user = {
        "id": new_id,
        "username": user_data["username"],
        "password": hashed_pw,
        "role": user_data.get("role", "seller"),
        "shop_name": user_data.get("shop_name", f"Toko {user_data['username']}"),
        "phone": user_data.get("phone", ""),
        "email": user_data.get("email", ""),
        "status": "active",
        "created_at": datetime.now().strftime("%Y-%m-%d"),
        "token": token
    }
    
    users_db.append(new_user)
    return new_user

def update_user(user_id, update_data):
    """Update user data"""
    for i, user in enumerate(users_db):
        if user["id"] == user_id:
            # Update fields
            if "password" in update_data and update_data["password"]:
                users_db[i]["password"] = hashlib.sha256(update_data["password"].encode()).hexdigest()
            
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
    """Delete user (soft delete - change status to inactive)"""
    for i, user in enumerate(users_db):
        if user["id"] == user_id:
            users_db[i]["status"] = "inactive"
            return True
    return False

def generate_random_password(length=8):
    """Generate random password"""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

# Test the functions
if __name__ == "__main__":
    print("Users in database:", len(users_db))
    print("Admin user:", get_user_by_username("admin"))
