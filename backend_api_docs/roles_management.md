# Roles Management API Documentation

This document outlines the API endpoints required for the Roles Management feature, enabling seamless integration with the existing frontend.

---

## 1. Data Models

### 1.1. `Permission`
Represents a specific permission within the system.

```typescript
interface Permission {
  id: string; // Unique identifier for the permission
  name: string; // Display name of the permission (e.g., "View Users")
  module: string; // The module the permission belongs to (e.g., "Users", "Folders")
}
```

### 1.2. `Role`
Represents a user role with associated permissions.

```typescript
interface Role {
  id: string; // Unique identifier for the role
  name: string; // Name of the role (e.g., "Administrator", "Department Head")
  description: string; // Description of the role
  type: "system" | "custom"; // Type of role: system-defined or custom
  status: "active" | "inactive"; // Current status of the role
  permissions: Permission[]; // Array of permissions assigned to this role
  usersCount: number; // Number of users assigned to this role
  createdAt: string; // ISO 8601 timestamp of creation
  lastModified: string; // ISO 8601 timestamp of last modification
  color?: string; // Optional: UI hint for badge color (e.g., "primary", "warning", "purple", "gray")
  isLocked?: boolean; // Optional: Indicates if the role is a system role and cannot be edited/deleted
}
```

### 1.3. `RoleFormData`
Represents the data structure used for creating or updating a role from the frontend.

```typescript
interface RoleFormData {
  name: string; // Name of the role
  description: string; // Description of the role
  type: "system" | "custom"; // Type of role
  permissions: string[]; // Array of permission IDs (strings)
}
```

### 1.4. `RoleFilters`
Represents the filtering and sorting parameters for fetching roles.

```typescript
interface RoleFilters {
  search: string; // General search term for role name or description
  roleType: 'all' | 'system' | 'custom'; // Filter by role type
  userCount: 'all' | 'zero'; // Filter by user count (e.g., roles with zero users)
  recentlyEdited: boolean; // Filter for recently edited roles
  // Backend should also support:
  // sortBy: 'name' | 'usersCount' | 'createdAt' | 'lastModified'; // Field to sort by
  // sortOrder: 'asc' | 'desc'; // Sort direction
  // page: number; // Current page number for pagination
  // limit: number; // Number of items per page for pagination
}
```

---

## 2. API Endpoints

All endpoints should be prefixed with `/api/v1/roles`.

### 2.1. Get All Roles

*   **HTTP Method:** `GET`
*   **Endpoint URL:** `/api/v1/roles`
*   **Description:** Retrieves a list of all roles, with support for filtering, searching, and pagination.
*   **Query Parameters:**
    *   `search` (string, optional): Search term for role name or description.
    *   `roleType` (string, optional): Filter by role type (`system` or `custom`). Default: `all`.
    *   `userCount` (string, optional): Filter by user count (`zero`). Default: `all`.
    *   `recentlyEdited` (boolean, optional): Filter for recently edited roles.
    *   `sortBy` (string, optional): Field to sort by (`name`, `usersCount`, `createdAt`, `lastModified`). Default: `name`.
    *   `sortOrder` (string, optional): Sort direction (`asc` or `desc`). Default: `asc`.
    *   `page` (number, optional): Current page number (1-indexed). Default: `1`.
    *   `limit` (number, optional): Number of roles per page. Default: `10` (or a sensible backend default).
*   **Success Response:** `200 OK`
    ```json
    {
      "roles": [
        {
          "id": "role-123",
          "name": "Administrator",
          "description": "Full access to all system features.",
          "type": "system",
          "status": "active",
          "permissions": [
            { "id": "perm-001", "name": "Manage Users", "module": "Users" },
            { "id": "perm-002", "name": "Manage Roles", "module": "Roles" }
          ],
          "usersCount": 10,
          "createdAt": "2024-01-01T10:00:00Z",
          "lastModified": "2024-05-20T15:30:00Z",
          "color": "primary",
          "isLocked": true
        },
        // ... more roles
      ],
      "totalItems": 50,
      "totalPages": 5,
      "currentPage": 1,
      "itemsPerPage": 10
    }
    ```
*   **Error Responses:**
    *   `500 Internal Server Error` (Generic error)
*   **Authentication/Authorization:** Requires authenticated user. Admin or role management permissions.

### 2.2. Get Single Role by ID

*   **HTTP Method:** `GET`
*   **Endpoint URL:** `/api/v1/roles/{id}`
*   **Description:** Retrieves details of a single role by its ID.
*   **Path Parameters:**
    *   `id` (string, required): The unique identifier of the role.
*   **Success Response:** `200 OK`
    ```json
    {
      "id": "role-123",
      "name": "Administrator",
      "description": "Full access to all system features.",
      "type": "system",
      "status": "active",
      "permissions": [
        { "id": "perm-001", "name": "Manage Users", "module": "Users" },
        { "id": "perm-002", "name": "Manage Roles", "module": "Roles" }
      ],
      "usersCount": 10,
      "createdAt": "2024-01-01T10:00:00Z",
      "lastModified": "2024-05-20T15:30:00Z",
      "color": "primary",
      "isLocked": true
    }
    ```
