import fs from 'node:fs';
import dotenv from 'dotenv';
import nodemailer from 'nodemailer';

dotenv.config({ path: '/var/www/bourse-analyzer/.env', quiet: true });
const recipient = fs.readFileSync('/tmp/boursnegar-test-email.input', 'utf8').trim();
if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(recipient)) throw new Error('INVALID_TEST_RECIPIENT');
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
  socketTimeout: 15_000,
});
await transport.sendMail({
  from: process.env.SMTP_FROM,
  to: recipient,
  subject: 'آزمایش کنترل‌شده ایمیل بورس‌نگار',
  text: 'این پیام فقط برای تأیید اتصال امن سرویس ایمیل بورس‌نگار ارسال شده است.',
  html: '<div dir="rtl" style="font-family:Tahoma,Arial,sans-serif;line-height:1.9"><h2>آزمایش ایمیل بورس‌نگار</h2><p>این پیام فقط برای تأیید اتصال امن سرویس ایمیل ارسال شده است.</p></div>',
});
transport.close();
console.log('CONTROLLED_EMAIL=SUBMITTED');
