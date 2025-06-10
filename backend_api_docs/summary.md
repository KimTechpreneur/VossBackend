'''
# Backend API Documentation Summary for VOSS Frontend Application

This document provides a consolidated summary of the backend API documentation generated for the VOSS frontend application. The goal was to infer API requirements based on existing frontend implementations (pages, components, hooks, and types files), specifically for a Django backend integration. All identified frontend implementations use mock data, thus new backend APIs are necessary.

## Documented Features (with inferred API Endpoints and Data Models)

1.  **Roles Management:**
    *   **Document:** `backend_api_docs/roles_management.md`
    *   **Key Data Models:** `Permission`, `Role`, `RoleFormData`, `RoleFilters`.
    *   **API Endpoints:** GET all roles (with filters/pagination), GET single role by ID, POST create new role, PATCH update existing role, DELETE role.

2.  **Users Management:**
    *   **Document:** `backend_api_docs/users_management.md`
    *   **Key Data Models:** `UserRole`, `UserStatus`, `UserDepartment`, `PasswordSetupMethod`, `User`, `UserFilters`, `AddUserFormData`, `UserUpdateFormData`.
    *   **API Endpoints:** GET all users (with search/filters/pagination), GET single user by ID, POST create new user, PATCH update existing user, DELETE user, POST bulk deactivate users, POST bulk send password reset, PATCH bulk change role, PATCH toggle user status.

3.  **Offices Management:**
    *   **Document:** `backend_api_docs/offices_management.md`
    *   **Key Data Models:** `InternalOfficeStatus`, `InternalOfficeType`, `InternalOffice`, `AddInternalOfficeFormData`, `InternalOfficeFilters`, `OfficeStaffMember`, `OfficeFolderItem`, `OfficeTransferItem`, `InternalOfficeDetailed`.
    *   **API Endpoints:** GET all internal offices (with search/filters/pagination), GET single internal office by ID (detailed), POST create new internal office, PATCH update existing internal office, DELETE internal office, POST/PATCH bulk update office status, POST/DELETE bulk delete offices.

4.  **Agents Management:**
    *   **Document:** `backend_api_docs/agents_management.md`
    *   **Key Data Models:** `AgentStatus`, `BaseOffice`, `EmploymentType`, `Agent`, `AgentFilters`, `AgentDelivery`, `AgentFormData`.
    *   **API Endpoints:** GET all agents (with search/filters/pagination), GET single agent by ID, POST create new agent, PATCH update existing agent, DELETE agent, POST bulk deactivate agents, GET export agents data, GET agent deliveries.

5.  **Folders Management:**
    *   **Document:** `backend_api_docs/folders_management.md`
    *   **Key Data Models:** `FolderTransferStatus`, `FolderService`, `FolderPriority`, `Folder`, `FolderFilters`, `FolderFile`, `NewFolderData`, `FolderMetadata`.
    *   **API Endpoints:** GET all folders (with search/filters/pagination), GET single folder by ID (detailed with files), POST create new folder, PATCH update existing folder metadata, DELETE folder, POST add file(s) to folder, DELETE remove file from folder, GET download file from folder, POST bulk archive folders, POST/PATCH bulk assign folders to unit/location, POST/DELETE bulk delete folders.

6.  **Transfers Management:**
    *   **Document:** `backend_api_docs/transfers_management.md`
    *   **Key Data Models:** `FolderCategory`, `RetentionClass`, `TransferFolder`, `AttachedFile`, `RoutingStep`, `Transfer` (core model), `CreateTransferRequest`, `TransferFilters` (base and specific types for each page).
    *   **API Endpoints:** POST create new transfer, GET all active transfers, GET all overdue transfers, GET all completed transfers, GET all draft transfers, GET all returned transfers, GET transfer history, GET single transfer by ID (detailed), POST/PATCH save/update draft transfer, POST submit draft transfer, DELETE draft transfer, POST recall active transfer, POST escalate overdue transfer, PATCH reassign agent for transfer, POST force return overdue transfer, POST approve returned transfer, POST reject returned transfer, POST request revision for returned transfer, and various bulk actions (recall, escalate, reassign agent, archive, export, delete draft, submit draft).

7.  **Dashboard:**
    *   **Document:** `backend_api_docs/dashboard_management.md`
    *   **Key Data Models:** `DashboardMetrics`, `NotificationItem`, `ActivityItem`, `OverdueUnit`, `AuditItem`, `HealthMetric`, `TransferVolumeData`, `ProcessingTimeData`, `AgentSuccessData`.
    *   **API Endpoints:** GET dashboard summary metrics, GET recent alerts and notifications, GET recent activity feed, GET top overdue units, GET audit snapshot, GET system health metrics, GET transfer volume chart data, GET average processing time chart data, GET agent delivery success rate chart data.

8.  **Notifications Management:**
    *   **Document:** `backend_api_docs/notifications_management.md`
    *   **Key Data Models:** `NotificationPreference`, `NotificationChannel`, `DigestFrequency`, `PersonalNotificationSettings`, `NotificationHistoryItem`, `NotificationHistoryFilters`, `NotificationHistoryList`, `SystemNotificationRule`, `SystemRulesList`.
    *   **API Endpoints:** GET personal notification settings, PUT/PATCH update personal notification settings, GET notification history (paginated/filterable), POST mark notification as read, GET system notification rules, POST create system notification rule, PUT/PATCH update system notification rule, DELETE system notification rule, PATCH toggle system notification rule status.

9.  **Search and Tracking:**
    *   **Document:** `backend_api_docs/search_tracking.md`
    *   **Key Data Models:** `SearchResultItem`, `SearchFilters`, `SearchResultsList`, `FileInTrail`, `TransferPathStep`, `AgentActivity`, `TransferTrail`, `SelectOption`.
    *   **API Endpoints:** GET search files and folders (paginated/filterable/sortable), GET transfer trail details by folder ID, GET filter options for destination units, file types, item statuses, and agents.

10. **Units Management:**
    *   **Document:** `backend_api_docs/units_management.md`
    *   **Key Data Models:** `UnitStatus`, `UnitType`, `Unit`, `UnitFilters`, `UnitList`, `SelectOption`.
    *   **API Endpoints:** GET all units (paginated/filterable/sortable), GET single unit by ID, POST create new unit, PUT/PATCH update existing unit, DELETE unit, PATCH toggle unit status, GET head of unit options, GET unit type options, GET unit status options.

11. **User Guide:**
    *   **Document:** `backend_api_docs/user_guide.md`
    *   **Key Data Models:** `GuideCategory`, `ExternalLink`.
    *   **API Endpoints:** GET guide categories, GET external resources.

## Features with No Frontend Implementation (No API Inferred)

*   **Permissions:** The `src/features/permissions` directory was empty, indicating no direct frontend components from which to infer API requirements.
*   **Reports:** The `src/features/reports` directory was empty, indicating no direct frontend components from which to infer API requirements.
*   **Settings:** The `src/features/settings` directory was empty, indicating no direct frontend components from which to infer API requirements.

For these features, API documentation would need to be based on business requirements or existing backend definitions, rather than inferred from the current frontend codebase.
''' 