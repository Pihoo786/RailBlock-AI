import { useLanguage } from "../context/LanguageContext";
import { formatTime } from "../utils/formatTime";
import RouteStrip from "./RouteStrip";

const badgeStyles = {
  SCHEDULED: "bg-blue-500",
  APPROVED: "bg-emerald-600",
  ACTIVE: "bg-orange-500",
  COMPLETED: "bg-gray-400",
  CANCELLED: "bg-red-500",
};

function Row({ label, value }) {
  return (
    <div className="flex justify-between py-2 border-b border-gray-100 last:border-none">
      <span className="text-sm text-gray-500">{label}</span>
      <span className="font-semibold text-gray-800">{value}</span>
    </div>
  );
}

export default function StatusCard({ trainNumber, block }) {
  const { t } = useLanguage();
  return (
    <div className="mt-5 bg-white border border-gray-200 rounded-2xl p-5 shadow-sm">
      <Row label={t.rowTrain} value={trainNumber} />
      <Row label={t.rowSection} value={block.section} />
      <Row label={t.rowTime} value={`${formatTime(block.start_time)} – ${formatTime(block.end_time)}`} />
      <Row label={t.rowDelay} value={`${block.expected_delay_minutes} min`} />
      <Row label={t.rowReason} value={block.reason} />
      <div className="flex justify-between py-2">
        <span className="text-sm text-gray-500">{t.rowStatus}</span>
        <span className={`text-white text-xs font-semibold px-3 py-1 rounded-full ${badgeStyles[block.status] || "bg-gray-400"}`}>
          {block.status}
        </span>
      </div>
      <RouteStrip section={block.section} />
    </div>
  );
}