-- Total claims by status
SELECT
    status,
    COUNT(*) AS total_claims,
    SUM(claim_amount) AS total_amount
FROM claims
GROUP BY status
ORDER BY total_claims DESC;

-- Provider-level claim totals
SELECT
    provider_id,
    COUNT(*) AS claim_count,
    SUM(claim_amount) AS total_claim_amount,
    AVG(claim_amount) AS average_claim_amount
FROM claims
GROUP BY provider_id
ORDER BY total_claim_amount DESC;

-- Rejection summary
SELECT
    rejection_reason,
    COUNT(*) AS rejected_count
FROM rejected_claims
GROUP BY rejection_reason
ORDER BY rejected_count DESC;

-- Daily approved claim totals
SELECT
    claim_date,
    COUNT(*) AS approved_claims,
    SUM(claim_amount) AS approved_amount
FROM claims
WHERE status = 'APPROVED'
GROUP BY claim_date
ORDER BY claim_date;