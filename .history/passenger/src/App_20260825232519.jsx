import { useState } from "react";
import SearchBox from "./components/SearchBox";
import StatusCard from "./components/StatusCard";
import EmptyState from "./components/EmptyState";
import { mockBlocks } from "./data/mockBlocks";

export default function App() {
  const [query, setQuery] = useState("");
  const [searched, setSearched] = useState(null); // holds the matched block or "not-found"

  function handleSearch() {
    const trimmed = query.trim();
    if (!trimmed) return;
    const match = mockBlocks.find((b) => b.train_number === trimmed);
    setSearched(match || { notFound: true, query: trimmed });
  }

  return (
    <div className="min-h-screen bg-[#F7F9FB]">
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <span className="text-lg font-semibold text-[#2C5F8A]">🚆 RailPulse</span>
      </header>

      <main className="max-w-md mx-auto px-4 py-6">
        <SearchBox value={query} onChange={setQuery} onSearch={handleSearch} />

        {searched?.notFound && <EmptyState query={searched.query} />}
        {searched && !searched.notFound && <StatusCard block={searched} />}
      </main>
    </div>
  );
}