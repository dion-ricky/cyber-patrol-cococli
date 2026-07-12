# Cyber Patrol Backend

Supabase backend for the Cyber Patrol application.

## Project Structure

```
supabase/
├── config.toml           # Supabase project configuration
├── seed.sql             # Development seed data
├── migrations/          # Database migrations
│   ├── 001_initial_schema.sql
│   └── 002_storage_buckets.sql
└── functions/           # Edge Functions
    ├── _shared/         # Shared utilities
    │   └── supabase.ts
    ├── user-auth/       # User authentication
    ├── chat-api/        # Chat system API
    ├── evidence-api/    # Evidence storage API
    ├── file-upload-api/ # File upload API
    └── scan-site/       # Site scanning Edge Function
```

## Setup

1. Create a Supabase project at https://supabase.com
2. Run migrations in order:
   ```bash
   supabase db push
   ```
3. Deploy Edge Functions:
   ```bash
   supabase functions deploy
   ```

## API Endpoints

All endpoints are Edge Functions accessible at:
`https://<project-ref>.supabase.co/functions/v1/<function-name>`

### User Auth (`user-auth`)
- `POST /register` - Create new account
- `POST /login` - Sign in with email/password
- `POST /logout` - Sign out
- `POST /refresh` - Refresh access token
- `POST /get_profile` - Get user profile
- `POST /update_profile` - Update user profile

### Chat API (`chat-api`)
- `POST /create_session` - Create new chat session
- `POST /send_message` - Send message in session
- `POST /get_history` - Get session message history
- `POST /list_chats` - List user's chat sessions
- `POST /delete_session` - Delete a chat session

### Evidence API (`evidence-api`)
- `POST /upload_evidence` - Store scan evidence
- `POST /list_evidence` - List evidence for a scan
- `POST /download_evidence` - Get evidence details

### File Upload API (`file-upload-api`)
- `POST /upload_chat_file` - Get signed upload URL for chat files
- `POST /get_upload_url` - Get generic signed upload URL

### Site Scanning (`scan-site`)
- `POST /` - Trigger site scan (called internally or via webhook)

## Authentication

All endpoints require a valid Supabase JWT token in the Authorization header:
```
Authorization: Bearer <access-token>
```

## Development

1. Start local Supabase:
   ```bash
   supabase start
   ```

2. Access Supabase Studio at http://localhost:54323

3. Test Edge Functions:
   ```bash
   supabase functions serve user-auth
   ```
