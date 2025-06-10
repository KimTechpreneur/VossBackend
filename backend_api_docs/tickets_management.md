# Tickets Management API Documentation

This document outlines the API endpoints required for the Tickets Management feature, enabling seamless integration with the existing frontend.

---

## 1. Data Models

### 1.1. `TicketStatus`
Represents the possible statuses of a support ticket.

```typescript
type TicketStatus = 'Open' | 'In Progress' | 'Pending User' | 'Resolved' | 'Closed';
```

### 1.2. `TicketPriority`
Represents the priority levels for a support ticket.

```typescript
type TicketPriority = 'Low' | 'Medium' | 'High' | 'Urgent';
```

### 1.3. `TicketCategory`
Represents the categories a support ticket can fall under.

```typescript
type TicketCategory =
  | 'Technical Issue'
  | 'Billing Inquiry'
  | 'Feature Request'
  | 'Account Access'
  | 'Data Management'
  | 'User Interface'
  | 'Performance Issue'
  | 'General Question'
  | 'Other';
```

### 1.4. `UserSummary`
Represents a summary of a user, used for reporter and assignee.

```typescript
interface UserSummary {
  id: string;
  name: string;
  email: string;
  avatarUrl?: string; // Optional: URL to user's avatar
}
```

### 1.5. `TicketAttachment`
Represents a file attached to a ticket or a comment.

```typescript
interface TicketAttachment {
  id: string;
  fileName: string;
  fileUrl: string; // URL to access the attachment
  fileType: string; // e.g., 'image/png', 'application/pdf'
  fileSize: number; // in bytes
  uploadedAt: string; // ISO date string
}
```

### 1.6. `TicketComment`
Represents a comment or internal note on a ticket.

```typescript
interface TicketComment {
  id: string;
  user: UserSummary; // User who made the comment
  text: string;
  timestamp: string; // ISO date string
  isInternalNote: boolean; // True if it's an internal note, false for public comment
  attachments?: TicketAttachment[];
}
```

### 1.7. `Ticket`
Represents a comprehensive support ticket object.

```typescript
interface Ticket {
  id: string; // e.g., TCK-2024-00001 (backend generated)
  title: string;
  description: string; // Detailed description (can support Markdown/HTML)
  status: TicketStatus;
  priority: TicketPriority;
  category: TicketCategory;
  reporter: UserSummary; // User who created the ticket
  assignee?: UserSummary; // Optional: Admin/support assigned to the ticket
  createdAt: string; // ISO date string
  updatedAt: string; // ISO date string
  resolvedAt?: string; // ISO date string, if resolved
  closedAt?: string; // ISO date string, if closed
  tags?: string[]; // Optional keywords
  attachments?: TicketAttachment[]; // Initial attachments with the ticket
  comments: TicketComment[];
  lastReplyBy?: 'User' | 'Support'; // Indicates who last replied
  dueBy?: string; // ISO date string, if applicable
}
```

### 1.8. `TicketFilters`
Represents the filtering and sorting parameters for fetching tickets.

```typescript
interface TicketFilters {
  status?: TicketStatus | 'All';
  priority?: TicketPriority | 'All';
  category?: TicketCategory | 'All';
  assigneeId?: string | 'All' | 'Unassigned'; // Filter by assignee user ID
  reporterId?: string | 'All'; // Filter by reporter user ID
  searchTerm?: string; // General search for ID, title, reporter/assignee name, tags
  dateFrom?: string; // ISO date string for createdAt start range
  dateTo?: string; // ISO date string for createdAt end range
  sortBy?: keyof Ticket | 'relevance'; // Field to sort by
  sortDirection?: 'asc' | 'desc';
}
```

### 1.9. `CreateTicketData`
Represents the data structure for creating a new ticket.

```typescript
interface CreateTicketData {
  title: string;
  description: string;
  category: TicketCategory;
  priority: TicketPriority;
  attachments?: File[]; // Frontend: File objects for upload. Backend: This will need to handle file uploads separately.
}
```

### 1.10. `AddCommentData`
Represents the data structure for adding a comment to a ticket.

```typescript
interface AddCommentData {
  text: string;
  isInternalNote: boolean;
  attachments?: File[]; // Frontend: File objects for upload. Backend: This will need to handle file uploads separately.
}
```

---

## 2. API Endpoints

All endpoints should be prefixed with `/api/v1/tickets`.

### 2.1. Create New Ticket

*   **HTTP Method:** `POST`
*   **Endpoint URL:** `/api/v1/tickets`
*   **Description:** Allows a user to submit a new support ticket.
*   **Request Body:** (`application/json` or `multipart/form-data` if direct file upload is supported)
    ```json
    {
      "title": "Login button not working on Safari",
      "description": "The login button is unresponsive when clicked on Safari browser version 15.3.",
      "category": "Technical Issue",
      "priority": "High",
      "attachments": ["file-id-1", "file-id-2"] // Array of uploaded file IDs, if files are pre-uploaded
      // Alternatively, files could be part of multipart/form-data directly
    }
    ```
