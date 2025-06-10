'''
# Notifications Management API Documentation

This document outlines the API endpoints required for the Notifications feature, encompassing personal notification settings, notification history, and system-wide notification rules. All data currently displayed in the frontend is mocked, necessitating new backend APIs for data retrieval and manipulation.

## Data Models

### NotificationPreference
Represents a user's preference for a specific type of notification.

```typescript
interface NotificationPreference {
  id: string; // Unique identifier for the preference type (e.g., "transfer_updates")
  title: string;
  description: string;
  isEnabled: boolean;
  // icon: string; // Backend might provide a string identifier for the icon
  // iconColorClass?: string; // CSS class for icon color
  // iconBgClass?: string; // CSS class for icon background color
}
```

### NotificationChannel
Represents a channel through which notifications can be sent.

```typescript
interface NotificationChannel {
  id: "in_app" | "email"; // Unique identifier for the channel
  label: string; // Display name (e.g., "In-App", "Email")
  isEnabled: boolean;
  // icon: string; // Backend might provide a string identifier for the icon
}
```

### DigestFrequency
Represents the frequency of email digests.

```typescript
type DigestFrequency = "daily" | "weekly" | "none";
```

### PersonalNotificationSettings
Represents a user's complete personal notification settings.

```typescript
interface PersonalNotificationSettings {
  preferences: NotificationPreference[];
  channels: NotificationChannel[];
  digestFrequency: DigestFrequency;
}
```

### NotificationHistoryItem
Represents a single entry in the user's notification history.

```typescript
interface NotificationHistoryItem {
  id: string;
  title: string;
  message: string;
  timestamp: string; // ISO 8601 string or similar format for sorting
  type: "system" | "transfer" | "escalation" | "agent" | "task";
  status: "read" | "unread";
  referenceId?: string; // Optional: ID of a related entity (e.g., folder ID, transfer ID)
  fileLink?: string; // Optional: Link to a related file/transfer page
  // icon: string; // Backend might provide a string identifier for the icon
  // iconColorClass: string; // CSS class for icon color
  // iconBgClass: string; // CSS class for icon background color
}
```

### NotificationHistoryFilters
Represents the filters applied to the notification history.

```typescript
interface NotificationHistoryFilters {
  dateRange: "last_7_days" | "last_30_days" | "last_90_days" | "custom";
  customStartDate?: string; // ISO 8601 date string
  customEndDate?: string;   // ISO 8601 date string
  notificationType: "all" | NotificationHistoryItemType;
  status: "all" | NotificationReadStatus;
  searchTerm: string;
}
```

### NotificationHistoryList
Represents a paginated list of notification history items.

```typescript
interface NotificationHistoryList {
  items: NotificationHistoryItem[];
  filters: NotificationHistoryFilters; // Reflects the applied filters
  currentPage: number;
  totalPages: number;
  totalItems: number;
}
```

### SystemNotificationRule
Represents a system-wide notification rule.

```typescript
interface SystemNotificationRule {
  id: string;
  name: string;
  triggerType: "file_inactive" | "agent_delay" | "file_rejected_returned" | "no_action_taken" | "weekly_digest" | string; // extensible
  recipients: ("file_sender" | "file_recipient" | "office_admin" | "agent_supervisor" | "office_heads" | "global_admin" | string)[]; // Array of recipient roles/types
  thresholdValue?: number; // e.g., 5 for 5 days
  thresholdUnit?: "minutes" | "hours" | "days" | "weeks" | "instant"; // e.g., "days"
  notificationChannels: ("in_app" | "email")[];
  messageTemplate?: string; // Optional: custom message template for the notification
  isEnabled: boolean;
  // icon: string; // Backend might provide a string identifier for the icon
  // iconColorClass: string; // CSS class for icon color
  // iconBgClass: string; // CSS class for icon background color
}
```

### SystemRulesList
Represents a list of system notification rules.

```typescript
interface SystemRulesList {
  rules: SystemNotificationRule[];
}
```

## API Endpoints

### Get Personal Notification Settings
Retrieves the current user's personal notification preferences and channel settings.

*   **Endpoint:** `GET /api/notifications/personal-settings`
*   **Response:** `PersonalNotificationSettings`

### Update Personal Notification Settings
Updates the current user's personal notification preferences and channel settings.

*   **Endpoint:** `PUT /api/notifications/personal-settings`
*   **Request Body:** `PersonalNotificationSettings`
*   **Response:** `PersonalNotificationSettings` (updated settings)

### Get Notification History
Retrieves a paginated and filterable list of notification history items for the current user.

*   **Endpoint:** `GET /api/notifications/history`
*   **Parameters:**
    *   `dateRange` (optional, string): Filter by date range (e.g., "last_7_days", "last_30_days", "custom").
    *   `customStartDate` (optional, date string): Required if `dateRange` is "custom".
    *   `customEndDate` (optional, date string): Required if `dateRange` is "custom".
    *   `notificationType` (optional, string): Filter by type (e.g., "transfer", "escalation"). Default: "all".
    *   `status` (optional, string): Filter by read status ("read", "unread"). Default: "all".
    *   `searchTerm` (optional, string): Search across title, message, or reference ID.
    *   `page` (optional, integer): Current page number for pagination. Default: 1.
    *   `pageSize` (optional, integer): Number of items per page. Default: 7 (inferred from UI).
*   **Response:** `NotificationHistoryList`

### Mark Notification as Read
Marks one or more notifications as read.

*   **Endpoint:** `POST /api/notifications/history/mark-read`
*   **Request Body:**
    ```json
    {
      "notificationIds": ["string"] // Array of notification IDs to mark as read
    }
    ```
*   **Response:** `204 No Content` or `{
  "message": "Notifications marked as read."
}`

### Get System Notification Rules
Retrieves a list of all system-wide notification rules.

*   **Endpoint:** `GET /api/notifications/rules`
*   **Response:** `SystemRulesList`

### Create System Notification Rule
Creates a new system-wide notification rule.

*   **Endpoint:** `POST /api/notifications/rules`
*   **Request Body:** `SystemNotificationRule` (without `id`)
*   **Response:** `SystemNotificationRule` (the created rule with its assigned ID)

### Update System Notification Rule
Updates an existing system-wide notification rule.

*   **Endpoint:** `PUT /api/notifications/rules/{id}` or `PATCH /api/notifications/rules/{id}` (PATCH for partial updates)
*   **URL Parameters:**
    *   `id` (string): The ID of the rule to update.
*   **Request Body:** `SystemNotificationRule` (full or partial, depending on PUT/PATCH)
*   **Response:** `SystemNotificationRule` (the updated rule)

### Delete System Notification Rule
Deletes a system-wide notification rule.

*   **Endpoint:** `DELETE /api/notifications/rules/{id}`
*   **URL Parameters:**
    *   `id` (string): The ID of the rule to delete.
*   **Response:** `204 No Content` or `{
  "message": "Rule deleted successfully."
}`

### Toggle System Notification Rule Status
Enables or disables a system-wide notification rule.

*   **Endpoint:** `PATCH /api/notifications/rules/{id}/toggle-status`
*   **URL Parameters:**
    *   `id` (string): The ID of the rule to toggle.
*   **Request Body:**
    ```json
    {
      "isEnabled": boolean
    }
    ```
*   **Response:** `SystemNotificationRule` (the updated rule with new status)
''' 