# Transfers Management API Documentation

This document outlines the API endpoints required for the Transfers Management feature, enabling seamless integration with the existing frontend.

---

## 1. Data Models

### 1.1. `FolderCategory`
Represents categories for folders that can be transferred.

```typescript
type FolderCategory = 'confidential' | 'official' | 'academic' | 'other';
```

### 1.2. `RetentionClass`
Represents retention classifications for folders.

```typescript
type RetentionClass = 'a' | 'b' | 'c';
```

### 1.3. `TransferFolder`
Represents a folder object specifically for transfer purposes (can be created or existing).

```typescript
interface TransferFolder {
  id: string;
  title: string;
  subject: string;
  category: FolderCategory;
  retentionClass: RetentionClass;
  description?: string;
  createdAt: string; // ISO 8601 string
  createdBy: string; // User ID or name
}
```

### 1.4. `AttachedFile`
Represents a file attached to a transfer.

```typescript
interface AttachedFile {
  id: string;
  fileName: string;
  fileType: string; // e.g., 'pdf', 'docx'
  fileSize: number; // in bytes
  uploadedBy: string; // User ID or name
  uploadedAt: string; // ISO 8601 string
  isSelected: boolean; // Frontend specific, not for backend storage
}
```

### 1.5. `RoutingStep`
Represents a step in the transfer's routing process.

```typescript
interface RoutingStep {
  id: string; // Unique ID for the step (backend-generated)
  stepNumber: number;
  unitOffice: string; // Name or ID of the unit/office
  responsibleUser: string; // Name or ID of the responsible user at this step
  dueDate?: string; // ISO 8601 string, optional
  status: 'pending' | 'in-progress' | 'completed' | 'overdue';
}
```

### 1.6. `Transfer` (Core Model)
Represents a comprehensive transfer object.

```typescript
interface Transfer {
  id: string;
  folderId: string;
  folder: TransferFolder; // Embedded folder details
  attachedFiles: AttachedFile[]; // List of attached files
  routingSteps: RoutingStep[]; // Sequence of routing steps
  deliveryMethod: 'self' | 'agent';
  assignedAgent?: { id: string; name: string; notes?: string; }; // Basic agent info if assigned
  priority: 'normal' | 'urgent' | 'immediate';
  tags: string[];
  notifications: {
    inApp: boolean;
    email: boolean;
    sms: boolean;
  };
  status: 'draft' | 'submitted' | 'in-transit' | 'delivered' | 'cancelled';
  createdAt: string; // ISO 8601 string
  createdBy: string; // User ID or name
  submittedAt?: string; // ISO 8601 string, if submitted
  // Fields specific to different views/pages (e.g., ActiveTransfer, OverdueTransfer) are variations of this core.
}
```

### 1.7. `CreateTransferRequest`
Represents the data structure for creating a new transfer.

```typescript
interface CreateTransferRequest {
  folderOption: 'create' | 'existing';
  folder?: {
    title: string;
    subject: string;
    category: FolderCategory;
    retentionClass: RetentionClass;
    description?: string;
  }; // Required if folderOption is 'create'
  existingFolderId?: string; // Required if folderOption is 'existing'
  attachedFileIds: string[]; // IDs of already uploaded files or temporary IDs for new files
  routingSteps: Array<{ unitOffice: string; responsibleUser: string; dueDate?: string; }>; // Without id/status
  deliveryMethod: 'self' | 'agent';
  assignedAgentId?: string; // Required if deliveryMethod is 'agent' and autoAssignAgent is false
  agentNotes?: string; // Notes for the agent
  priority: 'normal' | 'urgent' | 'immediate';
  tags: string[];
  notifications: {
    inApp: boolean;
    email: boolean;
    sms: boolean;
  };
  // autoAssignAgent: boolean; // Frontend field, backend determines agent assignment
}
```

### 1.8. `TransferFilters` (Base)
Base interface for transfer filtering.

