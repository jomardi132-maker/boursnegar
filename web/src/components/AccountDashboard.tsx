import { FormEvent, useEffect, useState } from "react";
import {
  Bell,
  CreditCard,
  Gauge,
  History,
  Megaphone,
  Settings,
  Shield,
  Users,
  X,
} from "lucide-react";
import { api, type User } from "../AppProduction";
import "../payment.css";

type Props = {
  user: User;
  onClose: () => void;
  onCredits: (value: number) => void;
};
type Overview = {
  credits: number;
  subscription: any;
  payments: any[];
  referralCode: string;
};
type Tab =
  "overview" | "history" | "payments" | "referrals" | "alerts" | "admin";

export function AccountDashboard({ user, onClose, onCredits }: Props) {
  const [tab, setTab] = useState<Tab>("overview");
  const [data, setData] = useState<any>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  async function load(next = tab) {
    setBusy(true);
    setError("");
    try {
      if (next === "payments") {
        const [plans, campaigns] = await Promise.all([
          api<any>("/api/plans"),
          api<any>("/api/campaigns"),
        ]);
        setData({ plans: plans.plans, campaigns: campaigns.campaigns });
        return;
      }
      const url =
        next === "overview"
          ? "/api/account/overview"
          : next === "history"
            ? "/api/account/analyses"
            : next === "referrals"
              ? "/api/account/referrals"
              : next === "alerts"
                ? "/api/alerts"
                : "/api/admin/stats";
      setData(await api(url));
    } catch (e) {
      setError(e instanceof Error ? e.message : "خطا در دریافت اطلاعات");
    } finally {
      setBusy(false);
    }
  }
  useEffect(() => {
    load(tab);
  }, [tab]);
  return (
    <div
      className="modal-backdrop dashboard-backdrop"
      onMouseDown={(e) => e.target === e.currentTarget && onClose()}
    >
      <section
        className="dashboard"
        role="dialog"
        aria-modal="true"
        aria-labelledby="dashboard-title"
      >
        <header>
          <div>
            <small>حساب کاربری</small>
            <h2 id="dashboard-title">
              {user.role === "admin"
                ? "پنل مدیریت بورس‌نگار"
                : "پنل کاربری بورس‌نگار"}
            </h2>
          </div>
          <button className="icon-button" onClick={onClose} aria-label="بستن">
            <X />
          </button>
        </header>
        <div className="dashboard-layout">
          <nav aria-label="بخش‌های پنل">
            {(
              [
                ["overview", Gauge, "نمای کلی"],
                ["history", History, "تاریخچه تحلیل"],
                ["payments", CreditCard, "خرید و پرداخت"],
                ["referrals", Users, "معرفی دوستان"],
                ["alerts", Bell, "هشدارها"],
                ...(user.role === "admin" ? [["admin", Shield, "مدیریت"]] : []),
              ] as [Tab, any, string][]
            ).map(([id, Icon, label]) => (
              <button
                className={tab === id ? "active" : ""}
                onClick={() => setTab(id)}
                key={id}
              >
                <Icon />
                {label}
              </button>
            ))}
          </nav>
          <main>
            {busy ? (
              <DashboardSkeleton />
            ) : error ? (
              <div className="dashboard-error" role="alert">
                {error}
                <button onClick={() => load()}>تلاش دوباره</button>
              </div>
            ) : (
              <TabContent
                tab={tab}
                data={data}
                reload={() => load()}
                onCredits={onCredits}
              />
            )}
          </main>
        </div>
      </section>
    </div>
  );
}

