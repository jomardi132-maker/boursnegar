BEGIN;
INSERT INTO system_settings(key,value,is_public) VALUES ('referral_referrer_reward','10',false),('referral_referred_reward','5',false),('referral_monthly_cap','10',false) ON CONFLICT (key) DO NOTHING;
INSERT INTO schema_migrations(version) VALUES ('011_referral_rewards') ON CONFLICT DO NOTHING;
COMMIT;
