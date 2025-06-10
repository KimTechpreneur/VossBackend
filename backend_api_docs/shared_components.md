'''
# Shared/Common Components API Documentation

This document outlines common data models, shared API patterns, and utility endpoints that are applicable across multiple features of the VOSS application. Establishing these common components ensures consistency and reusability in backend API development.

## Data Models

### User
Represents a user within the system, often used for `headOfUnit` in Unit/Office or for agent tracking.

```typescript
export interface User {
  id: string;
  name: string;
  email: string;
  department?: string; // Optional department information
  initials?: string; // Optional initials for display
  avatarColor?: string; // Optional color for avatar display
}
```

### SelectOption
A generic interface used for populating dropdowns and selection lists across various features.

```typescript
interface SelectOption {
  value: string; // The internal value (e.g., ID)
  label: string; // The display label
}
```

### Pagination & Filtering Parameters (Common)
Many list-fetching endpoints follow a similar pattern for pagination, filtering, and sorting. These parameters are generally passed as query parameters.

```typescript
interface CommonListParameters {
  page?: number; // Current page number (1-indexed), default 1
  pageSize?: number; // Number of items per page, default varies (e.g., 10, 20, 50)
  searchQuery?: string; // General text search term
  sortBy?: string; // Field name to sort by (e.g., "name", "createdAt")
  sortDirection?: "asc" | "desc"; // Sort order
  // dateFrom?: string; // ISO 8601 date string for start of date range
  // dateTo?: string;   // ISO 8601 date string for end of date range
}
```

## API Patterns and Guidelines

### RESTful Principles

*   **Resource-Oriented:** APIs should be designed around resources (e.g., `/users`, `/roles`, `/folders`).
*   **Standard HTTP Methods:**
    *   `GET`: Retrieve resources.
    *   `POST`: Create new resources.
    *   `PUT`: Full update/replace a resource.
    *   `PATCH`: Partial update a resource.
    *   `DELETE`: Delete a resource.
*   **Status Codes:** Use standard HTTP status codes (e.g., `200 OK`, `201 Created`, `204 No Content`, `400 Bad Request`, `401 Unauthorized`, `403 Forbidden`, `404 Not Found`, `500 Internal Server Error`).

### Pagination

*   **Query Parameters:** `page` and `pageSize` (or `limit` and `offset`) should be used for pagination.
*   **Response Structure:** List endpoints should return an object containing:
    *   `items`: An array of the requested resources.
    *   `totalItems`: Total number of items available (for all pages).
    *   `currentPage`: The current page number.
    *   `totalPages`: The total number of pages.
    *   `filters`: An echo of the applied filters and sorting for clarity.

    ```json
    {
      "items": [...],
      "totalItems": 150,
      "currentPage": 1,
      "totalPages": 15,
      "filters": {"searchQuery": "", "sortBy": "name", "sortDirection": "asc"}
    }
    ```

### Filtering and Searching

*   **Query Parameters:** Filters (e.g., `status`, `unitType`, `dateFrom`, `dateTo`) should generally be passed as query parameters.
*   **Search Term:** A general `searchQuery` parameter can be used for broad text searches across relevant fields.

### Sorting

*   **Query Parameters:** `sortBy` and `sortDirection` (e.g., `?sortBy=name&sortDirection=asc`) should be used for sorting.

### Error Handling

*   **Consistent Error Responses:** API should return consistent JSON error objects for client-side parsing.

    ```json
    {
      "error": "string",
      "message": "string",
      "details": "object" // Optional: more specific error details
    }
    ```

### Authentication and Authorization

*   **Authentication:** Assume a token-based authentication mechanism (e.g., JWT or session tokens) passed in the `Authorization` header (`Bearer Token`).
*   **Authorization (Permissions/Roles):** Backend should enforce permissions based on the authenticated user's roles, as inferred from `Roles Management` and `Users Management`.

## Common Utility Endpoints

### Get Lookup Data / Dropdown Options
Many features require dropdowns populated with dynamic data (e.g., `Unit Types`, `Agent Statuses`, `User Roles`). These should ideally be exposed through dedicated, simple GET endpoints.

*   **Endpoint Pattern:** `GET /api/options/{resource-name}`
*   **Response:** `SelectOption[]`

    *Example: `GET /api/options/unit-types` returns `[{ value: "central_admin", label: "Central Admin" }, ...]`*

### Health Check / Status
An endpoint to check the overall health and status of the backend services.

*   **Endpoint:** `GET /api/health` or `GET /status`
*   **Response:** `200 OK` with a simple status object (e.g., `{"status": "healthy", "version": "1.0.0"}`)
''' 