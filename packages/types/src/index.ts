// ============================================================================
// Core Entity Types for OneZone
// ============================================================================

// ----------------------------------------------------------------------------
// User & Authentication
// ----------------------------------------------------------------------------

export interface IUser {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  display_name?: string;
  avatar?: string;
  timezone: string;
  theme: {
    theme: string;
    palette: string;
    darkPalette: boolean;
  };
  is_active: boolean;
  is_bot: boolean;
  created_at: string;
  updated_at: string;
}

export interface IAuthSession {
  user: IUser;
  token?: string;
  expires_at?: string;
}

// ----------------------------------------------------------------------------
// Workspace & Access Control
// ----------------------------------------------------------------------------

export interface IWorkspace {
  id: string;
  name: string;
  slug: string;
  owner: string;
  logo?: string;
  total_members: number;
  total_projects: number;
  total_pages: number;
  created_at: string;
  updated_at: string;
}

export interface IWorkspaceMember {
  id: string;
  workspace: string;
  member: string;
  member_detail?: IUser;
  role: EUserRole;
  is_active: boolean;
  created_at: string;
}

export enum EUserRole {
  OWNER = 20,
  ADMIN = 15,
  MEMBER = 10,
  GUEST = 5,
}

// ----------------------------------------------------------------------------
// Project
// ----------------------------------------------------------------------------

export interface IProject {
  id: string;
  workspace: string;
  name: string;
  identifier: string;
  description: string;
  description_html: string;

  emoji?: string;
  icon_prop?: {
    name: string;
    color: string;
  };
  cover_image?: string;

  // Access control
  network: 0 | 1 | 2; // 0=private, 1=internal, 2=public

  // Metadata
  timezone: string;
  total_members: number;
  total_pages: number;

  // Feature toggle (simplified - only pages)
  page_view: boolean;

  // Soft delete
  archived_at?: string;

  created_at: string;
  updated_at: string;
  created_by: string;
}

export interface IProjectMember {
  id: string;
  project: string;
  member: string;
  member_detail?: IUser;
  role: EProjectRole;
  created_at: string;
}

export enum EProjectRole {
  ADMIN = 20,
  MEMBER = 10,
  VIEWER = 5,
}

// ----------------------------------------------------------------------------
// Page (Main Feature)
// ----------------------------------------------------------------------------

export interface IPage {
  id: string;
  workspace: string;
  project: string | null;
  parent: string | null;

  // Content
  name: string;
  description: string;
  description_html: string;
  description_stripped: string;

  // TipTap editor content
  content: Record<string, any>; // TipTap JSON
  content_html: string;

  // Metadata
  emoji?: string;
  icon_prop?: Record<string, any>;
  cover_image?: string;

  // Access control
  access: 0 | 1 | 2; // 0=private, 1=project, 2=workspace

  // Locking (for collaborative editing)
  is_locked: boolean;
  locked_by?: string;
  locked_by_detail?: IUser;
  locked_at?: string;

  // Organization
  is_favorite: boolean;
  sort_order: number;

  // Publishing
  is_published: boolean;
  published_at?: string;
  public_slug?: string;

  // Metrics
  view_count: number;
  comment_count: number;
  reaction_count: number;

  // Soft delete
  archived_at?: string;
  deleted_at?: string;

  created_at: string;
  updated_at: string;
  created_by: string;
  created_by_detail?: IUser;
  updated_by: string;
  updated_by_detail?: IUser;
}

// ----------------------------------------------------------------------------
// Page Version (Version History)
// ----------------------------------------------------------------------------

export interface IPageVersion {
  id: string;
  page: string;
  version_number: number;

  // Snapshot of content
  name: string;
  content: Record<string, any>;
  content_html: string;

  // Metadata
  change_summary?: string;
  created_at: string;
  created_by: string;
  created_by_detail?: IUser;
}

// ----------------------------------------------------------------------------
// Page Comment
// ----------------------------------------------------------------------------

export interface IPageComment {
  id: string;
  workspace: string;
  project: string | null;
  page: string;
  parent: string | null; // For threaded comments

  actor: string;
  actor_detail?: IUser;

  // Comment content (TipTap JSON for rich text)
  comment: Record<string, any>;
  comment_html: string;
  comment_stripped: string;

  created_at: string;
  updated_at: string;
}

// ----------------------------------------------------------------------------
// Page Reaction
// ----------------------------------------------------------------------------

export interface IPageReaction {
  id: string;
  workspace: string;
  page: string;
  comment: string | null; // null = reaction on page, otherwise on comment

  actor: string;
  actor_detail?: IUser;

  reaction: string; // Emoji

  created_at: string;
}

// ----------------------------------------------------------------------------
// Pagination & API Responses
// ----------------------------------------------------------------------------

export interface IPaginatedResponse<T> {
  results: T[];
  next_cursor?: string;
  prev_cursor?: string;
  total_results: number;
  total_pages: number;
}

export interface IAPIError {
  error: string;
  detail?: string;
  field_errors?: Record<string, string[]>;
}

// ----------------------------------------------------------------------------
// Search
// ----------------------------------------------------------------------------

export interface ISearchResult {
  id: string;
  type: "page" | "project" | "user";
  title: string;
  description: string;
  url: string;
  highlights?: string[];
  relevance_score: number;
}

// ----------------------------------------------------------------------------
// Real-Time Collaboration
// ----------------------------------------------------------------------------

export interface IPresence {
  user_id: string;
  user: IUser;
  cursor_position?: number;
  selection?: {
    from: number;
    to: number;
  };
  last_active: string;
}

export interface ICollaborationSession {
  page_id: string;
  active_users: IPresence[];
  locked: boolean;
  locked_by?: string;
}

// ----------------------------------------------------------------------------
// File Upload
// ----------------------------------------------------------------------------

export interface IFileUpload {
  id: string;
  workspace: string;
  uploaded_by: string;

  file_name: string;
  file_size: number;
  file_type: string;
  file_url: string;

  // For images
  thumbnail_url?: string;
  width?: number;
  height?: number;

  created_at: string;
}

// ----------------------------------------------------------------------------
// Activity & Audit
// ----------------------------------------------------------------------------

export interface IPageActivity {
  id: string;
  workspace: string;
  project: string | null;
  page: string;
  actor: string;
  actor_detail?: IUser;

  verb: "created" | "updated" | "deleted" | "published" | "archived" | "commented";
  field?: string;
  old_value?: string;
  new_value?: string;
  comment?: string;

  created_at: string;
}

// ----------------------------------------------------------------------------
// Settings & Preferences
// ----------------------------------------------------------------------------

export interface IUserPreferences {
  theme: "light" | "dark" | "system";
  editor_mode: "default" | "zen" | "focus";
  auto_save_interval: number; // milliseconds
  show_line_numbers: boolean;
  spell_check: boolean;
}

export interface IWorkspaceSettings {
  allow_guest_invites: boolean;
  default_page_access: 0 | 1 | 2;
  enable_public_pages: boolean;
  require_approval_for_publishing: boolean;
}
