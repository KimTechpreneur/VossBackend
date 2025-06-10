# Users Management API Documentation

This document outlines the API endpoints required for the Users Management feature, enabling seamless integration with the existing frontend.

---

## 1. Data Models

### 1.1. `UserRole`
Represents the possible roles a user can have.

```typescript
type UserRole = 'Global Admin' | 'Unit Head' | 'Staff' | 'Agent';
```

### 1.2. `UserStatus`
Represents the possible statuses of a user account.

```typescript
type UserStatus = 'Active' | 'Inactive' | 'Suspended';
```

### 1.3. `UserDepartment`
Represents the departments a user can belong to.

```typescript
type UserDepartment = 'Engineering Department' | 'IT Department' | 'Finance Department' | 'Student Affairs' | 'Science Department' | 'Library' | 'Admissions';
```

### 1.4. `PasswordSetupMethod`
Represents the method for setting up a user's password.

```typescript
type PasswordSetupMethod = 'invite' | 'manual';
```

### 1.5. `User`
Represents a user in the system. This extends a potential `SharedUser` interface, but for backend purposes, all fields are listed here.

```typescript
interface User {
  id: string; // Unique identifier for the user
  fullName: string; // Full name of the user
  email: string; // User's email address (unique)
  phone?: string; // Optional: User's phone number
  role: UserRole; // User's assigned role
  status: UserStatus; // User's account status
  department: UserDepartment; // User's department
  lastLogin?: string; // Optional: ISO 8601 timestamp of last login
  employeeId?: string; // Optional: Employee ID
  officeLocation?: string; // Optional: Office location
  notes?: string; // Optional: Additional notes about the user
  initials?: string; // Derived from fullName, not needed for backend storage
}
```

### 1.6. `UserFilters`
Represents the filtering parameters for fetching users.

```typescript
interface UserFilters {
  searchBy: 'name' | 'email' | 'phone' | 'id'; // Field to search by
  searchQuery: string; // The search term
  role: UserRole | 'all'; // Filter by user role
  status: UserStatus | 'all'; // Filter by user status
  department: UserDepartment | 'all'; // Filter by user department
  dateRangeFrom?: string; // ISO 8601 timestamp for start of last login date range
  dateRangeTo?: string; // ISO 8601 timestamp for end of last login date range
  // Backend should also support:
  // sortBy: 'fullName' | 'email' | 'role' | 'status' | 'department' | 'lastLogin'; // Field to sort by
  // sortOrder: 'asc' | 'desc'; // Sort direction
  // page: number; // Current page number for pagination
  // limit: number; // Number of items per page for pagination
}
```

### 1.7. `AddUserFormData`
Represents the data structure used for creating a new user.

```typescript
interface AddUserFormData {
  fullName: string;
  email: string;
  phone?: string;
  employeeId?: string;
  role: UserRole;
  status: UserStatus;
  department: UserDepartment;
  officeLocation?: string;
  passwordMethod: PasswordSetupMethod; // 'invite' or 'manual'
  temporaryPassword?: string; // Required if passwordMethod is 'manual'
  confirmPassword?: string; // For frontend validation, backend should ensure consistency if manual
  forcePasswordChange: boolean; // If user should be forced to change password on first login
  notes?: string;
}
```

### 1.8. `UserUpdateFormData`
Represents the data structure for updating an existing user. All fields are optional as it's typically used for PATCH.

```typescript
interface UserUpdateFormData {
  fullName?: string;
  email?: string;
  phone?: string;
  employeeId?: string;
  role?: UserRole;
  status?: UserStatus;
  department?: UserDepartment;
  officeLocation?: string;
  notes?: string;
  // Password changes typically handled by separate endpoints/flows
}
```

---

## 2. API Endpoints

All endpoints should be prefixed with `/api/v1/users`.

### 2.1. Get All Users

