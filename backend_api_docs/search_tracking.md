'''
# Search and Tracking API Documentation

This document outlines the API endpoints required for the Search and Tracking feature, which allows users to search for files and folders, apply various filters, view search results, and get a detailed transfer trail for specific items. All data currently displayed in the frontend is mocked, necessitating new backend APIs for data retrieval.

## Data Models

### SearchResultItem
Represents a single item (folder or file) returned in search results.

```typescript
interface SearchResultItem {
  id: string; // Unique ID for the table row (can be File ID or Folder ID)
  folderId: string;
  fileName?: string; // Optional, as a search result could be just a folder
  subject?: string; // Subject or title of the folder/file
  fileId?: string; // Optional, if the result is a specific file within a folder
  currentOffice: string; // Current office/unit where the item resides
  currentStatus: "active" | "archived" | "in transit" | "delivered" | "returned" | "overdue" | "in review" | "awaiting pickup" | string; // Current status of the item
  lastActivity: string; // Timestamp or human-readable string (e.g., "2 minutes ago", "2023-10-26 10:30 AM")
}
```

### SearchFilters
Represents the criteria used for searching files and folders.

```typescript
interface SearchFilters {
  searchTerm: string; // General search term for folder ID, file ID, name, or subject
  dateRange?: {
    from?: string; // ISO 8601 date string
    to?: string;   // ISO 8601 date string
  };
  destinationUnit?: string; // ID or name of the destination unit
  office?: string; // ID or name of the internal office (dynamic based on unit)
  fileType?: string; // e.g., "Transcript", "Memo", "Letter"
  currentStatus?: "all" | ItemStatus; // Status of the item
  agentInvolved?: string; // ID or name of an involved agent
  treatmentFolderId?: string; // Specific treatment folder ID
  specificFileId?: string; // Specific file ID
}
```

### SearchResultsList
Represents a paginated list of search results.

```typescript
interface SearchResultsList {
  items: SearchResultItem[];
  totalItems: number;
  currentPage: number;
  totalPages: number;
  filters: SearchFilters; // Reflects the applied filters
  sortColumn?: keyof SearchResultItem | string; // Column by which results are sorted
  sortDirection?: "asc" | "desc"; // Sort direction
}
```

### FileInTrail
Represents a file within a transfer trail.

```typescript
interface FileInTrail {
  id: string;
  name: string;
  type: string; // e.g., "PDF", "DOCX"
}
```

### TransferPathStep
Represents a step in the transfer path of a folder/file.

```typescript
interface TransferPathStep {
  office: string; // Office/unit name
  status: string; // Status at this step (e.g., "Received", "Processed", "Sent")
  timestamp: string; // ISO 8601 date string
  notes?: string; // Optional notes for this step
}
```

### AgentActivity
Represents an activity performed by an agent related to a transfer.

```typescript
interface AgentActivity {
  status: string; // e.g., "Picked up", "In transit", "Delivered"
  timestamp: string; // ISO 8601 date string
  location?: string; // Optional: geographic location of the activity
}
```

### TransferTrail
Represents the complete transfer trail of a specific treatment folder.

```typescript
interface TransferTrail {
  treatmentFolderId: string;
  filesInside: FileInTrail[];
  transferPath: TransferPathStep[];
  currentPosition: {
    office: string;
    status: string; // e.g., "At QA Office - Pending Review"
  };
  agentTracking?: {
    agentName: string; // Name of the agent involved
    activity: AgentActivity[];
  };
}
```

### SelectOption
Generic interface for dropdown options.

```typescript
interface SelectOption {
  value: string;
  label: string;
}
```

## API Endpoints

### Search Files and Folders
Performs a search for files and folders based on various criteria.

*   **Endpoint:** `GET /api/search`
*   **Parameters:**
    *   `searchTerm` (optional, string): General search query (e.g., File ID, Folder ID, Name, Subject).
    *   `dateFrom` (optional, date string): Start date for activity.
    *   `dateTo` (optional, date string): End date for activity.
    *   `destinationUnit` (optional, string): Filter by destination unit ID/name.
    *   `office` (optional, string): Filter by internal office ID/name (might require `destinationUnit`).
    *   `fileType` (optional, string): Filter by file type.
    *   `currentStatus` (optional, string): Filter by current status.
    *   `agentInvolved` (optional, string): Filter by agent ID/name involved.
    *   `treatmentFolderId` (optional, string): Filter by specific treatment folder ID.
    *   `specificFileId` (optional, string): Filter by specific file ID.
    *   `page` (optional, integer): Current page number. Default: 1.
    *   `pageSize` (optional, integer): Number of items per page. Default: 10 or similar.
    *   `sortBy` (optional, string): Column to sort by (e.g., `folderId`, `fileName`, `currentOffice`, `lastActivity`).
    *   `sortDirection` (optional, string): Sort direction (`asc` or `desc`).
*   **Response:** `SearchResultsList`

### Get Transfer Trail Details
Retrieves the detailed transfer path and associated information for a given treatment folder.

*   **Endpoint:** `GET /api/search/transfer-trail/{folderId}`
*   **URL Parameters:**
    *   `folderId` (string): The ID of the treatment folder.
*   **Response:** `TransferTrail`

### Get Filter Options: Destination Units
Retrieves a list of available destination units for the advanced filter dropdown.

*   **Endpoint:** `GET /api/options/destination-units`
*   **Response:** `SelectOption[]`

### Get Filter Options: File Types
Retrieves a list of available file types for the advanced filter dropdown.

*   **Endpoint:** `GET /api/options/file-types`
*   **Response:** `SelectOption[]`

### Get Filter Options: Item Statuses
Retrieves a list of available item statuses for the advanced filter dropdown.

*   **Endpoint:** `GET /api/options/item-statuses`
*   **Response:** `SelectOption[]`

### Get Filter Options: Agents
Retrieves a list of available agents for the advanced filter dropdown.

*   **Endpoint:** `GET /api/options/agents`
*   **Response:** `SelectOption[]`
''' 