*   **Success Response:** `201 Created`
    ```json
    {
      "id": "TCK-2024-00001",
      "title": "Login button not working on Safari",
      "status": "Open",
      "createdAt": "2024-05-26T10:00:00Z",
      "reporter": { "id": "user-123", "name": "Alice Wonderland", "email": "alice@example.com" }
      // ... other relevant ticket details
    }
    ```
*   **Error Responses:** `400 Bad Request` (Validation errors), `401 Unauthorized`, `500 Internal Server Error`
*   **Authentication/Authorization:** Requires authenticated user. User can create tickets.

### 2.2. Get All Tickets

*   **HTTP Method:** `GET`
*   **Endpoint URL:** `/api/v1/tickets`
*   **Description:** Retrieves a list of all tickets, with support for searching, filtering, and pagination.
*   **Query Parameters:** (Based on `TicketFilters`)
    *   `status` (string, optional): Filter by `TicketStatus`.
    *   `priority` (string, optional): Filter by `TicketPriority`.
    *   `category` (string, optional): Filter by `TicketCategory`.
    *   `assigneeId` (string, optional): Filter by assignee's user ID. Use `unassigned` for tickets without an assignee.
    *   `reporterId` (string, optional): Filter by reporter's user ID.
    *   `searchTerm` (string, optional): Search for keywords in ID, title, reporter/assignee name, or tags.
    *   `dateFrom`, `dateTo` (string, optional): Filter by `createdAt` date range.
    *   `sortBy` (string, optional): Field to sort by (`createdAt`, `updatedAt`, `priority`, `status`, `title`, `relevance`). Default: `createdAt`.
    *   `sortDirection` (string, optional): Sort direction (`asc` or `desc`). Default: `desc`.
    *   `page` (number, optional): Current page number (1-indexed). Default: `1`.
    *   `limit` (number, optional): Number of items per page. Default: `10`.
*   **Success Response:** `200 OK`
    ```json
    {
      "tickets": [
        {
          "id": "TCK-2024-00001",
          "title": "Login button not working on Safari",
          "status": "Open",
          "priority": "High",
          "category": "Technical Issue",
          "reporter": { "id": "user-123", "name": "Alice Wonderland", "email": "alice@example.com" },
          "assignee": { "id": "admin-456", "name": "Bob The Builder", "email": "bob@example.com" },
          "createdAt": "2024-03-10T10:00:00Z",
          "updatedAt": "2024-03-11T14:30:00Z",
          "lastReplyBy": "User",
          "tags": ["login", "safari", "bug"]
        }
      ],
      "totalItems": 50,
      "totalPages": 5,
      "currentPage": 1,
      "itemsPerPage": 10
    }
    ```
*   **Error Responses:** `401 Unauthorized`, `500 Internal Server Error`
*   **Authentication/Authorization:** Requires authenticated user. Users can typically view their own tickets. Admins/Support can view all or assigned tickets.

### 2.3. Get Single Ticket by ID

*   **HTTP Method:** `GET`
*   **Endpoint URL:** `/api/v1/tickets/{id}`
*   **Description:** Retrieves detailed information for a single ticket, including all comments and attachments.
*   **Path Parameters:**
    *   `id` (string, required): The unique identifier of the ticket.
*   **Success Response:** `200 OK`
    ```json
    {
      "id": "TCK-2024-00001",
      "title": "Login button not working on Safari",
      "description": "The login button is unresponsive when clicked on Safari browser version 15.3. It works fine on Chrome and Firefox.",
      "status": "Open",
      "priority": "High",
      "category": "Technical Issue",
      "reporter": { "id": "user-123", "name": "Alice Wonderland", "email": "alice@example.com" },
      "assignee": { "id": "admin-456", "name": "Bob The Builder", "email": "bob@example.com" },
      "createdAt": "2024-03-10T10:00:00Z",
      "updatedAt": "2024-03-11T14:30:00Z",
      "resolvedAt": null,
      "closedAt": null,
      "tags": ["login", "safari", "bug"],
      "attachments": [
        { "id": "att-1", "fileName": "screenshot.png", "fileUrl": "https://example.com/attachments/screenshot.png", "fileType": "image/png", "fileSize": 500000, "uploadedAt": "2024-03-10T10:02:00Z" }
      ],
      "comments": [
        {
          "id": "comment-1",
          "user": { "id": "user-123", "name": "Alice Wonderland", "email": "alice@example.com" },
          "text": "I already tried clearing cache and cookies, issue persists.",
          "timestamp": "2024-03-10T10:05:00Z",
          "isInternalNote": false
        }
      ],
      "lastReplyBy": "User",
      "dueBy": null
    }
    ```