```typescript
interface BaseFilters {
  status?: string; // Specific status (e.g., 'in_transit', 'completed', 'draft', 'overdue', 'pending_review')
  priority?: string; // 'normal' | 'urgent' | 'immediate'
  dateRangeFrom?: string; // ISO 8601 start date
  dateRangeTo?: string; // ISO 8601 end date
  searchQuery?: string; // General search term for folder title, ID, agent name etc.
}

interface TransferFilters extends BaseFilters {
  owningUnit?: string; // For Active, Overdue
  assignedAgent?: string; // For Active, Overdue
  // For Returns
  originUnit?: string;
  destinationUnit?: string;
  returnReason?: string;
  // For Completed
  deliveryMode?: string; // 'self' | 'agent'
  rating?: string; // For completed transfers
  // For Drafts
  progress?: string; // 'folder_setup' | 'files_attached' | 'routing_defined' | 'ready_to_submit'
  createdBy?: string; // For Drafts, History
  // For Overdue
  overdueDuration?: string; // e.g., '3+days', 'week', 'month'
  currentOffice?: string;
  fileType?: string;
  // For History
  // (Combines filters from other pages as needed)
}
```

---

## 2. API Endpoints

All endpoints should be prefixed with `/api/v1/transfers`.

### 2.1. Create New Transfer

*   **HTTP Method:** `POST`
*   **Endpoint URL:** `/api/v1/transfers`
*   **Description:** Creates a new transfer, either by linking to an existing folder or creating a new one, attaching files, defining routing, and setting delivery/metadata.
*   **Request Body:** (`application/json`)
    ```json
    {
      "folderOption": "create",
      "folder": {
        "title": "New Folder Title",
        "subject": "Subject of new folder",
        "category": "official",
        "retentionClass": "a",
        "description": "Optional description for the new folder"
      },
      "attachedFileIds": ["file-temp-123", "file-existing-456"], // Temporary IDs for new uploads, or actual IDs for existing files
      "routingSteps": [
        { "unitOffice": "HR Department", "responsibleUser": "user-hr-manager", "dueDate": "2024-06-01T00:00:00Z" },
        { "unitOffice": "Finance Office", "responsibleUser": "user-finance-head" }
      ],
      "deliveryMethod": "agent",
      "assignedAgentId": "agent-xyz", // Required if deliveryMethod is 'agent' and not auto-assigned
      "agentNotes": "Deliver by end of day.",
      "priority": "urgent",
      "tags": ["confidential", "budget"],
      "notifications": {
        "inApp": true,
        "email": true,
        "sms": false
      }
    }
    ```
    *   **Note:** File uploads might be a separate pre-process, where file IDs are then passed in `attachedFileIds`.
*   **Success Response:** `201 Created`
    ```json
    {
      "id": "TRF-2024-0001",
      "folderId": "FOLDER-2024-0001",
      "status": "submitted",
      // ... other transfer details from the core Transfer interface
    }
    ```
*   **Error Responses:** `400 Bad Request`, `403 Forbidden`, `404 Not Found` (for existing folder/agent IDs), `500 Internal Server Error`
*   **Authentication/Authorization:** Requires authenticated user with permissions to create transfers.

### 2.2. Get All Active Transfers

*   **HTTP Method:** `GET`
*   **Endpoint URL:** `/api/v1/transfers/active`
*   **Description:** Retrieves a list of active (in-progress, picked-up, pending receipt) transfers.
*   **Query Parameters:** (Based on `ActiveTransfer` and `TransferFilters`)
    *   `searchQuery` (string, optional)
    *   `status` (string, optional): `in_transit`, `picked_up`, `pending_receipt`
    *   `priority` (string, optional)
    *   `dateRangeFrom`, `dateRangeTo` (string, optional): For `dateInitiated` or `lastUpdated`
    *   `owningUnit` (string, optional)
    *   `assignedAgent` (string, optional): Agent ID
    *   `sortBy`, `sortOrder`, `page`, `limit`
*   **Success Response:** `200 OK`
    ```json
    {
      "transfers": [
        {
          "id": "TF-20250524-ENG-0032",
          "folderTitle": "Exam Appeals / Engineering",
          "fileCount": 3,
          "originUnit": "Engineering Dept",
          "currentStep": "With Science HOD",
          "nextStep": "Engineering HOD",
          "deliveryMode": "agent",
          "agentName": "John Doe",
          "priority": "urgent",
          "dateInitiated": "2025-05-24T09:15:00Z",
          "lastUpdated": "2025-05-24T13:22:00Z",
          "transferStatus": "in_transit"
        }
      ],
      "totalItems": 24,
      "totalPages": 3,
      "currentPage": 1,
      "itemsPerPage": 10
    }
    ```