*   **HTTP Method:** `GET`
*   **Endpoint URL:** `/api/v1/users`
*   **Description:** Retrieves a list of all users, with support for searching, filtering, and pagination.
*   **Query Parameters:**
    *   `searchBy` (string, optional): Field to search on (`name`, `email`, `phone`, `id`). Default: `name`.
    *   `searchQuery` (string, optional): The search term. Supports special prefixes like `role:`, `status:`, `department:`.
    *   `role` (string, optional): Filter by user role (`Global Admin`, `Unit Head`, `Staff`, `Agent`). Default: `all`.
    *   `status` (string, optional): Filter by user status (`Active`, `Inactive`, `Suspended`). Default: `all`.
    *   `department` (string, optional): Filter by user department.
    *   `dateRangeFrom` (string, optional): Start date (ISO 8601) for `lastLogin` filter.
    *   `dateRangeTo` (string, optional): End date (ISO 8601) for `lastLogin` filter.
    *   `sortBy` (string, optional): Field to sort by (`fullName`, `email`, `role`, `status`, `department`, `lastLogin`). Default: `fullName`.
    *   `sortOrder` (string, optional): Sort direction (`asc` or `desc`). Default: `asc`.
    *   `page` (number, optional): Current page number (1-indexed). Default: `1`.
    *   `limit` (number, optional): Number of users per page. Default: `10` (or a sensible backend default).
*   **Success Response:** `200 OK`
    ```json
    {
      "users": [
        {
          "id": "USR-000421",
          "fullName": "Sarah Mutiso",
          "email": "s.mutiso@voss.edu",
          "phone": "+254 712 345 678",
          "role": "Unit Head",
          "status": "Active",
          "department": "Engineering Department",
          "lastLogin": "2025-05-24T15:14:00Z",
          "employeeId": "EMP-001",
          "officeLocation": "Block A, Floor 2",
          "notes": "Department lead for engineering projects"
        },
        // ... more users
      ],
      "totalItems": 156,
      "totalPages": 16,
      "currentPage": 1,
      "itemsPerPage": 10
    }
    ```
*   **Error Responses:**
    *   `500 Internal Server Error` (Generic error)
*   **Authentication/Authorization:** Requires authenticated user. Admin or user management permissions.

### 2.2. Get Single User by ID

*   **HTTP Method:** `GET`
*   **Endpoint URL:** `/api/v1/users/{id}`
*   **Description:** Retrieves details of a single user by their ID.
*   **Path Parameters:**
    *   `id` (string, required): The unique identifier of the user.
*   **Success Response:** `200 OK`
    ```json
    {
      "id": "USR-000421",
      "fullName": "Sarah Mutiso",
      "email": "s.mutiso@voss.edu",
      "phone": "+254 712 345 678",
      "role": "Unit Head",
      "status": "Active",
      "department": "Engineering Department",
      "lastLogin": "2025-05-24T15:14:00Z",
      "employeeId": "EMP-001",
      "officeLocation": "Block A, Floor 2",
      "notes": "Department lead for engineering projects"
    }
    ```
*   **Error Responses:**
    *   `404 Not Found` (If user with `id` does not exist)
    *   `500 Internal Server Error`
*   **Authentication/Authorization:** Requires authenticated user. Admin or relevant permissions (e.g., view own profile, view users in same department/unit).

### 2.3. Create New User

*   **HTTP Method:** `POST`
*   **Endpoint URL:** `/api/v1/users`
*   **Description:** Creates a new user account.
*   **Request Body:** (`application/json`)
    ```json
    {
      "fullName": "New User Name",
      "email": "new.user@example.com",
      "phone": "+1234567890",
      "employeeId": "EMP-002",
      "role": "Staff",
      "status": "Active",
      "department": "Finance Department",
      "officeLocation": "Building B, Room 101",
      "passwordMethod": "manual",
      "temporaryPassword": "StrongPassword123!",
      "forcePasswordChange": true,
      "notes": "New hire for finance team."
    }
    ```
    *   If `passwordMethod` is `invite`, `temporaryPassword` and `forcePasswordChange` might not be sent or would be ignored by the backend.
