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

  return (
    <div className="max-w-md">
      <h1 className="text-xl font-semibold text-gray-800">{t.checkStatusTitle}</h1>
      <SearchBox value={query} onChange={setQuery} onSearch={() => runSearch(query)} />

      {recent.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-2">
          <span className="text-xs text-gray-400 mr-1">{t.recentLabel}:</span>
          {recent.map((num) => (
            <button
              key={num}
              onClick={() => runSearch(num)}
              className="text-xs bg-gray-100 hover:bg-gray-200 px-2 py-1 rounded-full text-gray-600"
            >
              {num}
            </button>
          ))}
        </div>
      )}

      {loading && <p className="text-sm text-gray-400 mt-6">{t.loading}</p>}
      {result?.error && <p className="text-sm text-red-500 mt-6">{t.errorMsg}</p>}
      {result?.trainNotFound && <p className="text-sm text-gray-500 mt-6">{t.trainNotFound}</p>}
      {result?.blocks?.length === 0 && <EmptyState query={result.train_number} />}
      {result?.blocks?.map((block, i) => (
        <StatusCard key={i} trainNumber={result.train_number} block={block} />
      ))}
    </div>
  );
}