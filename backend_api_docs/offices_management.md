# Offices Management API Documentation

This document outlines the API endpoints required for the Offices Management feature, enabling seamless integration with the existing frontend.

---

## 1. Data Models

### 1.1. `InternalOfficeStatus`
Represents the possible statuses of an internal office.

```typescript
type InternalOfficeStatus = "Active" | "Inactive";
```

### 1.2. `InternalOfficeType`
Represents the categories of internal offices.

```typescript
type InternalOfficeType = "Faculty-Level" | "Departmental" | "Support Office" | "Record Storage"; // Note: 'All' is a filter option, not a type.
```

### 1.3. `InternalOffice`
Represents an internal office in the system. This is the detailed model returned by the backend.

```typescript
interface InternalOffice {
  id: string; // Unique identifier for the office
  officeName: string; // Name of the office
  officeType: InternalOfficeType; // Type of the office
  officeCode: string; // Unique code for the office (e.g., ENG-DEAN)
  headOfOffice: { id: string; name: string; email: string; phone?: string } | null; // Basic user info for the head of office
  staffCount: number; // Number of staff assigned to this office
  status: InternalOfficeStatus; // Current status of the office
  location?: string; // Optional: Physical location of the office
  description?: string; // Optional: Detailed description of the office
  ongoingTransfers?: number; // Optional: Number of ongoing transfers related to this office
  createdDate: string; // ISO 8601 timestamp of creation
  lastUpdatedDate: string; // ISO 8601 timestamp of last update
  updatedBy: string; // Name or ID of the user who last updated it
}
```

### 1.4. `AddInternalOfficeFormData`
Represents the data structure used for creating or updating an office.

```typescript
interface AddInternalOfficeFormData {
  officeName: string;
  officeType: Exclude<InternalOfficeType, 'All'>; // 'All' is for filters, not creation
  officeCode: string; // Frontend handles prefix (e.g., ENG-), backend should expect just the code (e.g., DEAN)
  headOfOfficeId?: string; // Optional: ID of the user designated as head of office
  staffCount: number;
  location?: string; // Optional
  description?: string; // Optional
  status: InternalOfficeStatus; // Active or Inactive
}
```

### 1.5. `InternalOfficeFilters`
Represents the filtering and sorting parameters for fetching offices.

```typescript
interface InternalOfficeFilters {
  searchQuery: string; // General search term for office name, code, or head of office name
  officeType: InternalOfficeType | 'All'; // Filter by office type
  status: InternalOfficeStatus | 'All'; // Filter by office status
  // Backend should also support:
  // sortBy: 'officeName' | 'officeCode' | 'headOfOffice.name' | 'staffCount' | 'status' | 'createdDate' | 'lastUpdatedDate'; // Field to sort by
  // sortOrder: 'asc' | 'desc'; // Sort direction
  // page: number; // Current page number for pagination
  // limit: number; // Number of items per page for pagination
}
```

### 1.6. `OfficeStaffMember`
Represents a staff member assigned to an office.

```typescript
interface OfficeStaffMember {
  id: string;
  fullName: string;
  email: string;
  role: string;
  status: 'Active' | 'Inactive' | 'Pending';
}
```

### 1.7. `OfficeFolderItem`
Represents a recent folder item associated with an office.

```typescript
interface OfficeFolderItem {
  id: string;
  folderId: string; // e.g., VOSS-2023-0047
  title: string;
  status: 'Completed' | 'In Progress' | 'Pending' | 'Archived' | 'Overdue';
  date: string; // ISO 8601 date, e.g., "2024-05-10T00:00:00Z"
  initiatedBy: string; // Name of initiator
}
```

### 1.8. `OfficeTransferItem`
Represents a recent transfer item associated with an office.

```typescript
interface OfficeTransferItem {
  id: string;
  transferId: string; // e.g., VOSS-2023-0051
  date: string; // ISO 8601 date
  party: string; // e.g., "From: Dean's Office" or "To: Faculty Archives"
  status: 'Received' | 'Delivered' | 'In Transit' | 'Pending' | 'Overdue';
  subject: string;
}
```

