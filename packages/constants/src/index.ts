// ============================================================================
// Constants for OneZone v2
// ============================================================================

// API Configuration
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// API Endpoints
export const ENDPOINTS = {
  // Authentication
  AUTH_LOGIN: "/api/v1/auth/login/",
  AUTH_LOGOUT: "/api/v1/auth/logout/",
  AUTH_SESSION: "/api/v1/auth/session/",
  AUTH_ME: "/api/v1/auth/me/",

  // Workspaces
  WORKSPACES: "/api/v1/workspaces/",
  WORKSPACE_DETAIL: (slug: string) => `/api/v1/workspaces/${slug}/`,
  WORKSPACE_MEMBERS: (slug: string) => `/api/v1/workspaces/${slug}/members/`,

  // Projects
  PROJECTS: (workspaceSlug: string) => `/api/v1/workspaces/${workspaceSlug}/projects/`,
  PROJECT_DETAIL: (workspaceSlug: string, projectId: string) =>
    `/api/v1/workspaces/${workspaceSlug}/projects/${projectId}/`,
  PROJECT_MEMBERS: (workspaceSlug: string, projectId: string) =>
    `/api/v1/workspaces/${workspaceSlug}/projects/${projectId}/members/`,

  // Pages (Main Feature)
  PAGES: (workspaceSlug: string, projectId?: string) => {
    if (projectId) {
      return `/api/v1/workspaces/${workspaceSlug}/projects/${projectId}/pages/`;
    }
    return `/api/v1/workspaces/${workspaceSlug}/pages/`;
  },
  PAGE_DETAIL: (workspaceSlug: string, pageId: string) =>
    `/api/v1/workspaces/${workspaceSlug}/pages/${pageId}/`,
  PAGE_VERSIONS: (workspaceSlug: string, pageId: string) =>
    `/api/v1/workspaces/${workspaceSlug}/pages/${pageId}/versions/`,
  PAGE_COMMENTS: (workspaceSlug: string, pageId: string) =>
    `/api/v1/workspaces/${workspaceSlug}/pages/${pageId}/comments/`,
  PAGE_REACTIONS: (workspaceSlug: string, pageId: string) =>
    `/api/v1/workspaces/${workspaceSlug}/pages/${pageId}/reactions/`,
  PAGE_PUBLISH: (workspaceSlug: string, pageId: string) =>
    `/api/v1/workspaces/${workspaceSlug}/pages/${pageId}/publish/`,
  PAGE_LOCK: (workspaceSlug: string, pageId: string) =>
    `/api/v1/workspaces/${workspaceSlug}/pages/${pageId}/lock/`,

  // Search
  SEARCH: "/api/v1/search/",
  SEARCH_PAGES: "/api/v1/search/pages/",

  // File uploads
  FILE_UPLOAD: "/api/v1/files/upload/",

  // Activity
  PAGE_ACTIVITY: (workspaceSlug: string, pageId: string) =>
    `/api/v1/workspaces/${workspaceSlug}/pages/${pageId}/activity/`,
};

// User Roles
export const USER_ROLES = {
  OWNER: 20,
  ADMIN: 15,
  MEMBER: 10,
  GUEST: 5,
} as const;

export const ROLE_LABELS = {
  [USER_ROLES.OWNER]: "Owner",
  [USER_ROLES.ADMIN]: "Admin",
  [USER_ROLES.MEMBER]: "Member",
  [USER_ROLES.GUEST]: "Guest",
};

// Page Access Levels
export const PAGE_ACCESS = {
  PRIVATE: 0,
  PROJECT: 1,
  WORKSPACE: 2,
} as const;

export const PAGE_ACCESS_LABELS = {
  [PAGE_ACCESS.PRIVATE]: "Private",
  [PAGE_ACCESS.PROJECT]: "Project",
  [PAGE_ACCESS.WORKSPACE]: "Workspace",
};

// File Upload
export const FILE_SIZE_LIMIT = 10 * 1024 * 1024; // 10MB
export const ALLOWED_FILE_TYPES = [
  "image/jpeg",
  "image/jpg",
  "image/png",
  "image/gif",
  "image/webp",
  "application/pdf",
  "text/plain",
  "text/markdown",
];

export const ALLOWED_IMAGE_TYPES = [
  "image/jpeg",
  "image/jpg",
  "image/png",
  "image/gif",
  "image/webp",
];

// Pagination
export const DEFAULT_PAGE_SIZE = 25;
export const MAX_PAGE_SIZE = 100;

// Editor Configuration
export const AUTO_SAVE_INTERVAL = 3000; // 3 seconds
export const DEBOUNCE_DELAY = 500; // 500ms

// WebSocket Events
export const WS_EVENTS = {
  CONNECT: "connect",
  DISCONNECT: "disconnect",
  JOIN_PAGE: "join_page",
  LEAVE_PAGE: "leave_page",
  PAGE_UPDATE: "page_update",
  USER_PRESENCE: "user_presence",
  CURSOR_UPDATE: "cursor_update",
  LOCK_PAGE: "lock_page",
  UNLOCK_PAGE: "unlock_page",
  NEW_COMMENT: "new_comment",
} as const;

// Theme
export const THEME = {
  LIGHT: "light",
  DARK: "dark",
  SYSTEM: "system",
} as const;

// Keyboard Shortcuts
export const SHORTCUTS = {
  CREATE_PAGE: "c",
  SEARCH: "k", // Cmd/Ctrl + K
  SAVE: "s", // Cmd/Ctrl + S
  TOGGLE_SIDEBAR: "\\",
  FOCUS_MODE: "f",
} as const;

// Rate Limiting
export const RATE_LIMITS = {
  API_KEY_RATE_LIMIT: 60, // requests per minute
  SEARCH_RATE_LIMIT: 20,
  UPLOAD_RATE_LIMIT: 10,
} as const;
