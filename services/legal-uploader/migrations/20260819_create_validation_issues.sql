-- Optional migration: create validation_issues table
CREATE TABLE IF NOT EXISTS validation_issues (
  id serial PRIMARY KEY,
  document_id uuid REFERENCES legal_documents(id) ON DELETE CASCADE,
  clause_id uuid NULL,
  issue_type varchar(128) NOT NULL,
  issue_code varchar(128) NOT NULL,
  message text,
  severity varchar(16) NOT NULL,
  rule_name varchar(128) NOT NULL,
  rule_payload jsonb,
  created_at timestamptz DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_validation_issues_document ON validation_issues(document_id);
CREATE INDEX IF NOT EXISTS idx_validation_issues_clause ON validation_issues(clause_id);