*   **Error Responses:** `500 Internal Server Error`
*   **Authentication/Authorization:** Requires authenticated user. Relevant viewing permissions.

### 2.3. Get All Overdue Transfers

*   **HTTP Method:** `GET`
*   **Endpoint URL:** `/api/v1/transfers/overdue`
*   **Description:** Retrieves a list of overdue transfers.
*   **Query Parameters:** (Based on `OverdueTransfer` and `OverdueFilters`)
    *   `searchQuery` (string, optional)
    *   `overdueDuration` (string, optional): e.g., '3+days', 'week', 'month'
    *   `priority` (string, optional)
    *   `originUnit` (string, optional)
    *   `currentOffice` (string, optional)
    *   `assignedAgent` (string, optional)
    *   `fileType` (string, optional)
    *   `sortBy`, `sortOrder`, `page`, `limit`
*   **Success Response:** `200 OK`
    ```json
    {
      "transfers": [
        {
          "id": "TF-20250518-LAW-0041",
          "folderTitle": "Misconduct Review Case",
          "fileCount": 8,
          "originUnit": "Law Department",
          "currentStep": "Dean of Students",
          "expectedDeliveryDate": "2025-05-20T00:00:00Z",
          "overdueDays": 8,
          "overdueBy": "8 Days",
          "assignedAgent": "John Doe",
          "deliveryMode": "agent",
          "priority": "immediate",
          "status": "Stuck at Dean's Office",
          "overdueSeverity": "severe"
        }
      ],
      "totalItems": 18,
      "totalPages": 2,
      "currentPage": 1,
      "itemsPerPage": 10
    }
    ```
*   **Error Responses:** `500 Internal Server Error`
*   **Authentication/Authorization:** Requires authenticated user. Relevant viewing permissions.

### 2.4. Get All Completed Transfers

*   **HTTP Method:** `GET`
*   **Endpoint URL:** `/api/v1/transfers/completed`
*   **Description:** Retrieves a list of completed transfers.
*   **Query Parameters:** (Based on `CompletedTransfer` and `CompletedFilters`)
    *   `searchQuery` (string, optional)
    *   `priority` (string, optional)
    *   `dateRangeFrom`, `dateRangeTo` (string, optional): For `dateCompleted`
    *   `originUnit` (string, optional)
    *   `destinationUnit` (string, optional)
    *   `deliveryMode` (string, optional)
    *   `rating` (string, optional): e.g., '5', '4', '3', '2', '1'
    *   `sortBy`, `sortOrder`, `page`, `limit`
*   **Success Response:** `200 OK`
    ```json
    {
      "transfers": [
        {
          "id": "TF-20250524-ENG-0032",
          "folderTitle": "Student Grade Appeals",
          "fileCount": 4,
          "originUnit": "Engineering Dept",
          "destinationUnit": "Academic Registry",
          "deliveryMode": "agent",
          "agentName": "John Doe",
          "priority": "urgent",
          "dateInitiated": "2025-05-22T09:00:00Z",
          "dateCompleted": "2025-05-24T14:30:00Z",
          "completionTime": "2.2 days",
          "deliveryConfirmation": "Electronic signature verified",
          "receivedBy": "Dr. Sarah Johnson",
          "rating": 5
        }
      ],
      "totalItems": 89,
      "totalPages": 9,
      "currentPage": 1,
      "itemsPerPage": 10
    }
    ```
*   **Error Responses:** `500 Internal Server Error`
*   **Authentication/Authorization:** Requires authenticated user. Relevant viewing permissions.

### 2.5. Get All Draft Transfers

*   **HTTP Method:** `GET`
*   **Endpoint URL:** `/api/v1/transfers/drafts`
*   **Description:** Retrieves a list of draft transfers.
*   **Query Parameters:** (Based on `DraftTransfer` and `DraftFilters`)
    *   `searchQuery` (string, optional)
    *   `progress` (string, optional): `folder_setup`, `files_attached`, `routing_defined`, `ready_to_submit`
    *   `priority` (string, optional)
    *   `dateRangeFrom`, `dateRangeTo` (string, optional): For `lastModified`
    *   `createdBy` (string, optional): User ID
    *   `sortBy`, `sortOrder`, `page`, `limit`
