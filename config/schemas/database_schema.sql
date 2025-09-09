-- SQLBook: Code
-- Dark Data Database Schema for Power System Failures
-- Supports JSON storage, full-text search, and RAG integration

CREATE TABLE incidents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    failure_date DATE NOT NULL,
    failure_time TIME NOT NULL,
    disconnected_mw REAL,
    classification TEXT,
    
    -- JSON storage for complex nested data
    raw_json TEXT, -- Full original JSON
    incident_details JSON, -- Structured incident info
    affected_installations JSON, -- Installation details
    generation_units JSON, -- Generation unit data
    transmission_elements JSON, -- Transmission data
    
    -- Text fields for RAG/semantic search
    failure_cause_text TEXT, -- Full failure description
    technical_summary TEXT, -- Technical details summary
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    document_pages INTEGER,
    extraction_date TIMESTAMP
);

CREATE TABLE companies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    rut TEXT,
    legal_representative TEXT,
    address TEXT
);

CREATE TABLE compliance_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_id INTEGER REFERENCES incidents(id),
    company_id INTEGER REFERENCES companies(id),
    reports_48h_status TEXT,
    reports_5d_status TEXT,
    compliance_issues JSON, -- Store issues as JSON array
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE equipment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    manufacturer TEXT,
    model TEXT,
    installation_date DATE,
    function_affected TEXT,
    system_number TEXT,
    raw_details JSON -- Store all equipment data
);

-- Full-text search indexes for RAG
CREATE VIRTUAL TABLE incidents_fts USING fts5(
    report_id,
    title,
    failure_cause_text,
    technical_summary,
    content=incidents
);

-- Indexes for performance
CREATE INDEX idx_incidents_date ON incidents(failure_date);
CREATE INDEX idx_incidents_classification ON incidents(classification);
CREATE INDEX idx_compliance_company ON compliance_reports(company_id);

-- Views for common queries
CREATE VIEW failure_summary AS
SELECT 
    i.report_id,
    i.title,
    i.failure_date,
    i.disconnected_mw,
    i.classification,
    COUNT(DISTINCT cr.company_id) as companies_affected,
    GROUP_CONCAT(DISTINCT c.name) as company_names
FROM incidents i
LEFT JOIN compliance_reports cr ON i.id = cr.incident_id  
LEFT JOIN companies c ON cr.company_id = c.id
GROUP BY i.id;