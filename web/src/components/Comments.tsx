import { useEffect, useState } from "react";
import { Flag, MessageSquare, ThumbsUp } from "lucide-react";
import { api, type User } from "../AppProduction";

type Comment = { id:string; body:string; created_at:string; user_label:string; likes:number };
export function Comments({ kind, symbol, user, onLogin }: { kind:"site_feedback"|"symbol_comment"; symbol?:string; user:User|null; onLogin:()=>void }) {
  const [items,setItems]=useState<Comment[]>([]); const [body,setBody]=useState(""); const [notice,setNotice]=useState(""); const [error,setError]=useState("");
  const load=()=>api<{comments:Comment[]}>(`/api/comments?kind=${kind}${symbol?`&symbol=${encodeURIComponent(symbol)}`:""}`).then(r=>setItems(Array.isArray(r?.comments) ? r.comments : [])).catch(()=>setItems([]));
  useEffect(()=>{void load()},[kind,symbol]);
  async function submit(){if(!user){onLogin();return;}setError("");setNotice("");try{await api("/api/comments",{method:"POST",body:JSON.stringify({kind,symbol,body})});setBody("");setNotice("نظر شما برای بررسی ارسال شد.");void load()}catch(e){setError(e instanceof Error?e.message:"خطا در ارسال نظر")}}
  return <section className="comments-section"><header><MessageSquare/><div><span>{kind==="site_feedback"?"بازخورد کاربران":"گفت‌وگوی این نماد"}</span><h2>{kind==="site_feedback"?"نظر شما درباره بورس‌نگار":"نظر کاربران درباره این سهم"}</h2></div></header><div className="comment-form"><textarea value={body} onChange={e=>setBody(e.target.value)} maxLength={2000} placeholder={user?"نظر یا پیشنهاد خود را بنویسید…":"برای ثبت نظر ابتدا وارد شوید."}/><button onClick={submit} disabled={body.trim().length<3}>{user?"ارسال نظر":"ورود و ارسال نظر"}</button>{notice&&<small className="success-state">{notice}</small>}{error&&<small className="error-state">{error}</small>}</div><div className="comment-list">{items.map(c=><article key={c.id}><p>{c.body}</p><small>{c.user_label} · {new Date(c.created_at).toLocaleDateString("fa-IR")}</small><span><ThumbsUp/> {c.likes} <Flag/></span></article>)}{!items.length&&<p className="empty-docs">هنوز نظری منتشر نشده است.</p>}</div></section>;
}
