export default function SearchBox({ value, onChange, onSearch }) {
  return (
    <div className="mt-6">
      <label className="text-sm text-gray-500">Enter your train number</label>
      <div className="flex gap-2 mt-2">
        <input
          type="text"
          inputMode="numeric"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && onSearch()}
          placeholder="e.g. 12627"
          className="flex-1 border border-gray-200 rounded-xl px-4 py-3 text-base focus:outline-none focus:ring-2 focus:ring-[#2C5F8A]"
        />
        <button
          onClick={onSearch}
          className="px-5 py-3 rounded-xl bg-[#2C5F8A] text-white font-semibold hover:opacity-90"
        >
          Check Status
        </button>
      </div>
    </div>
  );
}