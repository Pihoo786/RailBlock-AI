const badgeStyles = {
  SCHEDULED: "bg-gray-400",
  APPROVED: "bg-emerald-600",
  DELAYED: "bg-amber-500",
};

function Row({ label, value }) {
  return (
    <div className="flex justify-between py-2 border-b border-gray-100 last:border-none">
      <span className="text-sm text-gray-500">{label}</span>
      <span className="font-semibold text-gray-800">{value}</span>
    </div>
  );
}

export default function StatusCard({ block }) {
  return (
    <div className="mt-5 bg-white border border-gray-200 rounded-2xl p-5 shadow-sm">
      <Row label="Train" value={block.train_number} />
      <Row label="Section" value={block.section} />
      <Row label="Time" value={`${block.start_time} – ${block.end_time}`} />
      <Row label="Expected Delay" value={`${block.expected_delay_minutes} min`} />
      <Row label="Reason" value={block.reason} />
      <div className="flex justify-between py-2">
        <span className="text-sm text-gray-500">Status</span>
        <span className={`text-white text-xs font-semibold px-3 py-1 rounded-full ${badgeStyles[block.status] || "bg-gray-400"}`}>
          {block.status}
        </span>
      </div>
    </div>
  );
}