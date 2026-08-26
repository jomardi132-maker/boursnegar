import fs from 'node:fs';
import dotenv from 'dotenv';
import { createPasswordReset } from '../server/auth';
import { sendPasswordResetEmail } from '../server/mailer';

dotenv.config({ path: '/var/www/boursnegar-shared/web.env', quiet: true });
const recipientPath = '/tmp/boursnegar-test-email.input';
const tokenPath = '/tmp/boursnegar-e2e-reset-token';
const recipient = fs.readFileSync(recipientPath, 'utf8').trim();
const mode = process.argv[2] === 'send' ? 'send' : 'no-send';
const token = await createPasswordReset(recipient, '127.0.0.1');
if (!token) throw new Error('TEST_IDENTITY_NOT_FOUND');
fs.writeFileSync(tokenPath, token, { encoding: 'utf8', mode: 0o600 });
if (mode === 'send') {
  await sendPasswordResetEmail(recipient, `${process.env.PUBLIC_ORIGIN || 'https://boursnegar.ir'}/?reset-token=${encodeURIComponent(token)}`);
}
console.log(mode === 'send' ? 'RESET_EMAIL=SUBMITTED' : 'EXPIRY_TOKEN=CREATED');
