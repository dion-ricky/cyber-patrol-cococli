## 1. Supabase Project Setup

- [x] 1.1 Create Supabase project and configure database
- [x] 1.2 Set up Supabase Auth with email/password provider
- [x] 1.3 Create storage buckets (scan-evidence, chat-uploads)
- [x] 1.4 Configure storage access policies
- [x] 1.5 Enable Supabase Realtime for chat updates

## 2. Database Schema

- [x] 2.1 Create users table with auth integration
- [x] 2.2 Create chat_sessions table with user foreign key
- [x] 2.3 Create chat_messages table with session foreign key
- [x] 2.4 Create site_scans table with user and message foreign keys
- [x] 2.5 Create scan_evidence table with scan foreign key
- [x] 2.6 Add database indexes for performance
- [x] 2.7 Set up Row Level Security (RLS) policies

## 3. User Management API

- [x] 3.1 Implement user registration endpoint
- [x] 3.2 Implement user login endpoint
- [x] 3.3 Implement user profile CRUD endpoints
- [x] 3.4 Implement session token refresh logic
- [x] 3.5 Implement logout and session invalidation

## 4. Chat System API

- [x] 4.1 Implement create chat session endpoint
- [x] 4.2 Implement send message endpoint (text + file)
- [x] 4.3 Implement get chat history endpoint
- [x] 4.4 Implement list user chats endpoint
- [x] 4.5 Implement delete chat session endpoint
- [ ] 4.6 Set up Realtime subscription for new messages

## 5. Site Scanning Edge Function

- [x] 5.1 Create Edge Function project structure
- [x] 5.2 Implement scan trigger endpoint (HTTP or webhook)
- [x] 5.3 Implement scanning logic in Edge Function
- [x] 5.4 Implement scan result storage via Supabase client
- [x] 5.5 Add Edge Function error handling and retries
- [ ] 5.6 Deploy Edge Function to Supabase
- [x] 5.7 Implement get scan result API endpoint
- [x] 5.8 Implement scan status tracking API endpoint

## 6. Evidence Storage API

- [x] 6.1 Implement upload evidence endpoint
- [x] 6.2 Implement get evidence list endpoint
- [x] 6.3 Implement download evidence endpoint
- [x] 6.4 Implement evidence metadata storage

## 7. File Upload API

- [x] 7.1 Implement chat file upload endpoint
- [x] 7.2 Add file type validation
- [x] 7.3 Add file size validation
- [x] 7.4 Implement file access control policies

## 8. Integration & Testing

- [ ] 8.1 Test user management flows end-to-end
- [ ] 8.2 Test chat system with realtime updates
- [ ] 8.3 Test site scanning pipeline
- [ ] 8.4 Test file upload and evidence storage
- [ ] 8.5 Test Row Level Security policies
