# Cyber Patrol CLI (cococli)

A backend system for scanning the internet for malicious sites and providing a ChatGPT-like interface for users to interact with scan results.

## Features

- **Site Scanning**: Detect malicious sites (online gambling, scams, illegal lending/BNPL)
- **Chat Interface**: ChatGPT-like conversation with scan request capabilities
- **Evidence Capture**: Screenshots, screen recordings, and page metadata stored in blob storage
- **File Uploads**: Support for image and file attachments in chat messages
- **User Management**: Authentication, profiles, and session handling

## Tech Stack

- Supabase (PostgreSQL, Auth, Storage, Edge Functions, Realtime)
- Supabase Edge Functions (Deno)
- PostgreSQL with Row Level Security

## Getting Started

1. Create a Supabase project
2. Configure database schema (see `openspec/changes/backend-setup/specs/`)
3. Set up storage buckets (`scan-evidence`, `chat-uploads`)
4. Deploy Edge Functions for site scanning
5. Configure RLS policies for data access

## Project Structure

- `openspec/` - OpenSpec change management and specifications
- `.opencode/` - OpenCode configuration and workflow skills
- `.agents/` - Agent skills (Supabase, Postgres best practices)

## Development

Use OpenSpec workflow commands:
- `/opsx-propose` - Propose a new change
- `/opsx-apply` - Implement tasks from a change
- `/opsx-archive` - Archive completed changes

## License

MIT
