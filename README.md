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

## User Roles and Permissions

### 📋 Permissions Matrix

┌─────────────────────┬──────────────────────────┬──────────────┬─────────────────────┬─────────────────────┐
│ 🏷️ **Module**    │ 🔧 **Action**         │ 👤 **User** │ 👨‍💼 **Admin** │ 👑 **Super Admin** │
├─────────────────────┼──────────────────────────┼──────────────┼─────────────────────┼─────────────────────┤
│ **🔐 Authentication** │                      │              │                   │                   │
│ Login System      │ Standard Access       │ ✅ Full Access │ ✅ Full Access    │ ✅ Full Access     │
│ OTP Requirement   │ ❌ Bypassed          │ ✅ Required    │ ✅ Required        │ ✅ Required        │
├─────────────────────┼──────────────────────────┼──────────────┼─────────────────────┼─────────────────────┤
│ **📊 Dashboard**    │                      │              │                   │                   │
│ View Dashboard    │ ✅ Own Data          │ ✅ Company Data │ ✅ Company Data    │ ✅ All Data        │
│ View Analytics    │ ✅ Limited           │ ✅ Full       │ ✅ Full            │ ✅ Full            │
├─────────────────────┼──────────────────────────┼──────────────┼─────────────────────┼─────────────────────┤
│ **🎯 Campaigns**     │                      │              │                   │                   │
│ View Campaigns    │ ✅ Own Only          │ ✅ Company     │ ✅ Company         │ ✅ All             │
│ Create Campaigns  │ ❌ Blocked           │ ✅ Allowed     │ ✅ Allowed         │ ✅ Allowed         │
│ Edit Campaigns    │ ❌ Blocked           │ ✅ Allowed     │ ✅ Allowed         │ ✅ Allowed         │
│ Delete Campaigns  │ ❌ Blocked           │ ✅ Allowed     │ ✅ Allowed         │ ✅ Allowed         │
├─────────────────────┼──────────────────────────┼──────────────┼─────────────────────┼─────────────────────┤
│ **👥 Leads**         │                      │              │                   │                   │
│ View Leads        │ ✅ Own Only          │ ✅ Company     │ ✅ Company         │ ✅ All             │
│ Create Leads      │ ❌ Blocked           │ ✅ Allowed     │ ✅ Allowed         │ ✅ Allowed         │
│ Edit Leads        │ ❌ Blocked           │ ✅ Allowed     │ ✅ Allowed         │ ✅ Allowed         │
│ Delete Leads      │ ❌ Blocked           │ ✅ Allowed     │ ✅ Allowed         │ ✅ Allowed         │
├─────────────────────┼──────────────────────────┼──────────────┼─────────────────────┼─────────────────────┤
│ **📡 Channels**      │                      │              │                   │                   │
│ View Channels     │ ✅ Own Only          │ ✅ Company     │ ✅ Company         │ ✅ All             │
│ Create Channels   │ ❌ Blocked           │ ✅ Allowed     │ ✅ Allowed         │ ✅ Allowed         │
│ Edit Channels     │ ❌ Blocked           │ ✅ Allowed     │ ✅ Allowed         │ ✅ Allowed         │
│ Delete Channels   │ ❌ Blocked           │ ✅ Allowed     │ ✅ Allowed         │ ✅ Allowed         │
├─────────────────────┼──────────────────────────┼──────────────┼─────────────────────┼─────────────────────┤
│ **⏰ Scheduler**     │                      │              │                   │                   │
│ View Schedules    │ ✅ Own Only          │ ✅ Company     │ ✅ Company         │ ✅ All             │
│ Create Schedules  │ ❌ Blocked           │ ✅ Allowed     │ ✅ Allowed         │ ✅ Allowed         │
│ Edit Schedules    │ ❌ Blocked           │ ✅ Allowed     │ ✅ Allowed         │ ✅ Allowed         │
│ Delete Schedules  │ ❌ Blocked           │ ✅ Allowed     │ ✅ Allowed         │ ✅ Allowed         │
├─────────────────────┼──────────────────────────┼──────────────┼─────────────────────┼─────────────────────┤
│ **👤 User Management** │                      │              │                   │                   │
│ View Users        │ ❌ No Access          │ ✅ Company     │ ✅ Company         │ ✅ All             │
│ Create Users      │ ❌ Blocked           │ ✅ Company     │ ✅ Company         │ ✅ All             │
│ Edit Users        │ ❌ Blocked           │ ✅ Company     │ ✅ Company         │ ✅ All             │
│ Delete Users      │ ❌ Blocked           │ ✅ Company     │ ✅ Company         │ ✅ All             │
│ Reactivate Users  │ ❌ Blocked           │ ✅ Company     │ ✅ Company         │ ✅ All             │
│ Extend Access     │ ❌ Blocked           │ ❌ Blocked     │ ❌ Blocked         │ ✅ All             │
├─────────────────────┼──────────────────────────┼──────────────┼─────────────────────┼─────────────────────┤
│ **🏢 Companies**       │                      │              │                   │                   │
│ View Companies    │ ❌ No Access          │ ✅ All        │ ✅ All            │ ✅ All             │
│ Create Companies  │ ❌ Blocked           │ ❌ Blocked     │ ❌ Blocked         │ ✅ Allowed         │
│ Edit Companies    │ ❌ Blocked           │ ❌ Blocked     │ ❌ Blocked         │ ✅ Allowed         │
│ Delete Companies  │ ❌ Blocked           │ ❌ Blocked     │ ❌ Blocked         │ ✅ Allowed         │
├─────────────────────┼──────────────────────────┼──────────────┼─────────────────────┼─────────────────────┤
│ **⚙️ System**          │                      │              │                   │                   │
│ Admin Panel Access│ ❌ Blocked           │ ✅ Allowed     │ ✅ Allowed         │ ✅ Allowed         │
│ System Logs       │ ❌ Blocked           │ ❌ Blocked     │ ❌ Blocked         │ ✅ Allowed         │
│ Role Management   │ ❌ Blocked           │ ❌ Blocked     │ ❌ Blocked         │ ✅ Allowed         │
└─────────────────────┴──────────────────────────┴──────────────┴─────────────────────┴─────────────────────┘