*   **Success Response:** `200 OK`
    ```json
    {
      "transfers": [
        {
          "id": "DRAFT-20250524-ENG-0045",
          "folderTitle": "Student Grade Appeals",
          "fileCount": 3,
          "lastModified": "2025-05-24T14:30:00Z",
          "createdBy": "John Doe",
          "progress": "ready_to_submit",
          "priority": "urgent",
          "deliveryMode": "agent",
          "agentName": "Jane Smith"
        }
      ],
      "totalItems": 12,
      "totalPages": 2,
      "currentPage": 1,
      "itemsPerPage": 10
    }
    ```
*   **Error Responses:** `500 Internal Server Error`
*   **Authentication/Authorization:** Requires authenticated user. Only drafts created by the requesting user or users with admin/supervisory access.

### 2.6. Get All Returned Transfers

*   **HTTP Method:** `GET`
*   **Endpoint URL:** `/api/v1/transfers/returns`
*   **Description:** Retrieves a list of returned transfers.
*   **Query Parameters:** (Based on `ReturnTransfer` and `ReturnFilters`)
    *   `searchQuery` (string, optional)
    *   `status` (string, optional): `pending_review`, `approved`, `rejected`
    *   `priority` (string, optional)
    *   `dateRangeFrom`, `dateRangeTo` (string, optional): For `returnDate`
    *   `originUnit` (string, optional)
    *   `destinationUnit` (string, optional)
    *   `returnReason` (string, optional)
    *   `sortBy`, `sortOrder`, `page`, `limit`
*   **Success Response:** `200 OK`
    ```json
    {
      "transfers": [
        {
          "id": "RTN-20250524-ENG-0012",
          "folderTitle": "Student Grade Appeals",
          "fileCount": 4,
          "originUnit": "Engineering Dept",
          "destinationUnit": "Academic Registry",
          "deliveryMode": "agent",
          "agentName": "John Doe",
          "priority": "urgent",
          "returnReason": "Incomplete Documentation",
          "returnDate": "2025-05-24T14:30:00Z",
          "returnedBy": "Dr. Sarah Johnson",
          "status": "pending_review",
          "comments": "Missing student signatures on appeal forms"
        }
      ],
      "totalItems": 28,
      "totalPages": 3,
      "currentPage": 1,
      "itemsPerPage": 10
    }
    ```
*   **Error Responses:** `500 Internal Server Error`
*   **Authentication/Authorization:** Requires authenticated user. Relevant viewing permissions.

### 2.7. Get Transfer History

*   **HTTP Method:** `GET`
*   **Endpoint URL:** `/api/v1/transfers/history`
*   **Description:** Retrieves a comprehensive history of all transfers, including completed, cancelled, and failed.
*   **Query Parameters:** (Based on `HistoricalTransfer` and `HistoryFilters`)
    *   `searchQuery` (string, optional)
    *   `status` (string, optional): `completed`, `cancelled`, `failed`, `recalled`
    *   `priority` (string, optional)
    *   `dateRangeFrom`, `dateRangeTo` (string, optional): For `dateInitiated` or `dateCompleted`
    *   `originUnit` (string, optional)
    *   `destinationUnit` (string, optional)
    *   `deliveryMode` (string, optional)
    *   `createdBy` (string, optional)
    *   `sortBy`, `sortOrder`, `page`, `limit`
*   **Success Response:** `200 OK`
    ```json
    {
      "transfers": [
        {
          "id": "TF-20250520-ENG-0028",
          "folderTitle": "Student Grade Appeals",
          "fileCount": 4,
          "originUnit": "Engineering Dept",
          "destinationUnit": "Academic Registry",
          "deliveryMode": "agent",
          "agentName": "John Doe",
          "priority": "urgent",
          "dateInitiated": "2025-05-20T09:00:00Z",
          "dateCompleted": "2025-05-22T14:30:00Z",
          "duration": "2.2 days",
          "finalStatus": "completed",
          "createdBy": "Sarah Wilson"
        }
      ],
      "totalItems": 147,
      "totalPages": 15,
      "currentPage": 1,
      "itemsPerPage": 10
    }
    ```
*   **Error Responses:** `500 Internal Server Error`
*   **Authentication/Authorization:** Requires authenticated user. Relevant viewing permissions.

