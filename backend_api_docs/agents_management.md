# Agents Management API Documentation

This document outlines the API endpoints required for the Agents Management feature, enabling seamless integration with the existing frontend.

---

## 1. Data Models

### 1.1. `AgentStatus`
Represents the possible statuses of an agent.

```typescript
type AgentStatus = 'available' | 'in_transit' | 'offline' | 'on_leave' | 'suspended';
```

### 1.2. `BaseOffice`
Represents the base office locations for agents.

```typescript
type BaseOffice = 'Main Campus' | 'East Wing' | 'West Wing' | 'Admin Building';
```

### 1.3. `EmploymentType`
Represents the employment types for agents.

```typescript
type EmploymentType = 'Full Time' | 'Part Time' | 'Contract';
```

### 1.4. `Agent`
Represents an agent in the system.

```typescript
interface Agent {
  id: string; // Unique identifier for the agent
  name: string; // Agent's full name
  email: string; // Agent's email address (unique)
  phone: string; // Agent's phone number
  status: AgentStatus; // Current status of the agent
  baseOffice: BaseOffice; // Agent's assigned base office
  initials: string; // Derived from name, not for backend storage
  employmentType: EmploymentType; // Type of employment
  joinedDate: string; // ISO 8601 timestamp of when the agent joined
  lastActivity: string; // ISO 8601 timestamp of last activity (e.g., login, delivery)
  deliveriesToday: number; // Number of deliveries completed today
  successRate: number; // Agent's delivery success rate (0-100)
}
```

### 1.5. `AgentFilters`
Represents the filtering parameters for fetching agents.

```typescript
interface AgentFilters {
  location: string; // Filter by base office location
  status: AgentStatus | 'all'; // Filter by agent status
  search: string; // General search term for name, ID, location, or status
  // Backend should also support:
  // joinedDateFrom?: string; // ISO 8601 timestamp for start of joined date range
  // joinedDateTo?: string; // ISO 8601 timestamp for end of joined date range
  // sortBy: 'name' | 'email' | 'status' | 'baseOffice' | 'joinedDate' | 'lastActivity' | 'deliveriesToday' | 'successRate'; // Field to sort by
  // sortOrder: 'asc' | 'desc'; // Sort direction
  // page: number; // Current page number for pagination
  // limit: number; // Number of items per page for pagination
}
```

### 1.6. `AgentDelivery`
Represents a delivery performed by an agent (for detailed activity).

```typescript
interface AgentDelivery {
  id: string;
  date: string; // ISO 8601 date of delivery
  status: 'completed' | 'exception';
  from: string; // Origin of delivery
  to: string; // Destination of delivery
  timeTaken: string; // e.g., "2 hours 30 minutes"
  confirmationType?: 'signature' | 'qr_scan';
  exception?: string; // Details if status is 'exception'
}
```

### 1.7. `AgentFormData` (for Create/Update Agent)
Represents the data structure for creating or updating an agent.

```typescript
interface AgentFormData {
  name: string;
  email: string;
  phone: string;
  status: AgentStatus;
  baseOffice: BaseOffice;
  employmentType: EmploymentType;
  joinedDate: string; // ISO 8601 timestamp
  // For updates, all fields can be optional
}
```

---

## 2. API Endpoints

All endpoints should be prefixed with `/api/v1/agents`.

### 2.1. Get All Agents

*   **HTTP Method:** `GET`
*   **Endpoint URL:** `/api/v1/agents`
*   **Description:** Retrieves a list of all agents, with support for searching, filtering, and pagination.
*   **Query Parameters:**
    *   `search` (string, optional): Search term for agent name, ID, base office, or status.
    *   `location` (string, optional): Filter by `baseOffice`.
    *   `status` (string, optional): Filter by `status` (`available`, `in_transit`, etc.). Default: `all`.
    *   `joinedDateFrom` (string, optional): Start date (ISO 8601) for `joinedDate` filter.
    *   `joinedDateTo` (string, optional): End date (ISO 8601) for `joinedDate` filter.
    *   `sortBy` (string, optional): Field to sort by (`name`, `email`, `status`, `baseOffice`, `joinedDate`, `lastActivity`, `deliveriesToday`, `successRate`). Default: `lastActivity`.
    *   `sortOrder` (string, optional): Sort direction (`asc` or `desc`). Default: `desc`.
    *   `page` (number, optional): Current page number (1-indexed). Default: `1`.
    *   `limit` (number, optional): Number of agents per page. Default: `10` (or a sensible backend default).
