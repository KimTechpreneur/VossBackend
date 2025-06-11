# User Management API Documentation

This document provides a comprehensive overview of the User Management API for the VossBackend project. It covers authentication, permissions, and detailed descriptions of all available endpoints.

## 1. Overview

The User Management API provides a set of endpoints to manage users, roles, and permissions within the application. It is built using Django and Django Rest Framework, offering a RESTful interface for all user-related operations.

## 2. Authentication

All endpoints, unless otherwise specified, require token-based authentication. The client must include a valid JWT in the `Authorization` header of each request.

**Example:**
```
Authorization: Bearer <your_jwt_token>
```

## 3. Permissions

The API employs a role-based access control (RBAC) system to manage what actions a user can perform. Key roles and permissions include:

- **Admin (`is_staff=True`)**: Has unrestricted access to all endpoints and can perform any administrative action, including creating, updating, and deleting any user, role, or permission.
- **Unit Head (`role.name='Unit Head'`)**: A user with this role has delegated administrative privileges. They can manage users (view, update, deactivate, reset passwords) but *only* for users within their own department. They cannot create new users or manage roles/permissions.
- **Authenticated User**: Any logged-in user can view and edit their own profile information. They cannot access other users' data unless they have administrative privileges.

## 4. API Endpoints

The base URL for this API is assumed to be `/api/`.

---

### 4.1. Users

**Endpoint:** `/api/users/`

This resource is used for managing user accounts.

#### **GET /api/users/**
- **Description:** Retrieves a list of users.
- **Permissions:** Admin or Unit Head. Non-admin users will only see their own user object.
- **Query Parameters:**
    - `status` (string): Filter by user status (e.g., `Active`, `Inactive`).
    - `role` (string): Filter by role ID.
    - `department` (string): Filter by department name.
    - `search` (string): Search by `full_name`, `email`, `phone`, or `employee_id`.
    - `ordering` (string): Order results by `full_name`, `email`, `role`, `status`, `department`, `last_login`.
- **Success Response (200 OK):**
  ```json
  [
      {
          "id": "uuid-string",
          "email": "user@example.com",
          "first_name": "John",
          "last_name": "Doe",
          "full_name": "John Doe",
          "phone": "123-456-7890",
          "role": {
              "id": "uuid-string",
              "name": "Developer"
          },
          "status": "Active",
          "department": "Engineering Department",
          ...
      }
  ]
  ```

#### **POST /api/users/**
- **Description:** Creates a new user and sends an invitation email.
- **Permissions:** Admin User.
- **Request Body:**
  ```json
  {
      "email": "new.user@example.com",
      "first_name": "Jane",
      "last_name": "Doe",
      "role": "role-uuid-string",
      "department": "IT Department",
      "passwordMethod": "invite", // or "manual"
      "temporaryPassword": "a-strong-password", // Required if passwordMethod is "manual"
      "forcePasswordChange": true
  }
  ```
- **Success Response (201 Created):** Returns the newly created user object.

#### **GET /api/users/{id}/**
- **Description:** Retrieves the details of a specific user.
- **Permissions:** Owner or Admin/Unit Head.
- **Success Response (200 OK):** A single user object.

#### **PUT /api/users/{id}/** & **PATCH /api/users/{id}/**
- **Description:** Updates a user's details.
- **Permissions:** Owner or Admin/Unit Head.
- **Request Body:**
  ```json
  {
      "first_name": "Johnny",
      "last_name": "Smith",
      "phone": "987-654-3210",
      "office_location": "Building A, Room 101"
  }
  ```
- **Success Response (200 OK):** The updated user object.

#### **DELETE /api/users/{id}/**
- **Description:** Deletes a user.
- **Permissions:** Admin User.
- **Success Response (204 No Content):**

#### **Custom Actions**

- **POST /api/users/request_password_reset/**
    - **Description:** Initiates a password reset flow for a user.
    - **Permissions:** Allow Any.
    - **Request Body:** `{"email": "user@example.com"}`

- **POST /api/users/reset_password/**
    - **Description:** Resets the user's password using a valid token.
    - **Permissions:** Allow Any.
    - **Request Body:** `{"token": "reset-token", "newPassword": "new-strong-password"}`

- **POST /api/users/logout/**
    - **Description:** Blacklists a refresh token to log a user out.
    - **Permissions:** Authenticated.
    - **Request Body:** `{"refresh_token": "refresh-token-string"}`

- **POST /api/users/bulk_deactivate/**
    - **Description:** Deactivates multiple users at once.
    - **Permissions:** Admin User.
    - **Request Body:** `{"user_ids": ["uuid1", "uuid2"]}`

---

### 4.2. Roles

**Endpoint:** `/api/roles/`

This resource is for managing user roles.

#### **GET /api/roles/**
- **Description:** Retrieves a list of all roles.
- **Permissions:** Admin User.
- **Success Response (200 OK):** A list of role objects.

#### **POST /api/roles/**
- **Description:** Creates a new role.
- **Permissions:** Admin User.
- **Request Body:**
  ```json
  {
      "name": "New Role",
      "description": "Description for the new role.",
      "permissions": ["permission-uuid-1", "permission-uuid-2"]
  }
  ```
- **Success Response (201 Created):** The new role object.

#### Other Methods (GET {id}, PUT {id}, PATCH {id}, DELETE {id})
Standard CRUD operations are available for individual roles. They all require Admin permissions.

---

### 4.3. Permissions

**Endpoint:** `/api/permissions/`

This resource is for viewing available permissions. These are typically hard-coded in the application and not managed via the API.

#### **GET /api/permissions/**
- **Description:** Retrieves a list of all available permissions.
- **Permissions:** Admin User.
- **Query Parameters:**
    - `module` (string): Filter permissions by module name.
- **Success Response (200 OK):** A list of permission objects.

---

### 4.4. User Profile

**Endpoint:** `/api/profile/`

This resource is for the authenticated user to manage their own profile.

#### **GET /api/profile/**
- **Description:** Retrieves the profile of the currently authenticated user.
- **Permissions:** Authenticated.
- **Success Response (200 OK):** The user's own profile data.

#### **PUT /api/profile/** & **PATCH /api/profile/**
- **Description:** Updates the profile of the currently authenticated user.
- **Permissions:** Authenticated.
- **Request Body:**
  ```json
  {
      "first_name": "MyFirstName",
      "last_name": "MyLastName",
      "phone": "555-555-5555"
  }
  ```
- **Success Response (200 OK):** The updated user profile object. 