import { ExternalLink, Newspaper } from "lucide-react";
import { useEffect, useState } from "react";
import { api } from "../AppProduction";

type Report = { title: string; date: string; content: string; url: string; published_at: string };

export function CodalScanReportCard() {
  const [report, setReport] = useState<Report | null>(null);
  useEffect(() => { api<{ available: boolean; report: Report | null }>("/api/sources/codalscan/latest").then((response) => setReport(response.available ? response.report : null)).catch(() => setReport(null)); }, []);
  if (!report) return null;
  const lines = report.content.split("\n").map((line) => line.trim()).filter(Boolean).slice(0, 8);
  return <section className="codalscan-card" aria-labelledby="codalscan-title"><div className="codalscan-card__head"><span className="codalscan-card__eyebrow"><Newspaper size={16}/> منبع مکمل بازار</span><span className="codalscan-card__date">{report.date}</span></div><h2 id="codalscan-title">{report.title}</h2><div className="codalscan-card__content">{lines.map((line, index) => <p key={`${line}-${index}`}>{line}</p>)}</div><div className="codalscan-card__foot"><small>این خلاصه از CodalScan است و در محاسبات بنیادی بورس‌نگار استفاده نمی‌شود.</small><a href={`https://codalscan.ir${report.url}`} target="_blank" rel="noreferrer">مشاهده منبع <ExternalLink size={14}/></a></div></section>;
}
