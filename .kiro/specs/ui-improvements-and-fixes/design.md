# Design Document

## Overview

This design addresses six key UI improvements and fixes for the EduNexa LMS: notification system verification, profile page simplification, AI assistant markdown rendering, sidebar improvements, footer component addition, and duplicate notification icon resolution. The design focuses on creating a cleaner, more intuitive user experience while maintaining functionality.

## Architecture

### Component Structure

```
src/
├── components/
│   ├── layout/
│   │   ├── Header.tsx (modified - fix duplicate notifications)
│   │   ├── Footer.tsx (new - add footer component)
│   │   ├── Layout.tsx (modified - integrate footer)
│   │   ├── StudentSidebar.tsx (modified - improve organization)
│   │   ├── TeacherSidebar.tsx (modified - improve organization)
│   │   └── SuperAdminSidebar.tsx (modified - improve organization)
│   ├── profile/
│   │   └── ProfilePage.tsx (modified - simplify)
│   ├── ai/
│   │   └── AIAssistant.tsx (modified - fix markdown)
│   ├── notifications/
│   │   ├── NotificationsPage.tsx (verify functionality)
│   │   └── LearnerAlerts.tsx (verify positioning)
│   └── common/
│       └── MarkdownRenderer.tsx (verify/enhance)
```

## Components and Interfaces

### 1. Header Component Modifications

**Current Issue**: Two bell icons appear for teachers/admins - one from notifications and one from LearnerAlerts

**Design Solution**:
- Keep the standard notification bell icon in the header for all roles
- Position LearnerAlerts component separately with distinct styling
- Use different colors: blue for notifications, red/orange for learner alerts
- Ensure proper spacing between the two components

**Visual Layout**:
```
[Search] ... [LearnerAlerts] [Notifications] [Messages] [UserMenu]
```

### 2. Footer Component Design

**New Component**: `src/components/layout/Footer.tsx`

**Structure**:
```typescript
interface FooterProps {
  className?: string;
}

const Footer: React.FC<FooterProps> = ({ className }) => {
  // Footer content
}
```

**Layout**:
```
┌─────────────────────────────────────────────────────────┐
│  EduNexa © 2024                                         │
│  Help • Privacy Policy • Terms of Service               │
│  Version 1.0.0                                          │
└─────────────────────────────────────────────────────────┘
```

**Styling**:
- Background: Light gray (bg-gray-100)
- Text: Gray-600 for normal text, blue-600 for links
- Padding: py-6 px-4
- Border-top: 1px solid gray-200
- Responsive: Stack vertically on mobile

### 3. Profile Page Simplification

**Remove**:
- Mock achievements section
- Mock activity section
- Mock learning statistics (courses completed, study hours, etc.)
- Social media links (website, LinkedIn, GitHub)
- Bio field (not essential)
- Location field (not essential)

**Keep**:
- Profile picture upload/management
- Name (editable)
- Email (read-only)
- Phone (editable)
- Role-specific fields:
  - Students: Roll number (read-only), Department, Year, Semester
  - Teachers: Employee ID (read-only), Department, Designation
  - Super_Admin: Employee ID (read-only), Department, Designation
- Security section (simplified):
  - Password change button
  - Last password change date

