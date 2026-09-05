import { useLanguage } from "../context/useLanguage";
import { formatTime } from "../utils/formatTime";
import RouteStrip from "./RouteStrip";

const badgeStyles = {
  SCHEDULED: "bg-blue-100 text-blue-800",
  APPROVED: "bg-emerald-100 text-emerald-800",
  ACTIVE: "bg-orange-100 text-orange-800",
  COMPLETED: "bg-slate-100 text-slate-700",
  CANCELLED: "bg-red-100 text-red-800",
};

function Row({ label, value }) {
  return (
    <div className="flex items-start justify-between gap-4 border-b border-slate-100 py-3 last:border-none">
      <span className="text-sm text-slate-500">{label}</span>
      <span className="text-right text-sm font-semibold text-slate-800">{value}</span>
    </div>
  );
}

export default function StatusCard({ trainNumber, block }) {
  const { t } = useLanguage();
  return (
    <article className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">Passenger update</p>
          <p className="mt-1 text-xl font-bold text-slate-900">Train {trainNumber}</p>
        </div>
        <span className={`rounded-full px-3 py-1 text-xs font-bold ${badgeStyles[block.status] || "bg-slate-100 text-slate-700"}`}>
          {block.status}
        </span>
      </div>
      <Row label={t.rowSection} value={block.section} />
      <Row label={t.rowTime} value={`${formatTime(block.start_time)} – ${formatTime(block.end_time)}`} />
      <Row label={t.rowDelay} value={`${block.expected_delay_minutes} min`} />
      <Row label={t.rowReason} value={block.reason} />
      {block.reason_code && <Row label="Public reason code" value={block.reason_code} />}
      <RouteStrip section={block.section} />
      <p className="mt-4 text-xs text-slate-400">
        Only passenger-relevant information is shown. Internal risk, priority and optimization data are not published.
      </p>
    </article>
  );
}