### 2.8. Get Single Transfer by ID (Detailed View)

*   **HTTP Method:** `GET`
*   **Endpoint URL:** `/api/v1/transfers/{id}`
*   **Description:** Retrieves detailed information for a single transfer by its ID.
*   **Path Parameters:**
    *   `id` (string, required): The unique identifier of the transfer.
*   **Success Response:** `200 OK`
    ```json
    {
      "id": "TF-20250524-ENG-0032",
      "folderId": "F-ENG-001",
      "folder": {
        "id": "F-ENG-001",
        "title": "Exam Appeals / Engineering",
        "subject": "Exam Appeals for Engineering Students",
        "category": "academic",
        "retentionClass": "b",
        "createdAt": "2025-05-20T09:00:00Z",
        "createdBy": "user-sarah"
      },
      "attachedFiles": [
        { "id": "file-abc", "fileName": "appeal_form.pdf", "fileType": "pdf", "fileSize": 102400, "uploadedBy": "user-sarah", "uploadedAt": "2025-05-20T09:05:00Z" }
      ],
      "routingSteps": [
        { "id": "step-1", "stepNumber": 1, "unitOffice": "Engineering Dept", "responsibleUser": "user-eng-hod", "status": "completed", "dueDate": "2025-05-21T00:00:00Z" },
        { "id": "step-2", "stepNumber": 2, "unitOffice": "Science HOD", "responsibleUser": "user-sci-hod", "status": "in-progress" }
      ],
      "deliveryMethod": "agent",
      "assignedAgent": { "id": "agent-john", "name": "John Doe" },
      "priority": "urgent",
      "tags": ["exam", "student"],
      "notifications": { "inApp": true, "email": true, "sms": false },
      "status": "in-transit",
      "createdAt": "2025-05-20T09:00:00Z",
      "createdBy": "user-sarah",
      "submittedAt": "2025-05-20T09:10:00Z"
    }
    ```
*   **Error Responses:** `404 Not Found`, `500 Internal Server Error`
*   **Authentication/Authorization:** Requires authenticated user. Relevant viewing permissions.

### 2.9. Save Transfer as Draft / Update Draft

*   **HTTP Method:** `POST` (for new draft) / `PATCH` (for updating existing draft)
*   **Endpoint URL:** `/api/v1/transfers/drafts` (for new) / `/api/v1/transfers/drafts/{id}` (for update)
*   **Description:** Saves a new transfer as a draft or updates an existing draft.
*   **Request Body:** (`application/json`) - `CreateTransferRequest` or a subset of it.
    *   For new draft: full `CreateTransferRequest` with `status: 'draft'` implied.
    *   For update: fields to update (e.g., `folder`, `attachedFileIds`, `routingSteps`, `deliveryMethod`, `metadata`).
*   **Success Response:** `200 OK` (for update) / `201 Created` (for new draft)
    ```json
    {
      "id": "DRAFT-20250524-ENG-0045",
      "status": "draft",
      "progress": "routing_defined", // Backend tracks progress based on filled fields
      // ... relevant draft transfer fields
    }
    ```
*   **Error Responses:** `400 Bad Request`, `404 Not Found`, `500 Internal Server Error`
*   **Authentication/Authorization:** Requires authenticated user. Only drafts created by the requesting user or admin.

### 2.10. Submit Draft Transfer

*   **HTTP Method:** `POST`
*   **Endpoint URL:** `/api/v1/transfers/drafts/{id}/submit`
*   **Description:** Submits a ready draft transfer, moving it to an active status.
*   **Path Parameters:**
    *   `id` (string, required): The unique identifier of the draft transfer.
*   **Success Response:** `200 OK`
    ```json
    {
      "id": "TF-20250524-ENG-0032",
      "status": "submitted",
      "submittedAt": "2025-05-24T15:00:00Z"
      // ... other updated transfer fields
    }
    ```
*   **Error Responses:** `400 Bad Request` (if draft is incomplete), `404 Not Found`, `403 Forbidden`, `500 Internal Server Error`
*   **Authentication/Authorization:** Requires authenticated user. Only drafts created by the requesting user or admin.

### 2.11. Delete Draft Transfer