*   **Success Response:** `201 Created`
    ```json
    {
      "id": "USR-000428",
      "fullName": "New User Name",
      "email": "new.user@example.com",
      "phone": "+1234567890",
      "role": "Staff",
      "status": "Active",
      "department": "Finance Department",
      "lastLogin": null,
      "employeeId": "EMP-002",
      "officeLocation": "Building B, Room 101",
      "notes": "New hire for finance team."
    }
    ```
*   **Error Responses:**
    *   `400 Bad Request` (Invalid input, e.g., missing required fields, invalid email format, weak password if manual)
    *   `409 Conflict` (If user with same email already exists)
    *   `500 Internal Server Error`
*   **Authentication/Authorization:** Requires authenticated user with permissions to create users (e.g., Global Admin, Unit Head).

### 2.4. Update Existing User

*   **HTTP Method:** `PATCH`
    *   **Note:** Frontend uses `AddUserFormData` for `onSave` in `ViewUserPage.tsx`, implying a full update. However, `PATCH` is generally more flexible for partial updates.
*   **Endpoint URL:** `/api/v1/users/{id}`
*   **Description:** Updates an existing user's information identified by their ID.
*   **Path Parameters:**
    *   `id` (string, required): The unique identifier of the user to update.
*   **Request Body:** (`application/json`)
    *   Fields are optional. Only send fields that need to be updated.
    ```json
    {
      "phone": "+254 700 111 222",
      "status": "Inactive",
      "officeLocation": "Main Building, Floor 1"
    }
    ```
*   **Success Response:** `200 OK`
    ```json
    {
      "id": "USR-000421",
      "fullName": "Sarah Mutiso",
      "email": "s.mutiso@voss.edu",
      "phone": "+254 700 111 222",
      "role": "Unit Head",
      "status": "Inactive",
      "department": "Engineering Department",
      "lastLogin": "2025-05-24T15:14:00Z",
      "employeeId": "EMP-001",
      "officeLocation": "Main Building, Floor 1",
      "notes": "Department lead for engineering projects"
    }
    ```
