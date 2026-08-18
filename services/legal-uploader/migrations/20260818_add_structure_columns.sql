-- Migration: add legal structure columns to legal_clauses (Phase 2)
ALTER TABLE IF EXISTS public.legal_clauses
  ADD COLUMN IF NOT EXISTS part TEXT,
  ADD COLUMN IF NOT EXISTS subsection TEXT,
  ADD COLUMN IF NOT EXISTS article_title TEXT,
  ADD COLUMN IF NOT EXISTS article_id UUID,
  ADD COLUMN IF NOT EXISTS start_paragraph_index INTEGER,
  ADD COLUMN IF NOT EXISTS end_paragraph_index INTEGER,
  ADD COLUMN IF NOT EXISTS parent_clause_id UUID,
  ADD COLUMN IF NOT EXISTS is_needs_review BOOLEAN DEFAULT FALSE,
  ADD COLUMN IF NOT EXISTS review_reason TEXT;

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_legal_clauses_doc_article ON public.legal_clauses(document_id, article_number);
CREATE INDEX IF NOT EXISTS idx_legal_clauses_doc_order ON public.legal_clauses(document_id, order_index);
