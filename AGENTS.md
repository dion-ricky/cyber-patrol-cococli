# AGENTS.md

## Project Overview

Cyber Patrol CLI (`cococli`) - A backend system for scanning the internet for malicious sites (online gambling, scams, illegal lending/BNPL). Features a ChatGPT-like interface for users to chat and request site scans, with evidence capture (screenshots, recordings) stored in blob storage.

## Tech Stack

- **Backend**: Supabase (PostgreSQL + Auth + Storage + Edge Functions + Realtime)
- **Runtime**: Supabase Edge Functions (Deno)
- **Database**: PostgreSQL with Row Level Security (RLS)
- **Storage**: Supabase Blob Storage
- **Auth**: Supabase Auth (email/password)

## Project Structure

```
cyber-patrol-cococli/
├── openspec/                    # OpenSpec change management
│   ├── config.yaml
│   └── changes/
│       └── backend-setup/       # Current active change
├── .opencode/                   # OpenCode configuration
│   ├── skills/                  # OpenSpec workflow skills
│   └── commands/                # Custom slash commands
└── .agents/                     # Agent skills
    └── skills/
        ├── supabase/
        └── supabase-postgres-best-practices/
```

## Conventions

### Git
- Use conventional commits: `feat:`, `fix:`, `chore:`, `docs:`
- Commit messages should be concise

### Code Style
- Follow existing code patterns
- Use Supabase client library conventions
- Keep functions small and focused

## Key Commands

- OpenSpec workflow: Use `/opsx-*` commands (propose, apply, archive, etc.)

## Domain Knowledge

- Malicious site categories: online gambling, scams, illegal lending/BNPL
- Scan evidence: screenshots, screen recordings, page metadata
- Chat system supports text + file attachments
- All user data is protected by RLS policies

## Testing

- Test user management flows end-to-end
- Test chat system with realtime updates
- Test site scanning pipeline
- Test file upload and evidence storage
- Test Row Level Security policies

## Security

- Never expose API keys or secrets
- Always use RLS policies for data access
- Validate file uploads (type + size)
- Use Supabase Auth for all authenticated endpoints