*   **Success Response:** `200 OK`
    ```json
    {
      "agents": [
        {
          "id": "AGENT-001",
          "name": "John Doe",
          "email": "john.doe@voss.com",
          "phone": "+1234567890",
          "status": "available",
          "baseOffice": "Main Campus",
          "employmentType": "Full Time",
          "joinedDate": "2023-01-01T09:00:00Z",
          "lastActivity": "2024-05-26T14:00:00Z",
          "deliveriesToday": 5,
          "successRate": 98
        }
        // ... more agents
      ],
      "totalItems": 50,
      "totalPages": 5,
      "currentPage": 1,
      "itemsPerPage": 10
    }
    ```
*   **Error Responses:**
    *   `500 Internal Server Error` (Generic error)
*   **Authentication/Authorization:** Requires authenticated user. Agent management permissions.

### 2.2. Get Single Agent by ID

*   **HTTP Method:** `GET`
*   **Endpoint URL:** `/api/v1/agents/{id}`
*   **Description:** Retrieves detailed information for a single agent by their ID.
*   **Path Parameters:**
    *   `id` (string, required): The unique identifier of the agent.
*   **Success Response:** `200 OK`
    ```json
    {
      "id": "AGENT-001",
      "name": "John Doe",
      "email": "john.doe@voss.com",
      "phone": "+1234567890",
      "status": "available",
      "baseOffice": "Main Campus",
      "employmentType": "Full Time",
      "joinedDate": "2023-01-01T09:00:00Z",
      "lastActivity": "2024-05-26T14:00:00Z",
      "deliveriesToday": 5,
      "successRate": 98
      // Potentially include a list of recent deliveries as well
    }
    ```
*   **Error Responses:**
    *   `404 Not Found` (If agent with `id` does not exist)
    *   `500 Internal Server Error`
*   **Authentication/Authorization:** Requires authenticated user. Agent management permissions.

### 2.3. Create New Agent

*   **HTTP Method:** `POST`
*   **Endpoint URL:** `/api/v1/agents`
*   **Description:** Creates a new agent account.
*   **Request Body:** (`application/json`)
    ```json
    {
      "name": "New Agent Name",
      "email": "new.agent@voss.com",
      "phone": "+9876543210",
      "status": "available",
      "baseOffice": "East Wing",
      "employmentType": "Contract",
      "joinedDate": "2024-05-26T10:00:00Z"
    }
    ```
*   **Success Response:** `201 Created`
    ```json
    {
      "id": "AGENT-002",
      "name": "New Agent Name",
      "email": "new.agent@voss.com",
      "phone": "+9876543210",
      "status": "available",
      "baseOffice": "East Wing",
      "employmentType": "Contract",
      "joinedDate": "2024-05-26T10:00:00Z",
      "lastActivity": null,
      "deliveriesToday": 0,
      "successRate": 0
    }
    ```
*   **Error Responses:**
    *   `400 Bad Request` (Invalid input, e.g., missing required fields, invalid email format)
    *   `409 Conflict` (If agent with same email already exists)
    *   `500 Internal Server Error`
*   **Authentication/Authorization:** Requires authenticated user with permissions to create agents.

### 2.4. Update Existing Agent

*   **HTTP Method:** `PATCH`
*   **Endpoint URL:** `/api/v1/agents/{id}`
*   **Description:** Updates an existing agent's information identified by their ID.
*   **Path Parameters:**
    *   `id` (string, required): The unique identifier of the agent to update.
*   **Request Body:** (`application/json`)
    *   Fields are optional. Only send fields that need to be updated.
    ```json
    {
      "phone": "+1122334455",
      "status": "on_leave",
      "baseOffice": "West Wing"
    }
    ```
*   **Success Response:** `200 OK`
    ```json
    {
      "id": "AGENT-001",
      "name": "John Doe",
      "email": "john.doe@voss.com",
      "phone": "+1122334455",
      "status": "on_leave",
      "baseOffice": "West Wing",
      "employmentType": "Full Time",
      "joinedDate": "2023-01-01T09:00:00Z",
      "lastActivity": "2024-05-26T14:30:00Z",
      "deliveriesToday": 5,
      "successRate": 98
    }
    ```