### 1.9. `InternalOfficeDetailed`
Represents the detailed view of an internal office, including related staff, folders, and transfers.

```typescript
interface InternalOfficeDetailed extends InternalOffice {
  assignedStaff: OfficeStaffMember[];
  recentFolders: OfficeFolderItem[];
  recentTransfersIn: OfficeTransferItem[];
  recentTransfersOut: OfficeTransferItem[];
  activityStats: {
    transfersThisMonth: { value: number; progress: number };
    foldersCreated: { value: number; progress: number };
    avgResponseTime: { value: string; progress: number }; // e.g., "1.2 days"
  };
}
```

---

## 2. API Endpoints

All endpoints should be prefixed with `/api/v1/offices`.

### 2.1. Get All Internal Offices

*   **HTTP Method:** `GET`
*   **Endpoint URL:** `/api/v1/offices`
*   **Description:** Retrieves a list of all internal offices, with support for searching, filtering, and pagination.
*   **Query Parameters:**
    *   `searchQuery` (string, optional): Search term for office name, code, or head of office name.
    *   `officeType` (string, optional): Filter by office type (`Faculty-Level`, `Departmental`, etc.). Default: `All`.
    *   `status` (string, optional): Filter by office status (`Active`, `Inactive`). Default: `All`.
    *   `sortBy` (string, optional): Field to sort by (`officeName`, `officeCode`, `headOfOffice.name`, `staffCount`, `status`, `createdDate`, `lastUpdatedDate`). Default: `officeName`.
    *   `sortOrder` (string, optional): Sort direction (`asc` or `desc`). Default: `asc`.
    *   `page` (number, optional): Current page number (1-indexed). Default: `1`.
    *   `limit` (number, optional): Number of offices per page. Default: `10` (or a sensible backend default).
*   **Success Response:** `200 OK`
    ```json
    {
      "offices": [
        {
          "id": "1",
          "officeName": "Dean's Office",
          "officeType": "Faculty-Level",
          "officeCode": "ENG-DEAN",
          "headOfOffice": { "id": "1", "name": "Prof. N. Akono", "email": "n.akono@voss.edu" },
          "staffCount": 3,
          "status": "Active",
          "location": "Block A, Room 101",
          "description": "Main administrative office for the Faculty of Engineering.",
          "ongoingTransfers": 2,
          "createdDate": "2023-01-15T10:00:00Z",
          "lastUpdatedDate": "2024-05-20T14:30:00Z",
          "updatedBy": "Admin User"
        }
        // ... more offices
      ],
      "totalItems": 7,
      "totalPages": 1,
      "currentPage": 1,
      "itemsPerPage": 10
    }
    ```
*   **Error Responses:**
    *   `500 Internal Server Error` (Generic error)
*   **Authentication/Authorization:** Requires authenticated user. Admin or office management permissions.

### 2.2. Get Single Internal Office by ID (Detailed View)

*   **HTTP Method:** `GET`
*   **Endpoint URL:** `/api/v1/offices/{id}`
*   **Description:** Retrieves detailed information for a single internal office by its ID, including associated staff, recent folders, and transfers.
*   **Path Parameters:**
    *   `id` (string, required): The unique identifier of the office.
