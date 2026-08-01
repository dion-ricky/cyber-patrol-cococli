# AGENTS.md

## Project Overview

Cyber Patrol CLI (`cococli`) - A backend system for scanning the internet for malicious sites (online gambling, scams, illegal lending/BNPL). Features a ChatGPT-like interface for users to chat and request site scans, with evidence capture (screenshots, recordings) stored in blob storage.

## Tech Stack

- **Backend**: Deno / Python
- **Database**: PostgreSQL
- **Storage**: Blob storage for evidence files

## Project Structure

```
cyber-patrol-cococli/
├── .opencode/                   # OpenCode configuration
└── .agents/                     # Agent skills
```

## Conventions

### Git
- Use conventional commits: `feat:`, `fix:`, `chore:`, `docs:`
- Commit messages should be concise

### Code Style
- Follow existing code patterns
- Keep functions small and focused

## Domain Knowledge

- Malicious site categories: online gambling, scams, illegal lending/BNPL
- Scan evidence: screenshots, screen recordings, page metadata
- Chat system supports text + file attachments

## Testing

- Test user management flows end-to-end
- Test chat system updates
- Test site scanning pipeline
- Test file upload and evidence storage

## Security

- Never expose API keys or secrets
- Validate file uploads (type + size)