### 🎨 Legend

┌─────────┬─────────────────────────────────────────────────────┐
│ Symbol  │ Meaning                                       │
├─────────┼─────────────────────────────────────────────────────┤
│ ✅      │ **Allowed** - Full access to this feature      │
│ ❌      │ **Blocked** - No access to this feature         │
│ 👤      │ **User** - Basic view-only role               │
│ 👨‍💼    │ **Admin** - Company management role            │
│ 👑      │ **Super Admin** - System-wide control role       │
└─────────┴─────────────────────────────────────────────────────┘

### 🎭 Role Descriptions

---

#### 👤 **User Role**
> **🔍 Primary Access**: View-only access to their own data

**✨ Features:**
- 📊 **Dashboard**: View personal dashboard, analytics, campaigns, leads, channels, schedules
- 🎯 **Data Scope**: Limited to data they created or own
- 🔐 **Authentication**: OTP bypass for quick login convenience

**❌ Limitations:**
- Cannot create, edit, or delete any data
- No access to admin panel or user management
- Cannot view other users' data

---

#### 👨‍💼 **Admin Role**  
> **🏢 Primary Access**: Full management within their company

**✨ Features:**
- 👥 **User Management**: Create, edit, delete users within their company
- 🎯 **Data Management**: Full CRUD on campaigns, leads, channels, schedules
- 📊 **Company View**: Access to all company data and analytics
- 🔄 **User Lifecycle**: Activate/deactivate users they created

**🔒 Scope & Security:**
- 🏢 **Company Boundaries**: Limited to their own company and users they created
- 🔐 **Authentication**: OTP required for enhanced security
- ❌ **Cannot**: Manage other companies or access cross-company data

---

#### 👑 **Super Admin Role**
> **🌐 Primary Access**: System-wide administrative control

**✨ Features:**
- 🏢 **Company Management**: Create, edit, delete all companies
- 👥 **User Management**: Full control over all users across all companies
- ⚙️ **System Access**: Complete access to admin panel, logs, and settings
- 🔧 **Role Management**: Create and manage custom roles
- ⏰ **Access Control**: Extend user access and manage system-wide permissions

**🌟 Unlimited Scope:**
- 🌐 **No Restrictions**: Can access all data across all companies
- 🏢 **Cross-Company**: Full control over multi-tenant environment
- 🔐 **Authentication**: OTP required for maximum security

---

### 🛡️ Security Architecture

| 🔒 **Feature** | 📝 **Description** |
|-----------------|-------------------|
| **Role-Based Access Control** | All API endpoints enforce role permissions |
| **Company Boundaries** | Admins restricted to their own company data |
| **Activity Management** | Users can be deactivated/reactivated by admins |
| **Access Control** | Inactive users cannot access the system |
| **Token-Based Auth** | JWT tokens with expiration for security |
| **Data Isolation** | Multi-tenant architecture with data separation |