*   **Success Response:** `200 OK`
    ```json
    {
      "id": "1",
      "officeName": "Dean's Office",
      "officeType": "Faculty-Level",
      "officeCode": "ENG-DEAN",
      "headOfOffice": { "id": "1", "name": "Prof. N. Akono", "email": "n.akono@voss.edu", "phone": "+254712345678" },
      "staffCount": 3,
      "status": "Active",
      "location": "Block A, Room 101",
      "description": "Main administrative office for the Faculty of Engineering.",
      "ongoingTransfers": 2,
      "createdDate": "2023-01-15T10:00:00Z",
      "lastUpdatedDate": "2024-05-20T14:30:00Z",
      "updatedBy": "Admin User",
      "assignedStaff": [
        { "id": "1", "fullName": "Prof. N. Akono", "email": "n.akono@voss.edu", "role": "Unit Head", "status": "Active" },
        { "id": "8", "fullName": "Jane Doe", "email": "jane.doe@voss.edu", "role": "Staff", "status": "Active" }
      ],
      "recentFolders": [
        { "id": "f1", "folderId": "VOSS-2023-0047", "title": "Faculty Meeting Minutes 2023", "status": "Completed", "date": "2024-05-10T00:00:00Z", "initiatedBy": "Admin User" }
      ],
      "recentTransfersIn": [
        { "id": "t1", "transferId": "VOSS-2023-0051", "date": "2024-05-12T00:00:00Z", "party": "From: Admissions Office", "status": "Received", "subject": "Student Records Batch 2024" }
      ],
      "recentTransfersOut": [
        { "id": "t2", "transferId": "VOSS-2023-0052", "date": "2024-05-15T00:00:00Z", "party": "To: Central Archives", "status": "Delivered", "subject": "Research Project Documents" }
      ],
      "activityStats": {
        "transfersThisMonth": { "value": 15, "progress": 75 },
        "foldersCreated": { "value": 20, "progress": 60 },
        "avgResponseTime": { "value": "1.2 days", "progress": 85 }
      }
    }
    ```
*   **Error Responses:**
    *   `404 Not Found` (If office with `id` does not exist)
    *   `500 Internal Server Error`
*   **Authentication/Authorization:** Requires authenticated user. Admin or appropriate permissions (e.g., view offices).

### 2.3. Create New Internal Office

*   **HTTP Method:** `POST`
*   **Endpoint URL:** `/api/v1/offices`
*   **Description:** Creates a new internal office.
*   **Request Body:** (`application/json`)
    ```json
    {
      "officeName": "New Department",
      "officeType": "Departmental",
      "officeCode": "NEW-DEPT",
      "headOfOfficeId": "user-abc", // Optional: ID of an existing user to set as head
      "staffCount": 5,
      "location": "Main Campus, Building D",
      "description": "A newly established department for advanced studies.",
      "status": "Active"
    }
    ```
*   **Success Response:** `201 Created`
    ```json
    {
      "id": "new-office-id",
      "officeName": "New Department",
      "officeType": "Departmental",
      "officeCode": "NEW-DEPT",
      "headOfOffice": { "id": "user-abc", "name": "Dr. New Head", "email": "new.head@voss.edu" },
      "staffCount": 5,
      "status": "Active",
      "location": "Main Campus, Building D",
      "description": "A newly established department for advanced studies.",
      "ongoingTransfers": 0,
      "createdDate": "2024-05-26T10:00:00Z",
      "lastUpdatedDate": "2024-05-26T10:00:00Z",
      "updatedBy": "Current User"
    }
    ```
*   **Error Responses:**
    *   `400 Bad Request` (Invalid input, e.g., missing required fields, invalid office type/status, non-existent `headOfOfficeId`)
    *   `409 Conflict` (If an office with the same `officeName` or `officeCode` already exists)
    *   `500 Internal Server Error`
*   **Authentication/Authorization:** Requires authenticated user with permissions to create offices.

### 2.4. Update Existing Internal Office

*   **HTTP Method:** `PATCH`
*   **Endpoint URL:** `/api/v1/offices/{id}`
*   **Description:** Updates an existing internal office's information identified by its ID.
*   **Path Parameters:**
    *   `id` (string, required): The unique identifier of the office to update.
*   **Request Body:** (`application/json`)
    *   Fields are optional. Only send fields that need to be updated.
    ```json
    {
      "officeName": "Updated Department Name", // Optional
      "headOfOfficeId": "user-xyz", // Optional: Update head of office
      "status": "Inactive", // Optional: Change status
      "location": "New Building, Floor 5" // Optional
    }
    ```
