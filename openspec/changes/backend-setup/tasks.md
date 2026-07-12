## 1. Supabase Project Setup

- [ ] 1.1 Create Supabase project and configure database
- [ ] 1.2 Set up Supabase Auth with email/password provider
- [ ] 1.3 Create storage buckets (scan-evidence, chat-uploads)
- [ ] 1.4 Configure storage access policies
- [ ] 1.5 Enable Supabase Realtime for chat updates

## 2. Database Schema

- [ ] 2.1 Create users table with auth integration
- [ ] 2.2 Create chat_sessions table with user foreign key
- [ ] 2.3 Create chat_messages table with session foreign key
- [ ] 2.4 Create site_scans table with user and message foreign keys
- [ ] 2.5 Create scan_evidence table with scan foreign key
- [ ] 2.6 Add database indexes for performance
- [ ] 2.7 Set up Row Level Security (RLS) policies

## 3. User Management API

- [ ] 3.1 Implement user registration endpoint
- [ ] 3.2 Implement user login endpoint
- [ ] 3.3 Implement user profile CRUD endpoints
- [ ] 3.4 Implement session token refresh logic
- [ ] 3.5 Implement logout and session invalidation

## 4. Chat System API

- [ ] 4.1 Implement create chat session endpoint
- [ ] 4.2 Implement send message endpoint (text + file)
- [ ] 4.3 Implement get chat history endpoint
- [ ] 4.4 Implement list user chats endpoint
- [ ] 4.5 Implement delete chat session endpoint
- [ ] 4.6 Set up Realtime subscription for new messages

## 5. Site Scanning Edge Function

- [ ] 5.1 Create Edge Function project structure
- [ ] 5.2 Implement scan trigger endpoint (HTTP or webhook)
- [ ] 5.3 Implement scanning logic in Edge Function
- [ ] 5.4 Implement scan result storage via Supabase client
- [ ] 5.5 Add Edge Function error handling and retries
- [ ] 5.6 Deploy Edge Function to Supabase
- [ ] 5.7 Implement get scan result API endpoint
- [ ] 5.8 Implement scan status tracking API endpoint

## 6. Evidence Storage API

- [ ] 6.1 Implement upload evidence endpoint
- [ ] 6.2 Implement get evidence list endpoint
- [ ] 6.3 Implement download evidence endpoint
- [ ] 6.4 Implement evidence metadata storage

## 7. File Upload API

- [ ] 7.1 Implement chat file upload endpoint
- [ ] 7.2 Add file type validation
- [ ] 7.3 Add file size validation
- [ ] 7.4 Implement file access control policies

## 8. Integration & Testing

- [ ] 8.1 Test user management flows end-to-end
- [ ] 8.2 Test chat system with realtime updates
- [ ] 8.3 Test site scanning pipeline
- [ ] 8.4 Test file upload and evidence storage
- [ ] 8.5 Test Row Level Security policies