function DashboardSkeleton() {
  return (
    <div className="dashboard-skeleton" aria-label="در حال بارگذاری">
      <i />
      <i />
      <i />
    </div>
  );
}
function TabContent({
  tab,
  data,
  reload,
  onCredits,
}: {
  tab: Tab;
  data: any;
  reload: () => void;
  onCredits: (n: number) => void;
}) {
  if (tab === "overview") {
    const d = data as Overview;
    return (
      <>
        <div className="dashboard-cards">
          <article>
            <small>اعتبار تحلیل</small>
            <strong>{Number(d.credits || 0).toLocaleString("fa-IR")}</strong>
            <span>تحلیل باقی‌مانده</span>
          </article>
          <article>
            <small>اشتراک</small>
            <strong>{d.subscription?.title_fa || "رایگان"}</strong>
            <span>
              {d.subscription?.ends_at
                ? new Date(d.subscription.ends_at).toLocaleDateString("fa-IR")
                : "بدون تاریخ پایان"}
            </span>
          </article>
          <article>
            <small>پرداخت‌های ثبت‌شده</small>
            <strong>{d.payments?.length || 0}</strong>
            <span>آخرین ۳۰ مورد</span>
          </article>
        </div>
        <section className="dashboard-section">
          <h3>کد معرفی اختصاصی</h3>
          <code>{d.referralCode || "—"}</code>
          <p>
            پس از اولین خرید تأییدشده دوست شما، پاداش به‌صورت خودکار در دفتر
            اعتبار ثبت می‌شود.
          </p>
        </section>
      </>
    );
  }
  if (tab === "history")
    return (
      <List
        items={data.analyses}
        empty="هنوز تحلیلی ثبت نشده است."
        render={(x: any) => (
          <>
            <b>{x.symbol}</b>
            <span>
              {new Date(x.created_at).toLocaleString("fa-IR")} ·{" "}
              {x.report_mode === "audited" ? "حسابرسی‌شده" : "آخرین کدال"}
            </span>
          </>
        )}
      />
    );
  if (tab === "referrals")
    return (
      <List
        items={data.referrals}
        empty="هنوز کسی با کد شما ثبت‌نام نکرده است."
        render={(x: any) => (
          <>
            <b>{x.mobile_e164}</b>
            <span>
              {statusFa(x.status)} ·{" "}
              {new Date(x.created_at).toLocaleDateString("fa-IR")}
            </span>
          </>
        )}
      />
    );
  if (tab === "alerts") return <Alerts data={data} reload={reload} />;
  if (tab === "payments")
    return <Plans plans={data.plans || []} campaigns={data.campaigns || []} />;
  return <AdminPanel />;
}
function List({
  items = [],
  empty,
  render,
}: {
  items: any[];
  empty: string;
  render: (x: any) => any;
}) {
  return (
    <section className="dashboard-section">
      <h3>سوابق</h3>
      {items.length ? (
        <div className="dashboard-list">
          {items.map((x) => (
            <article key={x.id}>{render(x)}</article>
          ))}
        </div>
      ) : (
        <div className="empty-state">{empty}</div>
      )}
    </section>
  );
}
const statusFa = (s: string) =>
  ({
    pending: "در انتظار",
    approved: "تأییدشده",
    rejected: "ردشده",
    rewarded: "پاداش‌داده‌شده",
  })[s] || s;