*   **HTTP Method:** `DELETE`
*   **Endpoint URL:** `/api/v1/transfers/drafts/{id}`
*   **Description:** Deletes a draft transfer.
*   **Path Parameters:**
    *   `id` (string, required): The unique identifier of the draft transfer.
*   **Success Response:** `204 No Content`
*   **Error Responses:** `404 Not Found`, `403 Forbidden`, `500 Internal Server Error`
*   **Authentication/Authorization:** Requires authenticated user. Only drafts created by the requesting user or admin.

### 2.12. Recall Active Transfer

*   **HTTP Method:** `POST`
*   **Endpoint URL:** `/api/v1/transfers/{id}/recall`
*   **Description:** Recalls an active transfer back to its origin.
*   **Path Parameters:**
    *   `id` (string, required): The unique identifier of the transfer.
*   **Success Response:** `200 OK`
    ```json
    {
      "id": "TF-20250524-ENG-0032",
      "status": "recalled",
      // ... other updated transfer fields
    }
    ```
*   **Error Responses:** `400 Bad Request` (if transfer cannot be recalled), `404 Not Found`, `403 Forbidden`, `500 Internal Server Error`
*   **Authentication/Authorization:** Requires authenticated user with recall permissions.

### 2.13. Escalate Overdue Transfer

*   **HTTP Method:** `POST`
*   **Endpoint URL:** `/api/v1/transfers/{id}/escalate`
*   **Description:** Escalates an overdue transfer.
*   **Path Parameters:**
    *   `id` (string, required): The unique identifier of the overdue transfer.
*   **Success Response:** `200 OK`
    ```json
    {
      "id": "TF-20250518-LAW-0041",
      "isEscalated": true,
      // ... other updated transfer fields
    }
    ```
*   **Error Responses:** `400 Bad Request`, `404 Not Found`, `403 Forbidden`, `500 Internal Server Error`
*   **Authentication/Authorization:** Requires authenticated user with escalation permissions.

### 2.14. Reassign Agent for Transfer

*   **HTTP Method:** `PATCH`
*   **Endpoint URL:** `/api/v1/transfers/{id}/reassign-agent`
*   **Description:** Reassigns an agent to a specific transfer.
*   **Path Parameters:**
    *   `id` (string, required): The unique identifier of the transfer.
*   **Request Body:** (`application/json`)
    ```json
    {
      "newAgentId": "agent-new-id",
      "agentNotes": "Updated notes for new agent."
    }
    ```
*   **Success Response:** `200 OK`
    ```json
    {
      "id": "TF-20250518-LAW-0041",
      "assignedAgent": { "id": "agent-new-id", "name": "New Agent Name" },
      // ... other updated transfer fields
    }
    ```
*   **Error Responses:** `400 Bad Request`, `404 Not Found`, `403 Forbidden`, `500 Internal Server Error`
*   **Authentication/Authorization:** Requires authenticated user with agent reassignment permissions.

### 2.15. Force Return Overdue Transfer

*   **HTTP Method:** `POST`
*   **Endpoint URL:** `/api/v1/transfers/{id}/force-return`
*   **Description:** Forces an overdue transfer to return to its origin.
*   **Path Parameters:**
    *   `id` (string, required): The unique identifier of the overdue transfer.
*   **Success Response:** `200 OK`
    ```json
    {
      "id": "TF-20250518-LAW-0041",
      "status": "returned",
      // ... other updated transfer fields
    }
    ```
*   **Error Responses:** `400 Bad Request`, `404 Not Found`, `403 Forbidden`, `500 Internal Server Error`
*   **Authentication/Authorization:** Requires authenticated user with force return permissions.

### 2.16. Approve Returned Transfer

*   **HTTP Method:** `POST`
*   **Endpoint URL:** `/api/v1/transfers/returns/{id}/approve`
*   **Description:** Approves a returned transfer.
*   **Path Parameters:**
    *   `id` (string, required): The unique identifier of the returned transfer.
*   **Success Response:** `200 OK`
    ```json
    {
      "id": "RTN-20250524-ENG-0012",
      "status": "approved",
      // ... other updated transfer fields
    }
    ```
*   **Error Responses:** `400 Bad Request`, `404 Not Found`, `403 Forbidden`, `500 Internal Server Error`
*   **Authentication/Authorization:** Requires authenticated user with permissions to approve returns.

