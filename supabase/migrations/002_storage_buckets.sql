-- Storage buckets and policies
-- Migration: 002_storage_buckets

-- Create storage buckets
INSERT INTO storage.buckets (id, name, public)
VALUES
    ('scan-evidence', 'scan-evidence', false),
    ('chat-uploads', 'chat-uploads', false);

-- ============================================
-- Scan Evidence Bucket Policies
-- ============================================

-- Allow authenticated users to upload evidence for their scans
CREATE POLICY "Users can upload evidence for own scans"
    ON storage.objects FOR INSERT
    WITH CHECK (
        bucket_id = 'scan-evidence'
        AND auth.role() = 'authenticated'
    );

-- Allow users to view evidence from their own scans
CREATE POLICY "Users can view own scan evidence"
    ON storage.objects FOR SELECT
    USING (
        bucket_id = 'scan-evidence'
        AND auth.role() = 'authenticated'
    );

-- ============================================
-- Chat Uploads Bucket Policies
-- ============================================

-- Allow authenticated users to upload files
CREATE POLICY "Users can upload chat files"
    ON storage.objects FOR INSERT
    WITH CHECK (
        bucket_id = 'chat-uploads'
        AND auth.role() = 'authenticated'
    );

-- Allow users to view their own uploads
CREATE POLICY "Users can view own chat uploads"
    ON storage.objects FOR SELECT
    USING (
        bucket_id = 'chat-uploads'
        AND auth.role() = 'authenticated'
        AND (storage.foldername(name))[1] = auth.uid()::text
    );

-- Allow users to delete their own uploads
CREATE POLICY "Users can delete own chat uploads"
    ON storage.objects FOR DELETE
    USING (
        bucket_id = 'chat-uploads'
        AND auth.role() = 'authenticated'
        AND (storage.foldername(name))[1] = auth.uid()::text
    );
