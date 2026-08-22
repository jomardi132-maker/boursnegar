import nodemailer from 'nodemailer';

function smtpConfiguration() {
  const host = process.env.SMTP_HOST;
  const user = process.env.SMTP_USER;
  const password = process.env.SMTP_PASSWORD;
  const from = process.env.SMTP_FROM;
  if (!host || !user || !password || !from) return null;
  const port = Number(process.env.SMTP_PORT || 587);
  if (!Number.isInteger(port) || port < 1 || port > 65535) throw new Error('Invalid SMTP_PORT');
  return { host, port, user, password, from };
}

export function mailDeliveryReady(): boolean {
  return process.env.EMAIL_ENABLED === 'true' && smtpConfiguration() !== null;
}

export async function sendPasswordResetEmail(email: string, resetUrl: string): Promise<void> {
  const config = smtpConfiguration();
  if (!config) throw new Error('MAIL_NOT_CONFIGURED');
  const transport = nodemailer.createTransport({
    host: config.host,
    port: config.port,
    secure: config.port === 465,
    auth: { user: config.user, pass: config.password },
    requireTLS: config.port !== 465,
  });
  await transport.sendMail({
    from: config.from,
    to: email,
    subject: 'بازیابی رمز عبور بورس‌نگار',
    text: `برای تعیین رمز عبور جدید، تا ۳۰ دقیقه آینده این پیوند را باز کنید:\n${resetUrl}\n\nاگر این درخواست را شما ثبت نکرده‌اید، آن را نادیده بگیرید.`,
    html: `<div dir="rtl" style="font-family:Tahoma,Arial,sans-serif;line-height:1.9"><h2>بازیابی رمز عبور بورس‌نگار</h2><p>برای تعیین رمز عبور جدید، تا ۳۰ دقیقه آینده روی دکمه زیر بزنید.</p><p><a href="${resetUrl}" style="display:inline-block;padding:12px 20px;background:#059669;color:#fff;text-decoration:none;border-radius:8px">تعیین رمز جدید</a></p><p>اگر این درخواست را شما ثبت نکرده‌اید، آن را نادیده بگیرید.</p></div>`,
  });
}

export async function sendEmailVerificationEmail(email: string, code: string): Promise<void> {
  const config = smtpConfiguration();
  if (!config) throw new Error('MAIL_NOT_CONFIGURED');
  const transport = nodemailer.createTransport({ host: config.host, port: config.port, secure: config.port === 465, auth: { user: config.user, pass: config.password }, requireTLS: config.port !== 465 });
  await transport.sendMail({
    from: config.from, to: email, subject: 'تأیید ایمیل بورس‌نگار',
    text: `کد تأیید ایمیل بورس‌نگار: ${code}\nاین کد تا ۱۰ دقیقه معتبر است.`,
    html: `<div dir="rtl" style="font-family:Tahoma,Arial,sans-serif;line-height:1.9"><h2>تأیید ایمیل بورس‌نگار</h2><p>کد تأیید شما:</p><p style="font-size:28px;letter-spacing:8px;font-weight:bold">${code}</p><p>این کد تا ۱۰ دقیقه معتبر است.</p></div>`,
  });
}

export async function sendCreditNoticeEmail(email: string, delta: number, reason: string, balance: number): Promise<void> {
  const config = smtpConfiguration();
  if (!config) throw new Error('MAIL_NOT_CONFIGURED');
  const transport = nodemailer.createTransport({ host: config.host, port: config.port, secure: config.port === 465, auth: { user: config.user, pass: config.password }, requireTLS: config.port !== 465 });
  const subject = `افزایش اعتبار بورس‌نگار — ${reason}`;
  await transport.sendMail({ from: config.from, to: email, subject, text: `${delta} اعتبار به حساب شما اضافه شد.\nدلیل: ${reason}\nموجودی جدید: ${balance} اعتبار`, html: `<div dir="rtl" style="font-family:Tahoma,Arial,sans-serif;line-height:1.9"><h2>${subject}</h2><p><b>${delta} اعتبار</b> به حساب شما اضافه شد.</p><p>دلیل: ${reason}<br/>موجودی جدید: ${balance} اعتبار</p></div>` });
}
