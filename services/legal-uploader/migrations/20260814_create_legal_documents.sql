-- Migration: create legal_documents (DDD migrations)
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE TABLE IF NOT EXISTS public.legal_documents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title TEXT,
  reference_number TEXT,
  issued_date DATE,
  original_filename TEXT NOT NULL,
  storage_path TEXT NOT NULL,
  uploader_id UUID,
  status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
  error_message TEXT,
  approved_by UUID,
  approved_at TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_legal_documents_reference_number ON public.legal_documents(reference_number);
CREATE INDEX IF NOT EXISTS idx_legal_documents_status ON public.legal_documents(status);
