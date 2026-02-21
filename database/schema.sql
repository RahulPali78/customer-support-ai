-- Customer Support AI Database Schema
-- Run this in Supabase SQL Editor

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Main emails table
CREATE TABLE emails (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    external_id VARCHAR(255) UNIQUE, -- Gmail/Outlook message ID
    sender_email VARCHAR(255) NOT NULL,
    sender_name VARCHAR(255),
    subject TEXT NOT NULL,
    body_text TEXT,
    body_html TEXT,
    received_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    classification VARCHAR(50), -- REFUND, STATUS, COMPLAINT, GENERAL, OTHER
    confidence DECIMAL(3,2), -- 0.00 to 1.00
    ai_response TEXT, -- Generated response draft
    status VARCHAR(50) DEFAULT 'pending', -- pending, auto_replied, escalated, resolved
    assigned_agent VARCHAR(255),
    order_id VARCHAR(100),
    action_taken VARCHAR(255), -- What the system actually did
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Knowledge base documents for RAG
CREATE TABLE knowledge_documents (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(100), -- RETURNS, SHIPPING, PRODUCTS, etc.
    embedding VECTOR(1536), -- For semantic search (requires pgvector)
    metadata JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Audit log for all AI actions
CREATE TABLE audit_log (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    email_id UUID REFERENCES emails(id),
    action VARCHAR(100) NOT NULL, -- classify, generate_response, escalate
    model_used VARCHAR(100), -- gpt-4o-mini, gpt-4o, etc.
    prompt_tokens INTEGER,
    completion_tokens INTEGER,
    total_cost DECIMAL(10,6), -- In USD
    raw_request JSONB, -- Full API request (sanitized)
    raw_response JSONB, -- Full API response
    duration_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Analytics view: Daily metrics
CREATE VIEW daily_metrics AS
SELECT 
    DATE_TRUNC('day', received_at) as date,
    COUNT(*) as total_emails,
    COUNT(CASE WHEN classification = 'REFUND' THEN 1 END) as refund_requests,
    COUNT(CASE WHEN classification = 'STATUS' THEN 1 END) as status_inquiries,
    COUNT(CASE WHEN classification = 'COMPLAINT' THEN 1 END) as complaints,
    COUNT(CASE WHEN classification = 'GENERAL' THEN 1 END) as general_inquiries,
    COUNT(CASE WHEN status = 'auto_replied' THEN 1 END) as auto_replied,
    COUNT(CASE WHEN status = 'escalated' THEN 1 END) as escalated,
    ROUND(AVG(confidence), 2) as avg_confidence,
    SUM((raw_response->>'total_tokens')::int) filter (where audit_log.created_at = emails.created_at) as total_tokens_daily
FROM emails
LEFT JOIN audit_log ON emails.id = audit_log.email_id
GROUP BY DATE_TRUNC('day', received_at)
ORDER BY date DESC;

-- Indexes for performance
CREATE INDEX idx_emails_classification ON emails(classification);
CREATE INDEX idx_emails_status ON emails(status);
CREATE INDEX idx_emails_received_at ON emails(received_at DESC);
CREATE INDEX idx_emails_sender ON emails(sender_email);
CREATE INDEX idx_audit_email_id ON audit_log(email_id);

-- Enable Row Level Security
ALTER TABLE emails ENABLE ROW LEVEL SECURITY;
ALTER TABLE knowledge_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_log ENABLE ROW LEVEL SECURITY;

-- Create RLS policies (public read for demo)
CREATE POLICY "Allow all reads" ON emails FOR SELECT USING (true);
CREATE POLICY "Allow all inserts" ON emails FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow all updates" ON emails FOR UPDATE USING (true);

-- Row level security for other tables
CREATE POLICY "Allow all operations" ON knowledge_documents FOR ALL USING (true);
CREATE POLICY "Allow all operations" ON audit_log FOR ALL USING (true);

-- Insert sample knowledge documents
INSERT INTO knowledge_documents (title, content, category) VALUES
('Return Policy', 'We accept returns within 30 days of purchase. Items must be unused and in original packaging. Refunds processed within 5-7 business days to original payment method.', 'RETURNS'),
('Shipping Times', 'UK: 2-3 business days. EU: 5-7 business days. Rest of world: 7-14 business days. Express shipping available at checkout.', 'SHIPPING'),
('Order Tracking', 'Track your order using the link in your confirmation email or on our website under Order Status. Use your order number and email to lookup.', 'SHIPPING'),
('Damaged Items', 'If your item arrived damaged, please send photos to support@company.com within 48 hours. We will arrange replacement or full refund including shipping.', 'RETURNS'),
('Product Ingredients', 'All ingredients are listed on product pages and packaging. We use natural, cruelty-free ingredients. Contact us for specific allergen questions.', 'PRODUCTS');

-- Verify pgvector extension (for embeddings)
-- Run: CREATE EXTENSION IF NOT EXISTS vector;
-- Note: Enable this in Supabase Dashboard > Extensions first