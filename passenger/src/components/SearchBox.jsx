import { useLanguage } from "../context/useLanguage";

export default function SearchBox({ value, onChange, onSearch }) {
  const { t } = useLanguage();
  return (
    <div className="mt-6">
      <label className="text-xs font-semibold uppercase tracking-wide text-blue-100">
        {t.searchLabel}
      </label>
      <div className="mt-2 flex flex-col gap-2 sm:flex-row">
        <input
          type="text"
          inputMode="numeric"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && onSearch()}
          placeholder={t.searchPlaceholder}
          aria-label={t.searchLabel}
          className="min-w-0 flex-1 rounded-xl border border-white/20 bg-white px-4 py-3 text-base text-slate-900 outline-none focus:ring-2 focus:ring-blue-300"
        />
        <button
          onClick={onSearch}
          className="rounded-xl bg-white px-5 py-3 font-bold text-blue-800 shadow-sm hover:bg-blue-50"
        >
          {t.searchBtn}
        </button>
      </div>
    </div>
  );
}
