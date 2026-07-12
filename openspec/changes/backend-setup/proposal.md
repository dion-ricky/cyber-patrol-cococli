## Why

Cyber-patrol needs a backend infrastructure to power its core functionality: scanning the internet for malicious sites (online gambling, scams, illegal lending/BNPL). The backend will support a ChatGPT-like interface where users can chat and request site scans, with full evidence capture (images/videos) stored in blob storage.

## What Changes

- Set up Supabase backend with PostgreSQL database and blob storage
- Implement user management (authentication, profiles)
- Create chat session and message management system
- Build site scanning pipeline as Supabase Edge Function with result storage
- Add blob storage for scan evidence (screenshots, recordings)
- Support image/file uploads in chat messages

## Capabilities

### New Capabilities
- `user-management`: User authentication, profiles, and session handling
- `chat-system`: Chat sessions, message management, and real-time capabilities
- `site-scanning`: Malicious site detection, scan scheduling, and result storage
- `evidence-storage`: Blob storage for images, videos, and files captured during scans
- `file-uploads`: Image and file upload handling in chat messages

### Modified Capabilities

## Impact

- New Supabase project configuration (database, auth, storage)
- Backend API endpoints for all capabilities
- Database schema for users, chats, messages, scans, evidence
- Storage buckets for scan evidence and user uploads
- Integration with existing frontend (ChatGPT-like interface)
