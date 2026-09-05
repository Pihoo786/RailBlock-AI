import { useState } from "react";
import SearchBox from "../components/SearchBox";
import StatusCard from "../components/StatusCard";
import EmptyState from "../components/EmptyState";
import { getTrainBlocks } from "../api/passengerApi";
import { useLanguage } from "../context/useLanguage";

const RECENT_KEY = "railblock_recent_searches";

export default function CheckStatusPage() {
  const { t } = useLanguage();
  const [query, setQuery] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [recent, setRecent] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem(RECENT_KEY) || "[]");
    } catch {
      return [];
    }
  });

  async function runSearch(trainNumber) {
    const trimmed = trainNumber.trim();
    if (!trimmed) return;

    setLoading(true);
    setQuery(trimmed);
    setResult(null);
    try {
      const data = await getTrainBlocks(trimmed);
      setResult(data);
      const updated = [trimmed, ...recent.filter((r) => r !== trimmed)].slice(0, 3);
      setRecent(updated);
      localStorage.setItem(RECENT_KEY, JSON.stringify(updated));
    } catch {
      setResult({ error: true });
    } finally {
      setLoading(false);
    }
  }

  const hasDisruption = result?.blocks?.length > 0;

  return (
    <section className="max-w-3xl">
      <div className="rounded-3xl bg-gradient-to-br from-blue-800 to-slate-900 p-6 text-white shadow-lg md:p-8">
        <p className="text-sm font-semibold text-blue-200">Train information</p>
        <h1 className="mt-2 text-3xl font-bold tracking-tight md:text-4xl">
          {t.checkStatusTitle}
        </h1>
        <p className="mt-2 max-w-xl text-sm leading-6 text-slate-200">
          Check passenger-visible maintenance blocks, affected sections and expected delays.
        </p>
        <SearchBox value={query} onChange={setQuery} onSearch={() => runSearch(query)} />
      </div>

      {recent.length > 0 && (
        <div className="mt-4 flex flex-wrap items-center gap-2">
          <span className="text-xs font-semibold text-slate-500">{t.recentLabel}:</span>
          {recent.map((num) => (
            <button
              key={num}
              onClick={() => runSearch(num)}
              className="rounded-full border border-slate-200 bg-white px-3 py-1 text-xs font-semibold text-slate-600 hover:border-blue-300 hover:text-blue-700"
            >
              {num}
            </button>
          ))}
        </div>
      )}

      {loading && <p className="mt-8 text-sm text-slate-500">{t.loading}</p>}
      {result?.error && <p className="mt-8 rounded-xl bg-red-50 p-4 text-sm text-red-700">{t.errorMsg}</p>}
      {result?.trainNotFound && <p className="mt-8 rounded-xl bg-slate-100 p-4 text-sm text-slate-600">{t.trainNotFound}</p>}
      {hasDisruption && (
        <div className="mt-7">
          <p className="mb-3 text-sm font-semibold text-slate-600">
            Passenger update for train {result.train_number}
          </p>
          {result.blocks.map((block, i) => (
            <StatusCard key={`${block.section}-${i}`} trainNumber={result.train_number} block={block} />
          ))}
        </div>
      )}
      {result?.blocks?.length === 0 && <EmptyState query={result.train_number} />}
    </section>
  );
}
