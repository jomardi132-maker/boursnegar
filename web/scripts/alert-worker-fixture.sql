WITH created AS (
  INSERT INTO users(mobile_e164, role_id, referral_code)
  VALUES ('+989120000001', (SELECT id FROM roles WHERE code='user'), 'WORKERTEST')
  RETURNING id
)
INSERT INTO alerts(user_id, symbol, kind, comparator, target_value)
SELECT id, 'فولاد', 'price', 'gte', 100 FROM created
UNION ALL
SELECT id, 'فولاد', 'pe', 'gte', 2 FROM created
UNION ALL
SELECT id, 'فولاد', 'codal', NULL, NULL FROM created;