*   **Error Responses:**
    *   `400 Bad Request` (Invalid input)
    *   `404 Not Found` (If agent with `id` does not exist)
    *   `409 Conflict` (If new email conflicts with an existing agent's email)
    *   `500 Internal Server Error`
*   **Authentication/Authorization:** Requires authenticated user with permissions to edit agents.

### 2.5. Delete Agent

*   **HTTP Method:** `DELETE`
*   **Endpoint URL:** `/api/v1/agents/{id}`
*   **Description:** Deletes an agent account by their ID.
*   **Path Parameters:**
    *   `id` (string, required): The unique identifier of the agent to delete.
*   **Success Response:** `204 No Content` (No response body)
*   **Error Responses:**
    *   `404 Not Found` (If agent with `id` does not exist)
    *   `403 Forbidden` (If the agent has active deliveries or other dependencies)
    *   `500 Internal Server Error`
*   **Authentication/Authorization:** Requires authenticated user with permissions to delete agents.

### 2.6. Bulk Deactivate Agents

*   **HTTP Method:** `POST`
*   **Endpoint URL:** `/api/v1/agents/bulk/deactivate`
*   **Description:** Deactivates a list of agent accounts.
*   **Request Body:** (`application/json`)
    ```json
    {
      "agentIds": ["AGENT-001", "AGENT-002"]
    }
    ```
*   **Success Response:** `200 OK` or `204 No Content`
    ```json
    {
      "message": "Selected agents deactivated successfully."
    }
    ```
*   **Error Responses:** `400 Bad Request`, `403 Forbidden`, `500 Internal Server Error`
*   **Authentication/Authorization:** Requires authenticated user with bulk agent management permissions.

### 2.7. Export Agents Data

*   **HTTP Method:** `GET`
*   **Endpoint URL:** `/api/v1/agents/export`
*   **Description:** Exports agent data, potentially with applied filters, as a CSV or other file format.
*   **Query Parameters:** (Same as `Get All Agents`, for filtering the export data)
    *   `search` (string, optional)
    *   `location` (string, optional)
    *   `status` (string, optional)
    *   `joinedDateFrom` (string, optional)
    *   `joinedDateTo` (string, optional)
    *   `format` (string, optional): Desired export format (e.g., `csv`, `json`). Default: `csv`.
*   **Success Response:** `200 OK` with `Content-Type` header set to the appropriate file type (e.g., `text/csv`). The response body will be the file content.
*   **Error Responses:** `400 Bad Request`, `403 Forbidden`, `500 Internal Server Error`
*   **Authentication/Authorization:** Requires authenticated user with export permissions.

### 2.8. Get Agent Deliveries (for Agent Details Page)

*   **HTTP Method:** `GET`
*   **Endpoint URL:** `/api/v1/agents/{id}/deliveries`
*   **Description:** Retrieves a list of deliveries for a specific agent.
*   **Path Parameters:**
    *   `id` (string, required): The unique identifier of the agent.
*   **Query Parameters:**
    *   `filter` (string, optional): Filter deliveries by status (e.g., `completed`, `exception`). Default: `all`.
    *   `dateRange` (string, optional): Filter by date range (e.g., `week`, `month`, `year`). Backend should interpret this to `from` and `to` dates.
    *   `from` (string, optional): ISO 8601 start date for deliveries. Overrides `dateRange` if both provided.
    *   `to` (string, optional): ISO 8601 end date for deliveries. Overrides `dateRange` if both provided.
    *   `page` (number, optional): Current page number.
    *   `limit` (number, optional): Items per page.
*   **Success Response:** `200 OK`
    ```json
    {
      "deliveries": [
        {
          "id": "DEL-001",
          "date": "2024-05-25T11:00:00Z",
          "status": "completed",
          "from": "Office A",
          "to": "Office B",
          "timeTaken": "1h 30m",
          "confirmationType": "signature"
        }
      ],
      "totalItems": 100,
      "totalPages": 10,
      "currentPage": 1,
      "itemsPerPage": 10
    }
    ```
*   **Error Responses:** `404 Not Found`, `500 Internal Server Error`
*   **Authentication/Authorization:** Requires authenticated user with permissions to view agent delivery history.

---

## 3. General Considerations for Backend (Django)

*   **Model Relationships:** Agents can be a specialized type of `User` (e.g., through a OneToOne field or a separate `Agent` model that links to `User`). `BaseOffice` should likely be a ForeignKey to the `Office` model.
*   **Unique Constraints:** Ensure `email` addresses are unique for agents, similar to general users.
*   **Status Management:** Implement logic for handling `AgentStatus` transitions and their implications (e.g., `in_transit` might restrict certain actions).
*   **Metrics:** Implement the logic to calculate `deliveriesToday` and `successRate` from relevant delivery records.
*   **Filtering, Sorting, Pagination:** Utilize Django ORM and Django REST Framework features for efficient data handling.
*   **Error Handling:** Maintain consistent JSON error responses.
*   **API Versioning:** Continue using `/api/v1/`.
*   **Audit Logging:** Log significant agent actions (creation, updates, status changes, deletions, delivery actions).
*   **Export Functionality:** For data export, Django REST Framework and a library like `django-rest-framework-csv` or `django-rest-excel` can simplify the generation of CSV/Excel files. Make sure to handle large exports efficiently (e.g., background tasks).
*   **Activity Tracking:** The `AgentDelivery` model implies a need to track individual deliveries for agents. This should be a separate model with relevant fields and relationships to the `Agent` model and potentially `Folders` or `Transfers`. 