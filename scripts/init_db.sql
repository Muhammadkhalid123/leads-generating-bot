-- Keywords table
CREATE TABLE IF NOT EXISTS keywords (
    id SERIAL PRIMARY KEY,
    keyword VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL, -- 'hiring_intent', 'pain_point', 'tool_mention'
    source VARCHAR(20) NOT NULL,   -- 'reddit', 'upwork', 'amazon'
    weight INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Leads table
CREATE TABLE IF NOT EXISTS leads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source VARCHAR(20) NOT NULL,
    source_url TEXT,
    source_id VARCHAR(255),
    
    author_name VARCHAR(255),
    author_email VARCHAR(255),
    author_website VARCHAR(500),
    reddit_username VARCHAR(100),
    
    book_title VARCHAR(500),
    book_asin VARCHAR(20),
    book_category VARCHAR(100),
    
    formatting_issues JSONB,
    pain_point_summary TEXT,
    matched_keywords TEXT[],
    
    raw_content TEXT,
    relevance_score FLOAT DEFAULT 0.0,
    outreach_draft TEXT,
    
    status VARCHAR(30) DEFAULT 'new',
    contacted_at TIMESTAMP,
    notes TEXT,
    
    discovered_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_leads_source ON leads(source);
CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);
CREATE INDEX IF NOT EXISTS idx_leads_discovered ON leads(discovered_at DESC);
CREATE INDEX IF NOT EXISTS idx_leads_relevance ON leads(relevance_score DESC);
