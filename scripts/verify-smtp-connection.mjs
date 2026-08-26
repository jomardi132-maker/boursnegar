import dotenv from 'dotenv';
import nodemailer from 'nodemailer';

dotenv.config({ path: '/var/www/boursnegar-shared/web.env', quiet: true });
const required = ['SMTP_HOST', 'SMTP_PORT', 'SMTP_USER', 'SMTP_PASSWORD', 'SMTP_FROM'];
if (required.some((key) => !process.env[key])) throw new Error('SMTP_CONFIG_INCOMPLETE');
const port = Number(process.env.SMTP_PORT);
const transport = nodemailer.createTransport({
  host: process.env.SMTP_HOST,
  port,
  secure: port === 465,
  auth: { user: process.env.SMTP_USER, pass: process.env.SMTP_PASSWORD },
  requireTLS: port !== 465,
  connectionTimeout: 10_000,
  greetingTimeout: 10_000,
  socketTimeout: 15_000,
});
await transport.verify();
transport.close();
console.log('SMTP_CONNECTION=PASS');