### 2.17. Reject Returned Transfer

*   **HTTP Method:** `POST`
*   **Endpoint URL:** `/api/v1/transfers/returns/{id}/reject`
*   **Description:** Rejects a returned transfer.
*   **Path Parameters:**
    *   `id` (string, required): The unique identifier of the returned transfer.
*   **Request Body:** (`application/json`)
    ```json
    {
      "reason": "Incomplete re-submission",
      "comments": "Further documentation is required for approval."
    }
    ```
*   **Success Response:** `200 OK`
    ```json
    {
      "id": "RTN-20250524-ENG-0012",
      "status": "rejected",
      "rejectionReason": "Incomplete re-submission",
      // ... other updated transfer fields
    }
    ```
*   **Error Responses:** `400 Bad Request`, `404 Not Found`, `403 Forbidden`, `500 Internal Server Error`
*   **Authentication/Authorization:** Requires authenticated user with permissions to reject returns.

### 2.18. Request Revision for Returned Transfer

*   **HTTP Method:** `POST`
*   **Endpoint URL:** `/api/v1/transfers/returns/{id}/request-revision`
*   **Description:** Requests a revision for a returned transfer.
*   **Path Parameters:**
    *   `id` (string, required): The unique identifier of the returned transfer.
*   **Request Body:** (`application/json`)
    ```json
    {
      "comments": "Please provide revised budget figures."
    }
    ```
*   **Success Response:** `200 OK`
    ```json
    {
      "id": "RTN-20250524-SCI-0011",
      "status": "pending_revision",
      "revisionComments": "Please provide revised budget figures.",
      // ... other updated transfer fields
    }
    ```
*   **Error Responses:** `400 Bad Request`, `404 Not Found`, `403 Forbidden`, `500 Internal Server Error`
*   **Authentication/Authorization:** Requires authenticated user with permissions to request revisions for returns.

### 2.19. Bulk Actions (across different transfer types)

#### 2.19.1. Bulk Recall Transfers
*   **HTTP Method:** `POST`
*   **Endpoint URL:** `/api/v1/transfers/bulk/recall`
*   **Description:** Recalls multiple active transfers.
*   **Request Body:** (`application/json`)
    ```json
    {
      "transferIds": ["TF-001", "TF-002"]
    }
    ```
*   **Success Response:** `200 OK`
*   **Error Responses:** `400 Bad Request`, `403 Forbidden`, `500 Internal Server Error`
*   **Authentication/Authorization:** Requires authenticated user with bulk recall permissions.

#### 2.19.2. Bulk Escalate Transfers
*   **HTTP Method:** `POST`
*   **Endpoint URL:** `/api/v1/transfers/bulk/escalate`
*   **Description:** Escalates multiple overdue transfers.
*   **Request Body:** (`application/json`)
    ```json
    {
      "transferIds": ["TF-003", "TF-004"]
    }
    ```
*   **Success Response:** `200 OK`
*   **Error Responses:** `400 Bad Request`, `403 Forbidden`, `500 Internal Server Error`
*   **Authentication/Authorization:** Requires authenticated user with bulk escalation permissions.

#### 2.19.3. Bulk Reassign Agent
*   **HTTP Method:** `PATCH`
*   **Endpoint URL:** `/api/v1/transfers/bulk/reassign-agent`
*   **Description:** Reassigns an agent for multiple transfers.
*   **Request Body:** (`application/json`)
    ```json
    {
      "transferIds": ["TF-005", "TF-006"],
      "newAgentId": "agent-abc"
    }
    ```
*   **Success Response:** `200 OK`
*   **Error Responses:** `400 Bad Request`, `404 Not Found`, `403 Forbidden`, `500 Internal Server Error`
*   **Authentication/Authorization:** Requires authenticated user with bulk agent reassignment permissions.

#### 2.19.4. Bulk Archive Completed Transfers
*   **HTTP Method:** `POST`
*   **Endpoint URL:** `/api/v1/transfers/bulk/archive`
*   **Description:** Archives multiple completed transfers.
*   **Request Body:** (`application/json`)
    ```json
    {
      "transferIds": ["TF-007", "TF-008"]
    }
    ```