*   **Error Responses:** `404 Not Found`, `401 Unauthorized`, `403 Forbidden`, `500 Internal Server Error`
*   **Authentication/Authorization:** Requires authenticated user. Users can view their own tickets. Admins/Support can view all or assigned tickets.

### 2.4. Update Ticket Status

*   **HTTP Method:** `PATCH`
*   **Endpoint URL:** `/api/v1/tickets/{id}/status`
*   **Description:** Updates the status of an existing ticket.
*   **Path Parameters:**
    *   `id` (string, required): The unique identifier of the ticket.
*   **Request Body:** (`application/json`)
    ```json
    {
      "status": "In Progress"
    }
    ```
*   **Success Response:** `200 OK`
    ```json
    {
      "id": "TCK-2024-00001",
      "status": "In Progress",
      "updatedAt": "2024-05-26T11:00:00Z"
      // ... other relevant updated ticket fields
    }
    ```
*   **Error Responses:** `400 Bad Request`, `404 Not Found`, `401 Unauthorized`, `403 Forbidden`, `500 Internal Server Error`
*   **Authentication/Authorization:** Requires authenticated user with permissions to update ticket status (typically admin/support roles).

### 2.5. Update Ticket Priority

*   **HTTP Method:** `PATCH`
*   **Endpoint URL:** `/api/v1/tickets/{id}/priority`
*   **Description:** Updates the priority of an existing ticket.
*   **Path Parameters:**
    *   `id` (string, required): The unique identifier of the ticket.
*   **Request Body:** (`application/json`)
    ```json
    {
      "priority": "Urgent"
    }
    ```
*   **Success Response:** `200 OK`
    ```json
    {
      "id": "TCK-2024-00001",
      "priority": "Urgent",
      "updatedAt": "2024-05-26T11:05:00Z"
      // ... other relevant updated ticket fields
    }
    ```
*   **Error Responses:** `400 Bad Request`, `404 Not Found`, `401 Unauthorized`, `403 Forbidden`, `500 Internal Server Error`
*   **Authentication/Authorization:** Requires authenticated user with permissions to update ticket priority (typically admin/support roles).

### 2.6. Assign Ticket

*   **HTTP Method:** `PATCH`
*   **Endpoint URL:** `/api/v1/tickets/{id}/assign`
*   **Description:** Assigns a ticket to a support agent or unassigns it.
*   **Path Parameters:**
    *   `id` (string, required): The unique identifier of the ticket.
*   **Request Body:** (`application/json`)
    ```json
    {
      "assigneeId": "admin-789" // Provide user ID of assignee, or null/empty string to unassign
    }
    ```
*   **Success Response:** `200 OK`
    ```json
    {
      "id": "TCK-2024-00001",
      "assignee": { "id": "admin-789", "name": "Clark Kent", "email": "clark@example.com" },
      "updatedAt": "2024-05-26T11:10:00Z"
      // ... other relevant updated ticket fields
    }
    ```
*   **Error Responses:** `400 Bad Request`, `404 Not Found`, `401 Unauthorized`, `403 Forbidden`, `500 Internal Server Error`
*   **Authentication/Authorization:** Requires authenticated user with permissions to assign tickets (admin/support roles).

### 2.7. Add Comment to Ticket

*   **HTTP Method:** `POST`
*   **Endpoint URL:** `/api/v1/tickets/{id}/comments`
*   **Description:** Adds a new comment or internal note to a ticket.
*   **Path Parameters:**
    *   `id` (string, required): The unique identifier of the ticket.
*   **Request Body:** (`application/json` or `multipart/form-data`)
    ```json
    {
      "text": "I have reviewed the logs and found an error related to session management.",
      "isInternalNote": true,
      "attachments": ["file-id-3"] // Array of uploaded file IDs, if files are pre-uploaded
    }
    ```
*   **Success Response:** `201 Created`
    ```json
    {
      "id": "comment-2",
      "user": { "id": "admin-007", "name": "James Bond", "email": "james@example.com" },
      "text": "I have reviewed the logs...",
      "timestamp": "2024-05-26T11:15:00Z",
      "isInternalNote": true,
      "ticketId": "TCK-2024-00001"
    }
    ```
*   **Error Responses:** `400 Bad Request`, `404 Not Found`, `401 Unauthorized`, `403 Forbidden`, `500 Internal Server Error`
*   **Authentication/Authorization:** Requires authenticated user. Users can add public comments. Support/Admins can add internal notes and public comments.

### 2.8. Upload Ticket Attachment

*   **HTTP Method:** `POST`
*   **Endpoint URL:** `/api/v1/tickets/{id}/attachments`
*   **Description:** Uploads a file and associates it with a ticket (either initial attachment or to a comment).
*   **Path Parameters:**
    *   `id` (string, required): The unique identifier of the ticket.