*   **Error Responses:**
    *   `400 Bad Request` (Invalid input, e.g., invalid email format)
    *   `404 Not Found` (If user with `id` does not exist)
    *   `409 Conflict` (If new email conflicts with an existing user's email)
    *   `500 Internal Server Error`
*   **Authentication/Authorization:** Requires authenticated user with permissions to edit users (e.g., Global Admin, Unit Head). Users might be able to edit their own `phone`, `officeLocation`, `notes`.

### 2.5. Delete User

*   **HTTP Method:** `DELETE`
*   **Endpoint URL:** `/api/v1/users/{id}`
*   **Description:** Deletes a user account by their ID.
*   **Path Parameters:**
    *   `id` (string, required): The unique identifier of the user to delete.
*   **Success Response:** `204 No Content` (No response body)
*   **Error Responses:**
    *   `404 Not Found` (If user with `id` does not exist)
    *   `403 Forbidden` (If attempting to delete a system-critical user, or a user with active processes/dependencies)
    *   `500 Internal Server Error`
*   **Authentication/Authorization:** Requires authenticated user with permissions to delete users (e.g., Global Admin).

### 2.6. Bulk Actions (Optional but Recommended)

These endpoints are inferred from the `ManageUsersPage.tsx` and `SharedBulkActionsToolbar` usage. The backend should implement these as needed.

#### 2.6.1. Deactivate Multiple Users

*   **HTTP Method:** `POST`
*   **Endpoint URL:** `/api/v1/users/bulk/deactivate`
*   **Description:** Deactivates a list of user accounts.
*   **Request Body:** (`application/json`)
    ```json
    {
      "userIds": ["USR-0001", "USR-0002", "USR-0003"]
    }
    ```
*   **Success Response:** `200 OK` or `204 No Content`
    ```json
    {
      "message": "Selected users deactivated successfully."
    }
    ```
*   **Error Responses:** `400 Bad Request`, `403 Forbidden`, `500 Internal Server Error`
*   **Authentication/Authorization:** Requires authenticated user with bulk user management permissions.

#### 2.6.2. Send Password Reset to Multiple Users

*   **HTTP Method:** `POST`
*   **Endpoint URL:** `/api/v1/users/bulk/send-password-reset`
*   **Description:** Sends password reset instructions to a list of user accounts.
*   **Request Body:** (`application/json`)
    ```json
    {
      "userIds": ["USR-0001", "USR-0002"]
    }
    ```
*   **Success Response:** `200 OK`
    ```json
    {
      "message": "Password reset instructions sent to selected users."
    }
    ```
*   **Error Responses:** `400 Bad Request`, `403 Forbidden`, `500 Internal Server Error`
*   **Authentication/Authorization:** Requires authenticated user with password management permissions.

#### 2.6.3. Change Role for Multiple Users

*   **HTTP Method:** `PATCH`
*   **Endpoint URL:** `/api/v1/users/bulk/change-role`
*   **Description:** Changes the role for a list of user accounts.
*   **Request Body:** (`application/json`)
    ```json
    {
      "userIds": ["USR-0001", "USR-0002"],
      "newRole": "Unit Head"
    }
    ```
*   **Success Response:** `200 OK`
    ```json
    {
      "message": "Roles for selected users updated successfully."
    }
    ```
*   **Error Responses:** `400 Bad Request`, `403 Forbidden`, `500 Internal Server Error`
*   **Authentication/Authorization:** Requires authenticated user with bulk role assignment permissions.

### 2.7. Toggle User Status (Individual)

*   **HTTP Method:** `PATCH`
*   **Endpoint URL:** `/api/v1/users/{id}/toggle-status`
*   **Description:** Toggles the active/inactive status of a single user.
*   **Path Parameters:**
    *   `id` (string, required): The unique identifier of the user.
*   **Request Body:** (`application/json`)
    ```json
    {
      "status": "Active" // or "Inactive" or "Suspended"
    }
    ```
*   **Success Response:** `200 OK`
    ```json
    {
      "id": "USR-000421",
      "fullName": "Sarah Mutiso",
      // ... other user fields with updated status
      "status": "Inactive"
    }
    ```
*   **Error Responses:** `400 Bad Request`, `404 Not Found`, `403 Forbidden`, `500 Internal Server Error`
*   **Authentication/Authorization:** Requires authenticated user with permissions to manage user status.

---

## 3. General Considerations for Backend (Django)

*   **User Authentication and Authorization:** Django's built-in `User` model and authentication system are a strong starting point. Permissions should be tied to roles (which we defined previously) and checked at the API endpoint level.
*   **Password Management:** Implement secure password hashing. For `passwordMethod: 'invite'`, the backend should generate a secure temporary password and send an email with a password reset link. For `'manual'`, validate password strength.
*   **Email Services:** Integration with an email service will be necessary for sending password reset links and potentially initial user invitations.
*   **Unique Constraints:** Ensure `email` addresses are unique across all users in the database.
*   **Filtering and Sorting:** Utilize Django ORM's `filter`, `order_by`, and pagination (e.g., Django REST Framework's `PageNumberPagination` or `LimitOffsetPagination`) for efficient data retrieval.
*   **Error Handling:** Consistent and informative error responses (e.g., 400 for bad input, 404 for not found, 403 for forbidden actions).
*   **API Versioning:** Continue using `/api/v1/` for consistency.
*   **Audit Logging:** Log significant user actions (creation, updates, status changes, deletions) for accountability.
*   **Soft Deletion:** Consider implementing soft deletion for users instead of hard deletion, especially if user data might be needed for historical records or auditing (e.g., setting an `is_deleted` flag). 