*   **Success Response:** `200 OK`
    ```json
    {
      "id": "existing-office-id",
      "officeName": "Updated Department Name",
      "officeType": "Departmental",
      "officeCode": "OLD-DEPT",
      "headOfOffice": { "id": "user-xyz", "name": "Dr. XYZ", "email": "xyz@voss.edu" },
      "staffCount": 5,
      "status": "Inactive",
      "location": "New Building, Floor 5",
      "description": "An updated description.",
      "ongoingTransfers": 0,
      "createdDate": "2023-01-01T10:00:00Z",
      "lastUpdatedDate": "2024-05-26T11:30:00Z",
      "updatedBy": "Current User"
    }
    ```
*   **Error Responses:**
    *   `400 Bad Request` (Invalid input)
    *   `404 Not Found` (If office with `id` does not exist)
    *   `409 Conflict` (If new `officeName` or `officeCode` conflicts with an existing office)
    *   `500 Internal Server Error`
*   **Authentication/Authorization:** Requires authenticated user with permissions to edit offices.

### 2.5. Delete Internal Office

*   **HTTP Method:** `DELETE`
*   **Endpoint URL:** `/api/v1/offices/{id}`
*   **Description:** Deletes an internal office by its ID.
*   **Path Parameters:**
    *   `id` (string, required): The unique identifier of the office to delete.
*   **Success Response:** `204 No Content` (No response body)
*   **Error Responses:**
    *   `404 Not Found` (If office with `id` does not exist)
    *   `403 Forbidden` (If the office has associated staff, ongoing transfers, or is considered critical for system operation)
    *   `500 Internal Server Error`
*   **Authentication/Authorization:** Requires authenticated user with permissions to delete offices.

### 2.6. Bulk Update Office Status

*   **HTTP Method:** `POST` or `PATCH`
*   **Endpoint URL:** `/api/v1/offices/bulk/status`
*   **Description:** Updates the status (e.g., Active/Inactive) for multiple offices.
*   **Request Body:** (`application/json`)
    ```json
    {
      "officeIds": ["office-1", "office-2", "office-3"],
      "status": "Inactive"
    }
    ```
*   **Success Response:** `200 OK`
    ```json
    {
      "message": "Selected offices status updated successfully."
    }
    ```
*   **Error Responses:** `400 Bad Request`, `403 Forbidden`, `500 Internal Server Error`
*   **Authentication/Authorization:** Requires authenticated user with bulk office management permissions.

### 2.7. Bulk Delete Offices

*   **HTTP Method:** `POST` or `DELETE`
*   **Endpoint URL:** `/api/v1/offices/bulk/delete`
*   **Description:** Deletes multiple offices by their IDs.
*   **Request Body:** (`application/json`)
    ```json
    {
      "officeIds": ["office-1", "office-2", "office-3"]
    }
    ```
*   **Success Response:** `204 No Content`
*   **Error Responses:** `400 Bad Request`, `403 Forbidden`, `500 Internal Server Error`
*   **Authentication/Authorization:** Requires authenticated user with bulk office deletion permissions.

---

## 3. General Considerations for Backend (Django)

*   **Model Relationships:** Define clear relationships between `Office` and `User` models (e.g., a foreign key for `headOfOffice`). Consider `OfficeStaffMember`, `OfficeFolderItem`, and `OfficeTransferItem` as separate Django models or integrate them into existing models with appropriate foreign keys.
*   **Unique Constraints:** Enforce uniqueness for `officeName` and `officeCode` to prevent duplicate offices.
*   **Cascading Deletes/Referential Integrity:** When deleting an office, decide on the behavior for associated staff, folders, and transfers. Django's `on_delete` options in `ForeignKey` can help manage this.
*   **Validation:** Server-side validation for all incoming data is crucial, including custom validation for `officeCode` format.
*   **Filtering, Sorting, Pagination:** Implement these efficiently using Django ORM and Django REST Framework features.
*   **Error Handling:** Maintain consistent JSON error responses.
*   **API Versioning:** Continue using `/api/v1/`.
*   **Audit Logging:** Log significant office actions (creation, updates, status changes, deletions).
*   **Data Consistency for Related Entities:** When fetching detailed office information, ensure efficient retrieval of associated staff, recent folders, and transfers (e.g., by optimizing database queries or using select_related/prefetch_related). 