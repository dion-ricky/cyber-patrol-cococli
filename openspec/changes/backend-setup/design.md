## Context

Cyber-patrol is a web application that scans the internet for malicious sites (online gambling, scams, illegal lending/BNPL). The current frontend needs a backend to power its ChatGPT-like interface where users can chat and request site scans. The backend will be built on Supabase, providing PostgreSQL database, authentication, and blob storage.

## Goals / Non-Goals

**Goals:**
- Set up Supabase backend with all required infrastructure
- Implement user management with Supabase Auth
- Create chat system for user interactions
- Build site scanning pipeline with evidence capture
- Support file uploads in chat messages
- Store scan evidence (images/videos) in Supabase Storage

**Non-Goals:**
- Frontend implementation (already exists)
- Third-party API integrations beyond Supabase
- Advanced ML/AI for site classification (future enhancement)
- Mobile app backend (web only for now)

## Decisions

### Decision: Use Supabase as backend platform
**Choice**: Supabase (PostgreSQL + Auth + Storage + Realtime)
**Alternatives considered**: Firebase, AWS Amplify, custom backend
**Rationale**: Supabase provides all required features (database, auth, storage, realtime) with a single platform. PostgreSQL gives us powerful querying for scan results. Open source and vendor-lock-in is lower than Firebase.

### Decision: Chat system architecture
**Choice**: Store chat sessions and messages in PostgreSQL with realtime updates
**Alternatives considered**: WebSocket-only, third-party chat service
**Rationale**: PostgreSQL gives us ACID compliance for message ordering. Supabase Realtime enables live updates without custom WebSocket server. Messages are tied to user accounts for history.

### Decision: Evidence storage approach
**Choice**: Supabase Storage buckets for scan evidence (screenshots, videos)
**Alternatives considered**: S3, local filesystem
**Rationale**: Supabase Storage integrates directly with PostgreSQL via foreign keys. Built-in CDN and access control. No additional AWS/GCP setup needed.

### Decision: File upload handling
**Choice**: Supabase Storage with client-side upload, server-side validation
**Alternatives considered**: Server-side proxy upload, third-party upload service
**Rationale**: Client-side upload reduces server load. Supabase handles multipart uploads natively. Server validates file types and sizes before storage.

### Decision: Database schema design
**Choice**: Normalize into separate tables for users, chats, messages, scans, evidence
**Alternatives considered**: Denormalized JSON, single table
**Rationale**: Normalized schema provides better data integrity, easier querying, and clearer relationships. PostgreSQL handles joins efficiently at our scale.

## Risks / Trade-offs

**[Risk] Supabase vendor lock-in** → Mitigation: Use standard PostgreSQL features, document schema for potential migration
**[Risk] Storage costs for large video evidence** → Mitigation: Implement file size limits, compression, and retention policies
**[Risk] Realtime connection limits** → Mitigation: Use Supabase Realtime sparingly, implement polling fallback
**[Risk] Scan execution time** → Mitigation: Queue-based processing, background jobs, progress indicators
**[Trade-off] Simplicity vs flexibility** → Chose simpler Supabase setup over custom infrastructure for faster development