function Plans({ plans, campaigns }: { plans: any[]; campaigns: any[] }) {
  const [selected, setSelected] = useState<any>(null);
  const offers = [
    ...plans.map((p) => ({ ...p, offerType: "plan" })),
    ...campaigns.map((c) => ({
      ...c,
      offerType: "campaign",
      analysis_credits: c.credit_amount,
      duration_days: 0,
    })),
  ];
  return (
    <section className="dashboard-section">
      <h3>پلن‌های فعال</h3>
      <div className="plan-grid">
        {offers.map((p) => (
          <article key={p.id}>
            <b>{p.title_fa}</b>
            <strong>
              {Number(p.price_toman).toLocaleString("fa-IR")} تومان
            </strong>
            <span>
              {p.analysis_credits.toLocaleString("fa-IR")} اعتبار ·{" "}
              {p.duration_days.toLocaleString("fa-IR")} روز
            </span>
            <button
              className="button primary"
              disabled={!Number(p.price_toman)}
              onClick={() => setSelected(p)}
            >
              ثبت پرداخت
            </button>
          </article>
        ))}
      </div>
      {selected && (
        <PaymentForm plan={selected} done={() => setSelected(null)} />
      )}
    </section>
  );
}
function PaymentForm({ plan, done }: { plan: any; done: () => void }) {
  const [settings, setSettings] = useState<any>(null);
  const [tracking, setTracking] = useState("");
  const [paidAt, setPaidAt] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [message, setMessage] = useState("");
  useEffect(() => {
    api<any>("/api/public/settings").then((r) => setSettings(r.settings));
  }, []);
  async function submit(e: FormEvent) {
    e.preventDefault();
    if (!file) return;
    const body = new FormData();
    body.set(plan.offerType === "campaign" ? "campaignId" : "planId", plan.id);
    body.set("amountToman", String(plan.price_toman));
    body.set("trackingNumber", tracking);
    body.set("paidAt", new Date(paidAt).toISOString());
    body.set("receipt", file);
    await api("/api/payments", { method: "POST", body });
    setMessage("رسید با موفقیت ثبت شد و در انتظار بررسی مدیر است.");
  }
  return (
    <form className="payment-form" onSubmit={submit}>
      <h3>پرداخت کارت‌به‌کارت · {plan.title_fa}</h3>
      {settings?.payment_card_number ? (
        <p>
          شماره کارت: <b dir="ltr">{settings.payment_card_number}</b>
          <br />
          به نام: {settings.payment_card_holder || "—"}
        </p>
      ) : (
        <div className="empty-state">
          اطلاعات کارت هنوز توسط مدیر ثبت نشده است؛ ثبت رسید موقتاً ممکن نیست.
        </div>
      )}
      <label>
        شماره پیگیری
        <input
          value={tracking}
          onChange={(e) => setTracking(e.target.value)}
          minLength={4}
          maxLength={80}
          required
        />
      </label>
      <label>
        تاریخ و ساعت پرداخت
        <input
          type="datetime-local"
          value={paidAt}
          onChange={(e) => setPaidAt(e.target.value)}
          required
        />
      </label>
      <label>
        تصویر یا PDF رسید
        <input
          type="file"
          accept="image/jpeg,image/png,application/pdf"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
          required
        />
      </label>
      <small>حداکثر ۴ مگابایت؛ فقط JPG، PNG یا PDF واقعی.</small>
      {message && <div className="empty-state">{message}</div>}
      <div>
        <button
          className="button primary"
          disabled={!settings?.payment_card_number}
        >
          ارسال برای بررسی
        </button>
        <button type="button" className="button ghost" onClick={done}>
          بستن
        </button>
      </div>
    </form>
  );
}
function Alerts({ data, reload }: { data: any; reload: () => void }) {
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState<any>(null);
  async function toggle(a: any) {
    await api(`/api/alerts/${a.id}`, {
      method: "PATCH",
      body: JSON.stringify({ active: !a.active }),
    });
    reload();
  }
  async function remove(id: string) {
    await api(`/api/alerts/${id}`, { method: "DELETE" });
    reload();
  }
  return (
    <section className="dashboard-section">
      <div className="section-row">
        <h3>هشدارهای من</h3>
        <button
          className="button primary"
          onClick={() => {
            setEditing(null);
            setOpen(!open);
          }}
        >
          هشدار جدید
        </button>
      </div>
      {open && (
        <AlertForm
          initial={editing}
          done={() => {
            setOpen(false);
            setEditing(null);
            reload();
          }}
        />
      )}
      <div className="dashboard-list">
        {(data.alerts || []).map((a: any) => (
          <article key={a.id}>
            <b>
              {a.symbol} ·{" "}
              {a.kind === "price"
                ? "قیمت"
                : a.kind === "pe"
                  ? "P/E"
                  : "اطلاعیه کدال"}
            </b>
            <span>
              {a.target_value
                ? `${a.comparator === "gte" ? "بیشتر یا مساوی" : "کمتر یا مساوی"} ${a.target_value}`
                : "هر اطلاعیه جدید"}
            </span>
            <div>
              <button
                onClick={() => {
                  setEditing(a);
                  setOpen(true);
                }}
              >
                ویرایش
              </button>
              <button onClick={() => toggle(a)}>
                {a.active ? "غیرفعال‌کردن" : "فعال‌کردن"}
              </button>
              <button onClick={() => remove(a.id)}>حذف</button>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
function AlertForm({ done, initial }: { done: () => void; initial?: any }) {
  const [symbol, setSymbol] = useState(initial?.symbol || "");
  const [kind, setKind] = useState(initial?.kind || "price");
  const [comparator, setComparator] = useState(initial?.comparator || "gte");
  const [target, setTarget] = useState(
    initial?.target_value == null ? "" : String(initial.target_value),
  );
  async function submit(e: FormEvent) {
    e.preventDefault();
    await api(initial ? `/api/alerts/${initial.id}` : "/api/alerts", {
      method: initial ? "PATCH" : "POST",
      body: JSON.stringify({
        symbol,
        kind,
        ...(kind === "codal" ? {} : { comparator }),
        ...(kind === "codal" ? {} : { targetValue: Number(target) }),
      }),
    });
    done();
  }
  return (
    <form className="inline-form" onSubmit={submit}>
      <input
        aria-label="نماد"
        placeholder="نماد"
        value={symbol}
        onChange={(e) => setSymbol(e.target.value)}
        required
      />
      <select
        aria-label="نوع هشدار"
        value={kind}
        onChange={(e) => setKind(e.target.value)}
      >
        <option value="price">قیمت</option>
        <option value="pe">P/E</option>
        <option value="codal">اطلاعیه کدال</option>
      </select>
      {kind !== "codal" && (
        <>
          <select
            aria-label="شرط هشدار"
            value={comparator}
            onChange={(e) => setComparator(e.target.value)}
          >
            <option value="gte">بیشتر یا مساوی</option>
            <option value="lte">کمتر یا مساوی</option>
          </select>
          <input
            aria-label="مقدار هدف"
            type="number"
            min="0.01"
            step="0.01"
            value={target}
            onChange={(e) => setTarget(e.target.value)}
            required
          />
        </>
      )}
      <button>{initial ? "ذخیره تغییرات" : "ثبت"}</button>
    </form>
  );
}
function AdminPanel() {
  const [section, setSection] = useState("stats");
  const [data, setData] = useState<any>(null);
  const load = () =>
    api(
      section === "stats"
        ? "/api/admin/stats"
        : section === "users"
          ? "/api/admin/users"
          : section === "payments"
            ? "/api/admin/payments"
            : section === "plans"
              ? "/api/admin/plans"
              : section === "campaigns"
                ? "/api/admin/campaigns"
                : section === "referrals"
                  ? "/api/admin/referrals"
                  : section === "settings"
                    ? "/api/admin/settings"
                    : section === "sms"
                      ? "/api/admin/sms"
                      : "/api/admin/audit",
    ).then(setData);
  useEffect(() => {
    setData(null);
    load();
  }, [section]);
  return (
    <section className="dashboard-section">
      <div className="admin-tabs">
        {[
          ["stats", Gauge, "آمار"],
          ["users", Users, "کاربران"],
          ["payments", CreditCard, "پرداخت‌ها"],
          ["plans", CreditCard, "پلن‌ها"],
          ["campaigns", Megaphone, "کمپین‌ها"],
          ["referrals", Users, "معرفی‌ها"],
          ["settings", Settings, "تنظیمات"],
          ["sms", Bell, "پیامک"],
          ["audit", Shield, "ممیزی"],
        ].map(([id, Icon, label]: any) => (
          <button
            className={section === id ? "active" : ""}
            onClick={() => setSection(id)}
            key={id}
          >
            <Icon />
            {label}
          </button>
        ))}
      </div>
      {data ? (
        <AdminContent section={section} data={data} reload={load} />
      ) : (
        <DashboardSkeleton />
      )}
    </section>
  );
}
function AdminContent({
  section,
  data,
  reload,
}: {
  section: string;
  data: any;
  reload: () => void;
}) {
  if (section === "stats")
    return (
      <div className="dashboard-cards">
        {Object.entries(data.stats || {}).map(([k, v]) => (
          <article key={k}>
            <small>
              {(
                {
                  users: "کاربران",
                  registrations_30d: "ثبت‌نام ۳۰ روز اخیر",
                  active_users_30d: "کاربران فعال ۳۰ روز اخیر",
                  successful_analyses: "تحلیل‌های موفق",
                  failed_analyses: "تحلیل‌های ناموفق",
                  pending_payments: "پرداخت در انتظار",
                  revenue_toman: "درآمد تأییدشده",
                  credits_consumed: "اعتبار مصرف‌شده",
                } as any
              )[k] || k}
            </small>
            <strong>{Number(v).toLocaleString("fa-IR")}</strong>
          </article>
        ))}
      </div>
    );
  if (section === "payments")
    return (
      <div className="dashboard-list">
        {(data.payments || []).map((p: any) => (
          <article key={p.id}>
            <span>
              <b>{p.mobile_e164}</b>
              <br />
              {Number(p.amount_toman).toLocaleString("fa-IR")} تومان ·{" "}
              {p.tracking_number} · {p.plan_code || p.campaign_code}
            </span>
            <div>
              <a
                className="button ghost"
                href={`/api/admin/payments/${p.id}/receipt`}
                target="_blank"
                rel="noreferrer"
              >
                رسید
              </a>
              <button
                onClick={async () => {
                  await api(`/api/admin/payments/${p.id}/decision`, {
                    method: "POST",
                    body: JSON.stringify({ decision: "approved" }),
                  });
                  reload();
                }}
              >
                تأیید
              </button>
              <button
                onClick={async () => {
                  await api(`/api/admin/payments/${p.id}/decision`, {
                    method: "POST",
                    body: JSON.stringify({ decision: "rejected" }),
                  });
                  reload();
                }}
              >
                رد
              </button>
            </div>
          </article>
        ))}
      </div>
    );
  if (section === "users")
    return <AdminUsers initial={data.users || []} reload={reload} />;
  if (section === "plans")
    return (
      <div className="dashboard-list">
        {(data.plans || []).map((p: any) => (
          <PlanEditor plan={p} reload={reload} />
        ))}
      </div>
    );
  if (section === "campaigns")
    return (
      <>
        <CampaignCreator reload={reload} />
        <div className="dashboard-list">
          {(data.campaigns || []).map((c: any) => (
            <article key={c.id}>
              <span>
                <b>{c.title_fa}</b>
                <br />
                {c.code} · {c.credit_amount} اعتبار ·{" "}
                {c.active ? "فعال" : "متوقف"}
              </span>
              <button
                onClick={async () => {
                  await api(`/api/admin/campaigns/${c.id}/status`, {
                    method: "PATCH",
                    body: JSON.stringify({ active: !c.active }),
                  });
                  reload();
                }}
              >
                {c.active ? "توقف" : "فعال‌سازی"}
              </button>
            </article>
          ))}
        </div>
      </>
    );
  if (section === "settings")
    return (
      <>
        <SettingEditor reload={reload} />
        <div className="dashboard-list">
          {(data.settings || []).map((s: any) => (
            <article key={s.key}>
              <span>
                <b>{s.key}</b>
                <br />
                {JSON.stringify(s.value)}
              </span>
            </article>
          ))}
        </div>
      </>
    );
  if (section === "referrals")
    return (
      <div className="dashboard-list">
        {(data.referrals || []).map((r: any) => (
          <article key={r.id}>
            <span>
              <b>{r.referrer_mobile}</b> ← {r.referred_mobile}
              <br />
              {r.status} · {new Date(r.created_at).toLocaleString("fa-IR")}
            </span>
          </article>
        ))}
      </div>
    );
  if (section === "sms")
    return (
      <>
        <div className="empty-state">
          ارسال: {data.sendingEnabled ? "فعال" : "غیرفعال"} · OTP:{" "}
          {data.otpPending ? "در انتظار تأیید" : "آماده"}
        </div>
        <div className="dashboard-list">
          {(data.attempts || []).map((x: any) => (
            <article key={x.id}>
              <span>
                {x.mobile_masked} · {x.purpose} · {x.status}
              </span>
            </article>
          ))}
        </div>
      </>
    );
  return (
    <div className="dashboard-list">
      {(data.logs || []).map((x: any) => (
        <article key={x.id}>
          <span>
            <b>{x.action}</b>
            <br />
            {x.target_type} · {new Date(x.created_at).toLocaleString("fa-IR")}
          </span>
        </article>
      ))}
    </div>
  );
}
function AdminUsers({
  initial,
  reload,
}: {
  initial: any[];
  reload: () => void;
}) {
  const [users, setUsers] = useState(initial);
  const [query, setQuery] = useState("");
  const [activity, setActivity] = useState<Record<string, any>>({});
  async function search(e: FormEvent) {
    e.preventDefault();
    const result: any = await api(
      `/api/admin/users?q=${encodeURIComponent(query)}`,
    );
    setUsers(result.users || []);
  }
  async function updateUser(id: string, values: any) {
    await api(`/api/admin/users/${id}`, {
      method: "PATCH",
      body: JSON.stringify(values),
    });
    const result: any = await api(
      `/api/admin/users?q=${encodeURIComponent(query)}`,
    );
    setUsers(result.users || []);
  }
  async function adjustCredits(id: string) {
    const raw = window.prompt("مقدار تغییر اعتبار (مثبت یا منفی)");
    if (raw == null) return;
    const delta = Number(raw);
    const note = window.prompt("دلیل تغییر اعتبار (حداقل ۳ حرف)");
    if (!Number.isInteger(delta) || delta === 0 || !note || note.length < 3)
      return;
    await api(`/api/admin/users/${id}/credits`, {
      method: "POST",
      body: JSON.stringify({ delta, note }),
    });
    reload();
  }
  async function showActivity(id: string) {
    if (activity[id]) {
      setActivity((old) => ({ ...old, [id]: null }));
      return;
    }
    const result = await api(`/api/admin/users/${id}/activity`);
    setActivity((old) => ({ ...old, [id]: result }));
  }
  return (
    <>
      <form className="inline-form" onSubmit={search}>
        <input
          aria-label="جستجوی شماره موبایل"
          placeholder="جستجوی شماره موبایل"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button>جستجو</button>
      </form>
      <div className="dashboard-list">
        {users.map((u: any) => (
          <article key={u.id}>
            <span>
              <b>{u.mobile_e164}</b>
              <br />
              {u.role} · {u.credits} اعتبار · {u.status}
              {activity[u.id] && (
                <small>
                  <br />
                  دفتر اعتبار: {activity[u.id].ledger.length} · تحلیل‌ها:{" "}
                  {activity[u.id].analyses.length} · تلاش‌ها:{" "}
                  {activity[u.id].attempts.length} · اشتراک‌ها:{" "}
                  {activity[u.id].subscriptions.length}
                </small>
              )}
            </span>
            <div>
              <select
                aria-label="وضعیت کاربر"
                value={u.status}
                onChange={(e) => updateUser(u.id, { status: e.target.value })}
              >
                <option value="active">فعال</option>
                <option value="suspended">تعلیق</option>
              </select>
              <select
                aria-label="نقش کاربر"
                value={u.role}
                onChange={(e) => updateUser(u.id, { role: e.target.value })}
              >
                <option value="user">کاربر</option>
                <option value="admin">مدیر</option>
              </select>
              <button onClick={() => adjustCredits(u.id)}>تغییر اعتبار</button>
              <button onClick={() => showActivity(u.id)}>فعالیت</button>
            </div>
          </article>
        ))}
      </div>
    </>
  );
}
function PlanEditor({ plan, reload }: { plan: any; reload: () => void }) {
  const [title, setTitle] = useState(plan.title_fa);
  const [duration, setDuration] = useState(String(plan.duration_days));
  const [price, setPrice] = useState(String(plan.price_toman));
  const [credits, setCredits] = useState(String(plan.analysis_credits));
  const [active, setActive] = useState(Boolean(plan.active));
  return (
    <article>
      <span>
        <b>{plan.title_fa}</b>
        <br />
        {plan.code}
      </span>
      <div>
        <input
          aria-label="عنوان پلن"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
        />
        <input
          aria-label="مدت پلن"
          type="number"
          min="0"
          value={duration}
          onChange={(e) => setDuration(e.target.value)}
        />
        <input
          aria-label="قیمت پلن"
          type="number"
          min="0"
          value={price}
          onChange={(e) => setPrice(e.target.value)}
        />
        <input
          aria-label="اعتبار پلن"
          type="number"
          min="0"
          value={credits}
          onChange={(e) => setCredits(e.target.value)}
        />
        <button
          onClick={async () => {
            await api(`/api/admin/plans/${plan.id}`, {
              method: "PATCH",
              body: JSON.stringify({
                titleFa: title,
                durationDays: Number(duration),
                priceToman: Number(price),
                analysisCredits: Number(credits),
                active,
              }),
            });
            reload();
          }}
        >
          ذخیره
        </button>
        <label>
          <input
            type="checkbox"
            checked={active}
            onChange={(e) => setActive(e.target.checked)}
          />
          فعال
        </label>
      </div>
    </article>
  );
}
function CampaignCreator({ reload }: { reload: () => void }) {
  const [code, setCode] = useState("");
  const [title, setTitle] = useState("");
  const [price, setPrice] = useState("");
  const [credits, setCredits] = useState("");
  const [startsAt, setStartsAt] = useState(() =>
    new Date().toISOString().slice(0, 16),
  );
  const [endsAt, setEndsAt] = useState(() =>
    new Date(Date.now() + 30 * 86400000).toISOString().slice(0, 16),
  );
  const [capacity, setCapacity] = useState("");
  const [audience, setAudience] = useState("all");
  const [perUser, setPerUser] = useState("1");
  async function submit(e: FormEvent) {
    e.preventDefault();
    await api("/api/admin/campaigns", {
      method: "POST",
      body: JSON.stringify({
        code: code.toUpperCase(),
        titleFa: title,
        startsAt: new Date(startsAt).toISOString(),
        endsAt: new Date(endsAt).toISOString(),
        capacity: capacity ? Number(capacity) : null,
        creditAmount: Number(credits),
        priceToman: Number(price),
        active: false,
        rules: { audience, perUser: Number(perUser) },
      }),
    });
    reload();
  }
  return (
    <form className="inline-form" onSubmit={submit}>
      <input
        placeholder="کد کمپین"
        value={code}
        onChange={(e) => setCode(e.target.value)}
        required
      />
      <label>
        شروع
        <input
          type="datetime-local"
          value={startsAt}
          onChange={(e) => setStartsAt(e.target.value)}
          required
        />
      </label>
      <label>
        پایان
        <input
          type="datetime-local"
          value={endsAt}
          onChange={(e) => setEndsAt(e.target.value)}
          required
        />
      </label>
      <input
        type="number"
        min="1"
        placeholder="ظرفیت (اختیاری)"
        value={capacity}
        onChange={(e) => setCapacity(e.target.value)}
      />
      <select
        aria-label="مخاطبان کمپین"
        value={audience}
        onChange={(e) => setAudience(e.target.value)}
      >
        <option value="all">همه کاربران</option>
        <option value="new_users">کاربران جدید</option>
        <option value="existing_users">کاربران فعلی</option>
      </select>
      <input
        type="number"
        min="1"
        max="1"
        placeholder="سقف هر کاربر"
        value={perUser}
        onChange={(e) => setPerUser(e.target.value)}
        required
      />
      <input
        placeholder="عنوان"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        required
      />
      <input
        type="number"
        min="0"
        placeholder="قیمت"
        value={price}
        onChange={(e) => setPrice(e.target.value)}
        required
      />
      <input
        type="number"
        min="0"
        placeholder="اعتبار"
        value={credits}
        onChange={(e) => setCredits(e.target.value)}
        required
      />
      <button>ساخت غیرفعال</button>
    </form>
  );
}
function SettingEditor({ reload }: { reload: () => void }) {
  const [key, setKey] = useState("");
  const [value, setValue] = useState("");
  const [isPublic, setPublic] = useState(false);
  async function submit(e: FormEvent) {
    e.preventDefault();
    let parsed: any = value;
    try {
      parsed = JSON.parse(value);
    } catch {}
    await api(`/api/admin/settings/${key}`, {
      method: "PUT",
      body: JSON.stringify({ value: parsed, isPublic }),
    });
    reload();
  }
  return (
    <form className="inline-form" onSubmit={submit}>
      <input
        placeholder="کلید تنظیم"
        value={key}
        onChange={(e) => setKey(e.target.value)}
        required
      />
      <input
        placeholder="مقدار یا JSON"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        required
      />
      <label>
        <input
          type="checkbox"
          checked={isPublic}
          onChange={(e) => setPublic(e.target.checked)}
        />{" "}
        عمومی
      </label>
      <button>ذخیره</button>
    </form>
  );
}
