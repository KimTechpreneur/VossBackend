'''
# Dashboard Management API Documentation

This document outlines the API endpoints required for the Dashboard feature, which provides an overview of key system metrics, recent activities, alerts, and performance charts. All data currently displayed in the frontend is mocked, necessitating new backend APIs for data retrieval.

## Data Models

### Dashboard Summary Metrics
Represents key performance indicators displayed as stats cards on the dashboard.

```typescript
interface DashboardMetrics {
  totalActiveTransfers: number;
  pendingApprovals: number; // Could be KYC requests, staff requests, etc.
  overdueTransfers: number;
  agentPerformance: string; // e.g., "28 min" Avg. delivery time today
}
```

### NotificationItem
Represents a single alert or notification displayed in the Alerts & Notifications panel.

```typescript
interface NotificationItem {
  id: string;
  type: "warning" | "error" | "info";
  title: string;
  message: string;
  timestamp: string; // e.g., "Today, 10:24 AM"
  // icon: string; // Icon name or URL, determined by backend
}
```

### ActivityItem
Represents a single recent activity displayed in the Recent Activity feed.

```typescript
interface ActivityItem {
  id: string;
  type: "folder_created" | "transfer_initiated" | "staff_approval" | "delivery_confirmation";
  title: string;
  description: string;
  timestamp: string; // e.g., "Today, 11:32 AM"
  // icon: string; // Icon name or URL, determined by backend
}
```

### OverdueUnit
Represents a unit or department with overdue items, displayed in the "Top 5 Overdue Units" table.

```typescript
interface OverdueUnit {
  id: string;
  name: string; // Name of the unit/department
  overdueCount: number;
  avgDays: number; // Average days overdue
}
```

### AuditItem
Represents a single entry in the audit snapshot, displaying recent system actions.

```typescript
interface AuditItem {
  id: string;
  userName: string;
  action: string;
  timestamp: string; // e.g., "11:45 AM" or "Yesterday"
}
```

### HealthMetric
Represents a single system health metric.

```typescript
interface HealthMetric {
  id: string;
  title: string;
  value: string; // e.g., "99.98%"
  percentage: number;
  color: "green" | "yellow" | "red"; // Indicates health status for UI display
}
```

### TransferVolumeData
Represents data for the "Transfer Volume by Unit" bar chart.

```typescript
interface TransferVolumeData {
  labels: string[]; // e.g., ["Finance", "Admissions", ...]
  datasets: [
    {
      label: "Transfers Sent";
      data: number[];
      backgroundColor: string; // CSS color string
      borderColor: string;
      borderWidth: number;
      hoverBackgroundColor: string;
    },
    {
      label: "Transfers Received";
      data: number[];
      backgroundColor: string;
      borderColor: string;
      borderWidth: number;
      hoverBackgroundColor: string;
    }
  ];
}
```

### ProcessingTimeData
Represents data for the "Average Processing Time" line chart.

```typescript
interface ProcessingTimeData {
  labels: string[]; // e.g., ["Mon", "Tue", ...]
  datasets: [
    {
      label: "Average Processing Time";
      data: number[]; // In days, e.g., [2.1, 1.8, ...]
      backgroundColor: string; // CSS color string (for fill)
      borderColor: string;
      borderWidth: number;
      tension: number; // For line curvature
      fill: boolean;
      pointBackgroundColor: string;
      pointBorderColor: string;
      pointHoverBorderColor: string;
      pointRadius: number;
      pointHoverRadius: number;
    }
  ];
}
```

### AgentSuccessData
Represents data for the "Agent Delivery Success Rate" doughnut chart.

```typescript
interface AgentSuccessData {
  labels: string[]; // e.g., ["On-Time Delivery", "Delayed", "Failed"]
  datasets: [
    {
      data: number[]; // Percentages, e.g., [85, 12, 3]
      backgroundColor: string[]; // Array of CSS color strings
      borderWidth: number;
      hoverBackgroundColor: string[];
      hoverOffset: number;
    }
  ];
}
```

## API Endpoints

### Get Dashboard Summary Metrics
Retrieves key performance indicators for the dashboard.

*   **Endpoint:** `GET /api/dashboard/metrics`
*   **Response:** `DashboardMetrics`

### Get Recent Alerts and Notifications
Retrieves a limited number of recent alerts and notifications for display on the dashboard. A separate, more comprehensive endpoint would be needed for a full "View All" notifications page.

*   **Endpoint:** `GET /api/dashboard/alerts`
*   **Parameters:**
    *   `limit` (optional, integer): Maximum number of alerts to return. Default: 3 (inferred from UI)
*   **Response:** `NotificationItem[]`

### Get Recent Activity Feed
Retrieves a limited list of recent system activities for the dashboard. A separate, more comprehensive endpoint would be needed for a full "View All" activity log.

*   **Endpoint:** `GET /api/dashboard/activity`
*   **Parameters:**
    *   `limit` (optional, integer): Maximum number of activities to return. Default: 4 (inferred from UI)
*   **Response:** `ActivityItem[]`

### Get Top Overdue Units
Retrieves a list of units with the most overdue items, typically limited to the top N.

*   **Endpoint:** `GET /api/dashboard/overdue-units`
*   **Parameters:**
    *   `limit` (optional, integer): Maximum number of units to return. Default: 5 (inferred from UI)
*   **Response:** `OverdueUnit[]`

### Get Audit Snapshot
Retrieves a limited set of the most recent audit trail entries for the dashboard. A separate, more comprehensive endpoint would be needed for a full "View Audit Log" page.

*   **Endpoint:** `GET /api/dashboard/audit-snapshot`
*   **Parameters:**
    *   `limit` (optional, integer): Maximum number of audit items to return. Default: 5 (inferred from UI)
*   **Response:** `AuditItem[]`

### Get System Health Metrics
Retrieves current system health indicators.

*   **Endpoint:** `GET /api/dashboard/system-health`
*   **Response:** `HealthMetric[]`

### Get Transfer Volume Chart Data
Retrieves data necessary to render the "Transfer Volume by Unit" bar chart.

*   **Endpoint:** `GET /api/dashboard/charts/transfer-volume`
*   **Parameters:**
    *   `timeframe` (optional, string): e.g., "last_7_days", "last_30_days", "current_month", "last_month", "custom_range". Default: "current_month" (example)
    *   `start_date` (optional, date): Required if `timeframe` is "custom_range".
    *   `end_date` (optional, date): Required if `timeframe` is "custom_range".
*   **Response:** `TransferVolumeData`

### Get Average Processing Time Chart Data
Retrieves data necessary to render the "Average Processing Time" line chart.

*   **Endpoint:** `GET /api/dashboard/charts/processing-time`
*   **Parameters:**
    *   `timeframe` (optional, string): e.g., "last_7_days", "last_30_days", "current_month", "last_month", "custom_range". Default: "last_7_days" (example)
    *   `start_date` (optional, date): Required if `timeframe` is "custom_range".
    *   `end_date` (optional, date): Required if `timeframe` is "custom_range".
*   **Response:** `ProcessingTimeData`

### Get Agent Delivery Success Rate Chart Data
Retrieves data necessary to render the "Agent Delivery Success Rate" doughnut chart.

*   **Endpoint:** `GET /api/dashboard/charts/agent-success`
*   **Parameters:**
    *   `timeframe` (optional, string): e.g., "last_30_days", "current_month", "custom_range". Default: "last_30_days" (example)
    *   `start_date` (optional, date): Required if `timeframe` is "custom_range".
    *   `end_date` (optional, date): Required if `timeframe` is "custom_range".
*   **Response:** `AgentSuccessData`

## Quick Actions (No direct API, these are navigation points)
The quick actions section on the dashboard provides direct links to create new folders, initiate transfers, add users/agents, and add units/offices. These do not require dedicated dashboard API endpoints but rather leverage the existing APIs for their respective features (Folders, Transfers, Users, Offices). For example:

*   **Create New Treatment Folder:** Navigates to `/folders/create` (uses `POST /api/folders`).
*   **Initiate Transfer:** Navigates to `/transfers/create` (uses `POST /api/transfers`).
*   **Add New User / Agent:** Navigates to `/users/create` (uses `POST /api/users` or `POST /api/agents`).
*   **Add New Unit / Office:** Navigates to `/offices/create` (uses `POST /api/offices` or `POST /api/units`).
''' 