*   **Error Responses:**
    *   `404 Not Found` (If role with `id` does not exist)
    *   `500 Internal Server Error`
*   **Authentication/Authorization:** Requires authenticated user. Admin or role management permissions.

### 2.3. Create New Role

*   **HTTP Method:** `POST`
*   **Endpoint URL:** `/api/v1/roles`
*   **Description:** Creates a new role with the provided details and permissions.
*   **Request Body:** (`application/json`)
    ```json
    {
      "name": "New Role Name",
      "description": "Description of the new role.",
      "type": "custom",
      "permissions": ["perm-003", "perm-004"] // Array of permission IDs
    }
    ```
*   **Success Response:** `201 Created`
    ```json
    {
      "id": "role-456",
      "name": "New Role Name",
      "description": "Description of the new role.",
      "type": "custom",
      "status": "active",
      "permissions": [
        { "id": "perm-003", "name": "View Reports", "module": "Reports" },
        { "id": "perm-004", "name": "Edit Settings", "module": "Settings" }
      ],
      "usersCount": 0,
      "createdAt": "2024-05-25T10:00:00Z",
      "lastModified": "2024-05-25T10:00:00Z"
    }
    ```
*   **Error Responses:**
    *   `400 Bad Request` (Invalid input, e.g., missing `name`, duplicate role name)
    *   `409 Conflict` (If a role with the same name already exists)
    *   `500 Internal Server Error`
*   **Authentication/Authorization:** Requires authenticated user with permissions to create roles.

### 2.4. Update Existing Role

*   **HTTP Method:** `PUT` (for full replacement) or `PATCH` (for partial update)
    *   **Recommendation:** Use `PATCH` for partial updates to allow for flexibility, but `PUT` can be used if the frontend always sends the full `RoleFormData`. We will document `PATCH` for flexibility.
*   **Endpoint URL:** `/api/v1/roles/{id}`
*   **Description:** Updates an existing role identified by its ID.
*   **Path Parameters:**
    *   `id` (string, required): The unique identifier of the role to update.
*   **Request Body:** (`application/json`)
    *   For `PATCH`, fields are optional. Only send fields that need to be updated.
    ```json
    {
      "name": "Updated Role Name", // Optional
      "description": "Updated description.", // Optional
      "permissions": ["perm-003", "perm-005"] // Optional: Array of new permission IDs
    }
    ```
*   **Success Response:** `200 OK`
    ```json
    {
      "id": "role-456",
      "name": "Updated Role Name",
      "description": "Updated description.",
      "type": "custom",
      "status": "active",
      "permissions": [
        { "id": "perm-003", "name": "View Reports", "module": "Reports" },
        { "id": "perm-005", "name": "Approve Transfers", "module": "Transfers" }
      ],
      "usersCount": 0,
      "createdAt": "2024-05-25T10:00:00Z",
      "lastModified": "2024-05-25T11:30:00Z"
    }
    ```
*   **Error Responses:**
    *   `400 Bad Request` (Invalid input)
    *   `404 Not Found` (If role with `id` does not exist)
    *   `403 Forbidden` (If `isLocked` is true for a system role and attempt to modify it)
    *   `409 Conflict` (If new `name` conflicts with an existing role name)
    *   `500 Internal Server Error`
*   **Authentication/Authorization:** Requires authenticated user with permissions to edit roles. Cannot edit `isLocked` roles.

### 2.5. Delete Role

*   **HTTP Method:** `DELETE`
*   **Endpoint URL:** `/api/v1/roles/{id}`
*   **Description:** Deletes a role by its ID.
*   **Path Parameters:**
    *   `id` (string, required): The unique identifier of the role to delete.
*   **Success Response:** `204 No Content` (No response body)
*   **Error Responses:**
    *   `404 Not Found` (If role with `id` does not exist)
    *   `403 Forbidden` (If `isLocked` is true for a system role, or if role has associated users)
    *   `500 Internal Server Error`
*   **Authentication/Authorization:** Requires authenticated user with permissions to delete roles. Cannot delete `isLocked` roles or roles with `usersCount > 0`.

---

## 3. General Considerations for Backend (Django)

*   **Permissions Management:** The backend will need a robust way to manage permissions and associate them with roles. Consider using Django's built-in `auth.Permission` or a custom permission model.
*   **API Versioning:** The `/api/v1/` prefix is a good standard for API versioning.
*   **Error Handling:** Implement consistent JSON error responses across all endpoints (e.g., using Django REST Framework's exception handling).
*   **Authentication:** Integrate with Django's authentication system (e.g., Token authentication, JWT).
*   **Validation:** Server-side validation for all incoming data is crucial to prevent invalid data and security vulnerabilities.
*   **Database Schema:** The `Role` and `Permission` interfaces should guide the design of your Django models.
*   **Filtering, Sorting, Pagination:** Implement these features efficiently on the backend to handle large datasets. Django REST Framework's `FilterSet` and pagination classes can be very helpful here.
*   **System Roles:** Ensure `isLocked` logic is handled correctly to prevent accidental modification or deletion of predefined system roles.
*   **Audit Logging:** Consider logging who performed what action (create, update, delete) on roles for auditing purposes. 