*   **Request Body:** (`multipart/form-data` containing the file)
*   **Success Response:** `201 Created`
    ```json
    {
      "id": "new-attachment-id",
      "fileName": "log_file.txt",
      "fileUrl": "https://example.com/attachments/log_file.txt",
      "fileType": "text/plain",
      "fileSize": 150000,
      "uploadedAt": "2024-05-26T11:18:00Z"
    }
    ```
*   **Error Responses:** `400 Bad Request`, `404 Not Found`, `401 Unauthorized`, `403 Forbidden`, `500 Internal Server Error`
*   **Authentication/Authorization:** Requires authenticated user. Permissions to add attachments to tickets.

### 2.9. Download Ticket Attachment

*   **HTTP Method:** `GET`
*   **Endpoint URL:** `/api/v1/tickets/{ticketId}/attachments/{attachmentId}/download`
*   **Description:** Downloads a specific attachment from a ticket.
*   **Path Parameters:**
    *   `ticketId` (string, required): The ID of the ticket.
    *   `attachmentId` (string, required): The ID of the attachment.
*   **Success Response:** `200 OK` with file content (Content-Type header set appropriately).
*   **Error Responses:** `404 Not Found`, `401 Unauthorized`, `403 Forbidden`, `500 Internal Server Error`
*   **Authentication/Authorization:** Requires authenticated user. Permissions to view/download ticket attachments.

### 2.10. Resolve Ticket

*   **HTTP Method:** `POST`
*   **Endpoint URL:** `/api/v1/tickets/{id}/resolve`
*   **Description:** Marks a ticket as resolved.
*   **Path Parameters:**
    *   `id` (string, required): The unique identifier of the ticket.
*   **Request Body:** (Optional `application/json`)
    ```json
    {
      "resolutionNotes": "Issue fixed by updating X. User confirmed resolution."
    }
    ```
*   **Success Response:** `200 OK`
    ```json
    {
      "id": "TCK-2024-00001",
      "status": "Resolved",
      "resolvedAt": "2024-05-26T12:00:00Z",
      // ... other relevant updated ticket fields
    }
    ```
*   **Error Responses:** `400 Bad Request`, `404 Not Found`, `401 Unauthorized`, `403 Forbidden`, `500 Internal Server Error`
*   **Authentication/Authorization:** Requires authenticated user with permissions to resolve tickets (admin/support roles).

### 2.11. Close Ticket

*   **HTTP Method:** `POST`
*   **Endpoint URL:** `/api/v1/tickets/{id}/close`
*   **Description:** Marks a ticket as closed.
*   **Path Parameters:**
    *   `id` (string, required): The unique identifier of the ticket.
*   **Success Response:** `200 OK`
    ```json
    {
      "id": "TCK-2024-00001",
      "status": "Closed",
      "closedAt": "2024-05-26T12:05:00Z"
      // ... other relevant updated ticket fields
    }
    ```
*   **Error Responses:** `400 Bad Request`, `404 Not Found`, `401 Unauthorized`, `403 Forbidden`, `500 Internal Server Error`
*   **Authentication/Authorization:** Requires authenticated user with permissions to close tickets (admin/support roles, or reporter if `resolved`).

---

## 3. General Considerations for Backend (Django)

*   **Model Relationships:** Define Django models for `Ticket`, `TicketComment`, `TicketAttachment`. `Ticket` should have `ForeignKey` to `User` for `reporter` and `assignee`. `TicketComment` and `TicketAttachment` should have `ForeignKey` to `Ticket`.
*   **Rich Text/Markdown Support:** If `description` and `comment.text` support rich text or Markdown, consider how to store and render this securely (e.g., Markdown field, sanitized HTML).
*   **File Storage:** Implement robust file storage for attachments (e.g., Django's `FileField` or integration with cloud storage like S3).
*   **Email Integration:** Tickets often involve email notifications. Consider integrating with an email service for sending updates to reporters/assignees.
*   **Search and Filtering:** Implement efficient search (e.g., using Django's ORM `Q` objects for `OR` queries across multiple fields) and filtering based on the `TicketFilters`.
*   **State Management:** The `TicketStatus` transitions might benefit from a simple state machine logic.
*   **User Roles and Permissions:** Implement granular permissions for creating, viewing, updating, assigning, resolving, and closing tickets based on user roles.
*   **Real-time Updates (Optional):** For comments, consider using WebSockets (e.g., Django Channels) for real-time updates in the UI.
*   **Audit Logging:** Log significant actions on tickets (status changes, assignments, comment additions, resolutions).
*   **Due Dates:** If `dueBy` is used, implement logic for setting and tracking due dates, and potentially generating overdue notifications.
*   **Public vs. Internal Comments:** Clearly distinguish between public comments and internal notes in the backend logic and database. 