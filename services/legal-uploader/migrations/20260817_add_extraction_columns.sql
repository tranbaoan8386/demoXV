-- Migration: add extraction columns to legal_documents
ALTER TABLE IF EXISTS public.legal_documents
  ADD COLUMN IF NOT EXISTS content_hash TEXT,
  ADD COLUMN IF NOT EXISTS extracted_path TEXT,
  ADD COLUMN IF NOT EXISTS extraction_status TEXT,
  ADD COLUMN IF NOT EXISTS extraction_error TEXT;

-- No destructive changes; additive migration only.
