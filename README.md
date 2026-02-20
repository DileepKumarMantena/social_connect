# Social Connect API Documentation

## Base URL
```
http://localhost:8000
```

## Endpoints

### 1. Login
**URL:** `POST /api/v1/login`

**Request:**
```json
{
  "username": "testuser",
  "password": "password123"
}
```

**Response:**
```json
{
  "message": "Login successful",
  "success": true,
  "user": {
    "username": "testuser",
    "email": "test@example.com"
  }
}
```

### 2. Forgot Password
**URL:** `POST /api/v1/forgot-password`

**Request:**
```json
{
  "email": "test@example.com"
}
```

**Response:**
```json
{
  "message": "OTP sent to your email",
  "success": true
}
```

### 3. Verify OTP
**URL:** `POST /api/v1/verify-otp`

**Request:**
```json
{
  "email": "test@example.com",
  "otp": "1234"
}
```

**Response:**
```json
{
  "message": "OTP verified successfully",
  "success": true
}
```

### 4. Reset Password
**URL:** `POST /api/v1/reset-password`

**Request:**
```json
{
  "email": "test@example.com",
  "password": "newpassword123"
}
```

**Response:**
```json
{
  "message": "Password reset successfully",
  "success": true
}
```

## Health Check

### 5. Health Check
**URL:** `GET /`

**Response:**
```json
{
  "message": "Social Connect API is running"
}
```

## Test Credentials

**Username:** `testuser`
**Email:** `test@example.com`
**Password:** `password123`


## Setup Instructions

### Backend Setup
1. **Install dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Run backend server:**
   ```bash
   python extension.py
   ```

### Frontend Setup
1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Run frontend:**
   ```bash
   npm start
   ```

3. **Access frontend:**
   - Frontend URL: http://localhost:3000

### Access API
- **Base URL:** http://localhost:8000
- **Swagger UI:** http://localhost:8000/docs

## OTP Flow

1. **Request OTP** → Forgot Password API
2. **Check terminal** → OTP printed to console
3. **Verify OTP** → Verify OTP API
4. **Reset Password** → Reset Password API


