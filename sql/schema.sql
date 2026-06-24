DROP TABLE IF EXISTS rejected_claims;
DROP TABLE IF EXISTS claims;

CREATE TABLE claims (
    claim_id TEXT PRIMARY KEY,
    member_id TEXT NOT NULL,
    provider_id TEXT NOT NULL,
    claim_date DATE NOT NULL,
    claim_amount NUMERIC(10, 2) NOT NULL,
    status TEXT NOT NULL,
    diagnosis_code TEXT,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE rejected_claims (
    id SERIAL PRIMARY KEY,
    claim_id TEXT,
    member_id TEXT,
    provider_id TEXT,
    claim_date TEXT,
    claim_amount TEXT,
    status TEXT,
    diagnosis_code TEXT,
    rejection_reason TEXT NOT NULL,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);