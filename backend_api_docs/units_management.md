'''
# Units Management API Documentation

This document outlines the API endpoints required for the Units Management feature, which allows for the creation, viewing, updating, and deletion of organizational units. All data currently displayed in the frontend is mocked, necessitating new backend APIs for data retrieval and manipulation.

## Data Models

### UnitStatus
Represents the possible statuses for a unit.

```typescript
type UnitStatus = "active" | "inactive" | "archived";
```

### UnitType
Represents the predefined types of organizational units.

```typescript
type UnitType = 
  | "central_admin" 
  | "academic_faculty" 
  | "support_service" 
  | "health_services" 
  | "finance_division" 
  | "audit_unit"
  | "other";
```

### Unit
Represents an organizational unit.

```typescript
interface Unit {
  id: string;
  name: string;
  unitType: UnitType;
  unitCode: string; // Optional, e.g., "UNI-REG"
  headOfUnit: { id: string; name: string }; // Simplified UserSummary, contains ID and Name
  location: string;
  status: UnitStatus;
  staffCount: number; // Number of staff members in the unit
  ongoingTransfers: number; // Number of active transfers involving this unit
  description?: string; // Optional longer description
}
```

### UnitFilters
Represents the criteria for filtering and searching units.

```typescript
interface UnitFilters {
  searchQuery: string; // Search by unit name or code
  unitType: UnitType | "all"; // Filter by unit type
  status: UnitStatus | "all"; // Filter by unit status
}
```

### UnitList
Represents a paginated list of units.

```typescript
interface UnitList {
  items: Unit[];
  totalItems: number;
  currentPage: number;
  totalPages: number;
  filters: UnitFilters; // Reflects applied filters
  sortColumn?: "name" | "unitType" | "unitCode" | "location" | "status" | "headOfUnit"; // Column by which results are sorted
  sortDirection?: "asc" | "desc"; // Sort direction
}
```

### SelectOption
Generic interface for dropdown options (used for unit types and statuses).

```typescript
interface SelectOption {
  value: string;
  label: string;
}
```

## API Endpoints

### Get All Units
Retrieves a paginated and filterable list of all organizational units.

*   **Endpoint:** `GET /api/units`
*   **Parameters:**
    *   `searchQuery` (optional, string): Search by unit name or code.
    *   `unitType` (optional, string): Filter by unit type. Default: "all".
    *   `status` (optional, string): Filter by unit status. Default: "all".
    *   `page` (optional, integer): Current page number. Default: 1.
    *   `pageSize` (optional, integer): Number of items per page. Default: 10 or similar.
    *   `sortBy` (optional, string): Column to sort by (e.g., `name`, `unitType`, `status`).
    *   `sortDirection` (optional, string): Sort direction (`asc` or `desc`).
*   **Response:** `UnitList`

### Get Single Unit by ID
Retrieves the detailed information for a specific organizational unit.

*   **Endpoint:** `GET /api/units/{id}`
*   **URL Parameters:**
    *   `id` (string): The unique identifier of the unit.
*   **Response:** `Unit`

### Create New Unit
Creates a new organizational unit.

*   **Endpoint:** `POST /api/units`
*   **Request Body:**
    ```json
    {
      "name": "string",
      "unitType": "unit_type_enum",
      "unitCode": "string",
      "headOfUnitId": "string", // ID of the user designated as head of unit
      "location": "string",
      "status": "unit_status_enum", // Usually "active" by default on creation
      "description": "string" // Optional
    }
    ```
*   **Response:** `Unit` (the created unit with its assigned ID)

### Update Existing Unit
Updates the details of an existing organizational unit.

*   **Endpoint:** `PATCH /api/units/{id}` (for partial updates) or `PUT /api/units/{id}` (for full replacement)
*   **URL Parameters:**
    *   `id` (string): The unique identifier of the unit to update.
*   **Request Body:** `Partial<Unit>` for PATCH or `Unit` for PUT (without `id`, `staffCount`, `ongoingTransfers` and `headOfUnit` should be `headOfUnitId` for input).
    ```json
    {
      "name"?: "string",
      "unitType"?: "unit_type_enum",
      "unitCode"?: "string",
      "headOfUnitId"?: "string",
      "location"?: "string",
      "status"?: "unit_status_enum",
      "description"?: "string"
    }
    ```
*   **Response:** `Unit` (the updated unit)

### Delete Unit
Deletes an organizational unit by its ID.

*   **Endpoint:** `DELETE /api/units/{id}`
*   **URL Parameters:**
    *   `id` (string): The unique identifier of the unit to delete.
*   **Response:** `204 No Content` or `{
  "message": "Unit deleted successfully."
}`

### Toggle Unit Status
Enables or disables an organizational unit.

*   **Endpoint:** `PATCH /api/units/{id}/toggle-status`
*   **URL Parameters:**
    *   `id` (string): The ID of the unit to toggle status.
*   **Request Body:**
    ```json
    {
      "status": "active" | "inactive" // The desired new status
    }
    ```
*   **Response:** `Unit` (the updated unit with the new status)

### Get Head of Unit Options
Retrieves a list of available users who can be designated as a Head of Unit.

*   **Endpoint:** `GET /api/options/head-of-unit`
*   **Response:** `{ id: string; name: string }[]` (Simplified UserSummary)

### Get Unit Type Options
Retrieves a list of available unit types for dropdowns.

*   **Endpoint:** `GET /api/options/unit-types`
*   **Response:** `SelectOption[]`

### Get Unit Status Options
Retrieves a list of available unit statuses for dropdowns.

*   **Endpoint:** `GET /api/options/unit-statuses`
*   **Response:** `SelectOption[]`
''' 