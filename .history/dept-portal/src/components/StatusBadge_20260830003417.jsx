import { STATUS_STYLES, STATUS_LABELS } from "../data/statuses";

export default function StatusBadge({ status }) {
  return (
    <span className={`text-white text-xs font-semibold px-3 py-1 rounded-full ${STATUS_STYLES[status] || "bg-gray-400"}`}>
      {STATUS_LABELS[status] || status}
    </span>
  );
}