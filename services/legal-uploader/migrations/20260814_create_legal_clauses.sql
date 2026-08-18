-- Migration: create legal_clauses (DDD migrations)
CREATE TABLE IF NOT EXISTS public.legal_clauses (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  document_id UUID NOT NULL REFERENCES public.legal_documents(id) ON DELETE CASCADE,
  section TEXT NULL,
  chapter TEXT NULL,
  chapter_index INTEGER NULL,
  article_number INTEGER NULL,
  clause_number INTEGER NULL,
  point_label TEXT NULL,
  content TEXT NOT NULL,
  order_index INTEGER NOT NULL,
  raw_context JSONB NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_legal_clauses_document_id ON public.legal_clauses(document_id);
CREATE INDEX IF NOT EXISTS idx_legal_clauses_doc_article ON public.legal_clauses(document_id, article_number);
