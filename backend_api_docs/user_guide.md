'''
# User Guide API Documentation

This document outlines the API endpoints required for the User Guide feature, which provides categorized help topics and links to external resources. All data currently displayed in the frontend is mocked, necessitating new backend APIs for data retrieval.

## Data Models

### GuideCategory
Represents a category of help topics or guides.

```typescript
interface GuideCategory {
  id: string;
  title: string;
  description: string;
  // icon: string; // Backend might provide a string identifier for the icon
  // iconColorClass?: string; // CSS class for icon color
  // iconBgClass?: string; // CSS class for icon background color
  link?: string; // Optional: internal path to the detailed guide page for this category
}
```

### ExternalLink
Represents a link to an external resource.

```typescript
interface ExternalLink {
  id: string;
  label: string;
  url: string;
  description?: string; // Optional description of the link
  // icon?: string; // Backend might provide a string identifier for the icon
}
```

## API Endpoints

### Get Guide Categories
Retrieves a list of categorized help topics/guides to display on the User Guide page.

*   **Endpoint:** `GET /api/user-guide/categories`
*   **Response:** `GuideCategory[]`

### Get External Resources
Retrieves a list of external resource links to display on the User Guide page.

*   **Endpoint:** `GET /api/user-guide/external-resources`
*   **Response:** `ExternalLink[]`
''' 