**New Layout**:
```
┌─────────────────────────────────────────────────────────┐
│  [Profile Header with Picture]                          │
│  ┌───────────────────────────────────────────────────┐  │
│  │ Personal Information                              │  │
│  │ - Name, Email, Phone                              │  │
│  │ - Role-specific fields                            │  │
│  └───────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────┐  │
│  │ Security                                          │  │
│  │ - Password management                             │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### 4. AI Assistant Markdown Rendering

**Current Issue**: Markdown is not rendering properly with headings, bullets, etc.

**Design Solution**:
- Enhance the MarkdownRenderer component or use a library like `react-markdown`
- Apply proper CSS classes for markdown elements
- Ensure consistent spacing and typography

**Markdown Styling**:
```css
h1: text-2xl font-bold mb-4 mt-6
h2: text-xl font-bold mb-3 mt-5
h3: text-lg font-semibold mb-2 mt-4
p: mb-3 leading-relaxed
ul/ol: mb-3 ml-6 space-y-1
li: list-disc (ul) or list-decimal (ol)
code: bg-gray-100 px-2 py-1 rounded text-sm font-mono
pre: bg-gray-900 text-white p-4 rounded-lg overflow-x-auto
strong: font-semibold
em: italic
a: text-blue-600 hover:underline
```

### 5. Sidebar Improvements

**Current Issues**:
- Too many items without clear grouping
- Inconsistent spacing
- Unclear active state
- Complicated on mobile

**Design Solution**:

**Student Sidebar Sections**:
1. Core Learning (no divider above)
   - Dashboard
   - My Courses
   - Assignments
2. Learning Tools (divider)
   - My Progress
   - AI Assistant
   - Schedule
   - Achievements
3. Personal (divider)
   - Notifications
   - Profile
   - Settings

**Teacher Sidebar Sections**:
1. Core Teaching (no divider above)
   - Dashboard
   - My Courses
   - Create Course
   - Video Management
2. Student Management (divider)
   - Assignments
   - My Students
   - Analytics
3. Tools & Settings (divider)
   - AI Assistant
   - Notifications
   - Profile
   - Settings

**Spacing**:
- Between items in same section: 8px (space-y-2)
- Between sections: 16px (my-4) with 1px divider line
- Padding around items: px-3 py-3

**Active State**:
- Background: role-specific color at 50 opacity (blue-50 for students, green-50 for teachers)
- Text: role-specific color at 600 (blue-600, green-600)
- Border-left: 3px solid role color (optional enhancement)

**Mobile Behavior**:
- Full overlay when open
- Slide in from left
- Close on navigation
- Close on overlay click

### 6. Notification System Verification

**Design Approach**:
- Audit all notification-related components
- Ensure proper API integration
- Verify unread count updates
- Test notification marking as read
- Ensure proper routing to notification details

**Components to Verify**:
1. Header.tsx - notification bell
2. NotificationsPage.tsx - notification list
3. LearnerAlerts.tsx - teacher/admin alerts
4. API integration in config/api.ts

## Data Models

### Footer Configuration
```typescript
interface FooterConfig {
  systemName: string;
  version: string;
  links: {
    label: string;
    href: string;
  }[];
}
```

### Profile Form Data
```typescript
interface ProfileFormData {
  name: string;
  email: string; // read-only
  phone: string;
  profile_pic: string;
  // Role-specific fields
  department?: string;
  year?: string;
  semester?: string;
  roll_number?: string; // read-only
  designation?: string;
  employee_id?: string; // read-only
}
```

### Sidebar Navigation Item
```typescript
interface SidebarItem {
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  href: string;
  badge?: number;
}

interface SidebarSection {
  items: SidebarItem[];
}
```

## Error Handling

### Profile Update Errors
- Display inline error messages for validation failures
- Show toast notification for API errors
- Prevent form submission if validation fails
- Revert to previous values on cancel

### Notification Errors
- Gracefully handle API failures with fallback UI
- Show "Unable to load notifications" message
- Provide retry button
- Log errors to console for debugging

### Markdown Rendering Errors
- Fallback to plain text if markdown parsing fails
- Sanitize user input to prevent XSS
- Handle malformed markdown gracefully

## Testing Strategy

### Unit Tests
- Test MarkdownRenderer with various markdown inputs
- Test Footer component rendering
- Test ProfilePage form validation
- Test Sidebar navigation item rendering

### Integration Tests
- Test notification count updates across components
- Test profile update flow end-to-end
- Test sidebar navigation and routing
- Test AI assistant markdown rendering with API responses

### Visual Regression Tests
- Capture screenshots of sidebar in collapsed/expanded states
- Capture screenshots of profile page before/after simplification
- Capture screenshots of AI assistant with markdown responses
- Capture screenshots of footer on different screen sizes

### Manual Testing Checklist
1. Verify single notification icon for all roles
2. Verify LearnerAlerts positioning for teachers/admins
3. Test profile page editing and saving
4. Test AI assistant markdown rendering
5. Test sidebar navigation on desktop and mobile
6. Verify footer appears on all pages
7. Test notification marking as read
8. Test responsive behavior on various screen sizes

## Implementation Notes

### Dependencies
- Consider using `react-markdown` library for robust markdown rendering
- Use `remark-gfm` for GitHub Flavored Markdown support
- Use `rehype-sanitize` for XSS protection

### Performance Considerations
- Lazy load notification data
- Debounce profile form validation
- Optimize sidebar re-renders with React.memo
- Cache markdown rendering results

### Accessibility
- Ensure footer links are keyboard navigable
- Add ARIA labels to notification icons
- Ensure proper heading hierarchy in markdown
- Maintain focus management in sidebar navigation
- Ensure sufficient color contrast for all text

### Browser Compatibility
- Test on Chrome, Firefox, Safari, Edge
- Ensure CSS Grid/Flexbox fallbacks
- Test responsive behavior on iOS and Android
- Verify markdown rendering across browsers
