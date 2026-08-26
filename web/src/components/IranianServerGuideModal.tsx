import React, { useState } from 'react';
import { X, Server, ShieldCheck, Terminal, Smartphone, CreditCard, ChevronLeft, Copy, Check } from 'lucide-react';

interface IranianServerGuideModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const IranianServerGuideModal: React.FC<IranianServerGuideModalProps> = ({ isOpen, onClose }) => {
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);

  if (!isOpen) return null;

  const handleCopy = (code: string, idx: number) => {
    navigator.clipboard.writeText(code);
    setCopiedIndex(idx);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  const steps = [
    {
      stepNum: 1,
      title: 'مرحله اول: تهیه سرور مجازی ایران (Iranian Cloud VPS)',
      badge: 'زیرساخت سرور',
      description:
        'برای دسترسی بدون قطعی و سریع به وب‌سایت کدال (codal.ir) و سامانه TSETMC، باید سرور را از دیتاسنترهای داخل کشور تهیه کنید تا IP سرور کاملاً ایرانی باشد.',
      userActions: [
        'خرید سرور VPS لینوکس Ubuntu 22.04 LTS از ارائه‌دهندگان معتبر (آروان کلود، پارس آنلاین، آسیاتک یا افراپانت).',
        'حداقل مشخصات پیشنهادی: ۲ هسته CPU، ۴ گیگابایت رم، ۴۰ گیگابایت حافظه NVMe.',
        'اطمینان از متصل بودن IP ثابت ایران به سرور.',
      ],
      commandCode: `# اتصال به سرور از طریق SSH:\nssh root@YOUR_SERVER_IP\n\n# به‌روزرسانی پکیج‌های لینوکس:\nsudo apt update && sudo apt upgrade -y`,
    },
    {
      stepNum: 2,
      title: 'مرحله دوم: حل خطای SSL connection timeout و دانلود مستقیم روی سرور',
      badge: 'اجرا روی سرور (حل اختلال گیت‌هاب)',
      description:
        'به علت اختلالات اینترنت و فیلترینگ SSL روی سرورهای ایران، git clone دچار SSL connection timeout شد. برای حل این مشکل، دستورات زیر را کپی و روی سرور اجرا کنید تا پروژه بدون خطا دانلود و اجرا شود:',
      userActions: [
        '۱) دستورات زیر را در SSH سرور کپی و اجرا کنید.',
        '۲) این دستورات چک SSL را غیرفعال کرده و پروژه را به صورت مستقیم دانلود و Unzip می‌کنند.',
      ],
      commandCode: `# ۱) رفع خطای SSL connection timeout در گیت‌هاب:
git config --global http.sslVerify false
git config --global http.postBuffer 524288000

# ۲) رفتن به پوشه وب و دانلود مستقیم فایل zip پروژه:
mkdir -p /var/www && cd /var/www
rm -rf boursnegar app.zip boursnegar-main
curl -k -L https://github.com/jomardi132-maker/boursnegar/archive/refs/heads/main.zip -o app.zip

# ۳) آنزیپ کردن و ورود به پوشه پروژه:
apt install unzip -y
unzip app.zip
mv boursnegar-main boursnegar
cd boursnegar

# ۴) نصب پکیج‌ها، بیلد پروژه و اجرای پایدار با PM2:
npm install
npm run build
pm2 start dist/server.cjs --name bourse-app
pm2 save
pm2 startup`,
    },
    {
      stepNum: 3,
      title: 'مرحله سوم: راه‌اندازی پنل پیامک ایران (کاوه‌نگار / آی‌پی‌پنل)',
      badge: 'سامانه پیامک OTP',
      description:
        'برای ارسال کد تایید یک‌بارمصرف (OTP) و هشدارهای قیمتی، باید کلید API پنل پیامک خود را در فایل .env سرور قرار دهید.',
      userActions: [
        'ثبت‌نام در پنل کاوه‌نگار (kavenegar.com) یا آی‌پی‌پنل (ippanel.com).',
        'تایید خط خدماتی (جهت ارسال پیامک حتی به لیست سیاه بلک‌لیست).',
        'ایجاد الگوی پیامک کد تایید (Pattern Code) مانند: %code% کد ورود شما به سامانه است.',
      ],
      commandCode: `# تنظیم فایل .env سرور:\nKAVENEGAR_API_KEY="your_kavenegar_api_key"\nSMS_PATTERN_CODE="bourse_otp_pattern"\nSMS_LINE_NUMBER="10008000"`,
    },
    {
      stepNum: 4,
      title: 'مرحله چهارم: اتصال درگاه پرداخت بانکی (زرین‌پال / آی‌دی‌پی)',
      badge: 'فروش اشتراک',
      description:
        'جهت دریافت وجه اشتراک ۱ ماهه، ۳ ماهه و ۱ ساله کاربران از طریق کارت‌های عضو شتاب.',
      userActions: [
        'ثبت‌نام و احراز هویت در وب‌سایت زرین‌پال (zarinpal.com) یا IDPay.',
        'دریافت مرچنت کد (Merchant ID) اختصاصی درگاه.',
        'وارد کردن مرچنت کد در فایل تنظیمات سرور.',
      ],
      commandCode: `# افزودن کد درگاه پرداخت به .env:\nZARINPAL_MERCHANT_ID="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"\nCALLBACK_URL="https://yourdomain.ir/api/payment/verify"`,
    },
    {
      stepNum: 5,
      title: 'مرحله پنجم: حل قطعی خطای 502 (Bad Gateway) و بالا آمدن کامل boursnegar.ir',
      badge: 'رفع خطای 502 Bad Gateway & SSL',
      description:
        'تحلیل دقیق تغییر خطای 521 به 502: خطای 502 Bad Gateway یعنی Nginx و کلودفلر کاملاً روشن و به یکدیگر متصل شده‌اند، اما برنامه پردازشی اصلی Node/PM2 روی پورت 3000 پاسخ نمی‌داده است (به علت عدم دریافت متغیر NODE_ENV). اکنون کد سرور آپدیت و هوشمند شد تا بدون نیاز به متغیر محیطی، فایل‌های بیلد dist را روی پورت 3000 اجرا کند. دستورات زیر را کپی و در SSH بزنید تا سایت فوراً بالا بیاید:',
      userActions: [
        '۱) دریافت آخرین نسخه کد آپدیت‌شده از گیت‌هاب و بیلد مجدد پروژه روی سرور.',
        '۲) اجرای برنامه با PM2 و ریستارت Nginx.',
        '۳) تست پاسخ‌دهی پورت 3000 با curl.',
        '۴) تنظیم SSL در پنل کلودفلر: در بخش SSL/TLS حالت را روی «Flexible» بگذارید.',
      ],
      commandCode: `# ۱) دانلود آخرین نسخه آپدیت‌شده کدها و بیلد مجدد:
cd /var/www
rm -rf app.zip boursnegar-main
curl -k -L https://github.com/jomardi132-maker/boursnegar/archive/refs/heads/main.zip -o app.zip
unzip -o app.zip
cp -r boursnegar-main/* boursnegar/
cd /var/www/boursnegar
npm run build

# ۲) اجرای برنامه با PM2 و ریستارت Nginx:
NODE_ENV=production pm2 restart bourse-app --update-env || NODE_ENV=production pm2 start dist/server.cjs --name bourse-app
systemctl restart nginx

# ۳) تست سالم بودن پورت 3000 (باید HTTP/1.1 200 OK دهد):
curl -I http://127.0.0.1:3000

# ۴) دیدن لاگ‌های برنامه جهت اطمینان:
pm2 logs bourse-app --lines 20`,
    },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/90 backdrop-blur-md overflow-y-auto">
      <div className="relative w-full max-w-4xl bg-slate-900 border border-slate-800 rounded-2xl p-5 md:p-6 shadow-2xl space-y-6 text-right my-8">
        {/* Close Button */}
        <button
          type="button"
          onClick={onClose}
          className="absolute top-4 left-4 p-1 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Header */}
        <div className="flex items-center gap-3 border-b border-slate-800 pb-4">
          <div className="w-10 h-10 rounded-xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400 shrink-0">
            <Server className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-base md:text-lg font-bold text-white flex items-center gap-2">
              <span>راهنمای گام‌به‌گام پیاده‌سازی روی سرور ایران & کسب درآمد اشتراکی</span>
              <span className="text-xs bg-cyan-500/20 text-cyan-300 px-2 py-0.5 rounded border border-cyan-500/30 font-mono">
                Deployment Manual
              </span>
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              مراحل کامل راه‌اندازی سرور، اتصال به کدال، پیامک یک‌بارمصرف و درگاه پرداخت بانکی
            </p>
          </div>
        </div>

        {/* Steps accordion style list */}
        <div className="space-y-4">
          {steps.map((s, idx) => (
            <div key={s.stepNum} className="bg-slate-950 border border-slate-800 rounded-xl p-4 space-y-3">
              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 border-b border-slate-900 pb-2.5">
                <div className="flex items-center gap-2.5">
                  <span className="w-7 h-7 rounded-lg bg-cyan-500/20 border border-cyan-500/40 text-cyan-300 font-extrabold font-mono text-xs flex items-center justify-center">
                    {s.stepNum}
                  </span>
                  <h4 className="text-sm font-bold text-white">{s.title}</h4>
                </div>
                <span className="text-[10px] bg-slate-800 text-slate-300 px-2.5 py-0.5 rounded-full font-mono">
                  {s.badge}
                </span>
              </div>

              <p className="text-xs text-slate-300/90 leading-relaxed">{s.description}</p>

              {/* User Checklist */}
              <div className="space-y-1.5 pt-1">
                <span className="text-[11px] font-bold text-amber-400 block">
                  اقداماتی که شما باید انجام دهید:
                </span>
                <ul className="space-y-1 text-xs text-slate-300">
                  {s.userActions.map((act, i) => (
                    <li key={i} className="flex items-start gap-1.5">
                      <ChevronLeft className="w-3.5 h-3.5 text-cyan-400 shrink-0 mt-0.5" />
                      <span>{act}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Shell Commands Box */}
              <div className="relative bg-slate-900 rounded-lg p-3 border border-slate-800 font-mono text-xs text-emerald-300 dir-ltr text-left overflow-x-auto">
                <button
                  type="button"
                  onClick={() => handleCopy(s.commandCode, idx)}
                  className="absolute top-2 right-2 bg-slate-800 hover:bg-slate-700 text-slate-300 p-1.5 rounded transition-all text-[10px] flex items-center gap-1 dir-rtl"
                >
                  {copiedIndex === idx ? (
                    <>
                      <Check className="w-3 h-3 text-emerald-400" />
                      <span>کپی شد</span>
                    </>
                  ) : (
                    <>
                      <Copy className="w-3 h-3" />
                      <span>کپی دستورات</span>
                    </>
                  )}
                </button>
                <pre className="whitespace-pre-wrap">{s.commandCode}</pre>
              </div>
            </div>
          ))}
        </div>

        {/* Footer info */}
        <div className="p-3 bg-amber-500/10 border border-amber-500/30 rounded-xl text-xs text-amber-300 leading-relaxed">
          <strong>نکته مهم تجاری:</strong> با اجرای این ۵ گام، نرم‌افزار شما به‌طور ۱۰۰٪ مستقل روی سرور ایران بدون وابسته بودن به تحریم‌ها یا سرویس‌های خارجی اجرا می‌شود و می‌توانید با تعریف پلن‌های اشتراکی درگاه زرین‌پال، درآمد غیرفعال داشته باشید.
        </div>
      </div>
    </div>
  );
};