*   **Success Response:** `200 OK`
*   **Error Responses:** `400 Bad Request`, `403 Forbidden`, `500 Internal Server Error`
*   **Authentication/Authorization:** Requires authenticated user with bulk archive permissions.

#### 2.19.5. Bulk Export Transfers Data
*   **HTTP Method:** `GET`
*   **Endpoint URL:** `/api/v1/transfers/bulk/export`
*   **Description:** Exports data for multiple transfers (e.g., as CSV).
*   **Query Parameters:**
    *   `transferIds` (array of strings, required): IDs of transfers to export.
    *   `format` (string, optional): `csv`, `json`.
*   **Success Response:** `200 OK` with file content.
*   **Error Responses:** `400 Bad Request`, `403 Forbidden`, `500 Internal Server Error`
*   **Authentication/Authorization:** Requires authenticated user with export permissions.

#### 2.19.6. Bulk Delete Draft Transfers
*   **HTTP Method:** `DELETE`
*   **Endpoint URL:** `/api/v1/transfers/drafts/bulk/delete`
*   **Description:** Deletes multiple draft transfers.
*   **Request Body:** (`application/json`)
    ```json
    {
      "transferIds": ["DRAFT-001", "DRAFT-002"]
    }
    ```
*   **Success Response:** `204 No Content`
*   **Error Responses:** `400 Bad Request`, `403 Forbidden`, `500 Internal Server Error`
*   **Authentication/Authorization:** Requires authenticated user with bulk draft deletion permissions.

#### 2.19.7. Bulk Submit Draft Transfers
*   **HTTP Method:** `POST`
*   **Endpoint URL:** `/api/v1/transfers/drafts/bulk/submit`
*   **Description:** Submits multiple draft transfers.
*   **Request Body:** (`application/json`)
    ```json
    {
      "transferIds": ["DRAFT-001", "DRAFT-002"]
    }
    ```
*   **Success Response:** `200 OK`
*   **Error Responses:** `400 Bad Request`, `403 Forbidden`, `500 Internal Server Error`
*   **Authentication/Authorization:** Requires authenticated user with bulk draft submission permissions.

---

## 3. General Considerations for Backend (Django)

*   **Complex Relationships:** The `Transfer` model will have complex relationships: `ForeignKey` to `Folder`, `ManyToManyField` to `AttachedFile` (or a separate through model), and `ForeignKey` to `User` (for `createdBy`, `responsibleUser`, `assignedAgent`). Routing steps could be a separate model related to `Transfer`.
*   **State Machine for Transfers:** Implement a robust state machine for `TransferStatus` to manage transitions (e.g., `draft` -> `submitted` -> `in-transit` -> `delivered`/`cancelled`/`recalled`). This can be done using a library or custom logic.
*   **File Handling:** If files are uploaded directly with transfers, Django's `FileField` combined with proper storage backends (e.g., S3 for production) is essential. For large files or external storage, consider using pre-signed URLs.
*   **Asynchronous Tasks:** Operations like bulk actions (export, escalation, assignment) or heavy file processing might benefit from asynchronous tasks (e.g., Celery with Redis/RabbitMQ) to avoid blocking the main request thread.
*   **Notifications:** Integrate with a notification system (email, in-app push, SMS) based on the `notifications` field and transfer status changes.
*   **Audit Trail for Routing:** Track the history of each `RoutingStep` (who completed it, when, notes) for a comprehensive audit trail.
*   **Filtering, Sorting, Pagination:** Django REST Framework's filtering, sorting, and pagination classes will be critical due to the complexity of the data models and multiple list views.
*   **Error Handling:** Consistent and informative error responses across all endpoints.
*   **API Versioning:** Maintain consistency with `/api/v1/`.
*   **Permissions:** Granular permissions are crucial for transfer management, especially for actions like recall, escalate, approve/reject returns, and bulk operations. These should be linked to the `User` and `Role` models.
*   **Scheduler/Cron Jobs:** For features like detecting overdue transfers, consider running periodic tasks.
*   **Concurrency:** Handle concurrent updates to transfers to prevent race conditions, especially during status changes or reassignments.
*   **Data Consistency:** Ensure data consistency across related models (Folders, Users, Agents, Offices) when performing transfer operations.
*   **Custom Metrics:** The dashboard metrics (e.g., `totalActive`, `pickedUpToday`) will require specific database queries and aggregations. 