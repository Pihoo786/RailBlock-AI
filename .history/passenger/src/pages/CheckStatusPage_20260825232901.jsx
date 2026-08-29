import { useState } from "react";
import SearchBox from "../components/SearchBox";
import StatusCard from "../components/StatusCard";
import EmptyState from "../components/EmptyState";
import { mockBlocks } from "../data/mockBlocks";

export default function CheckStatusPage() {
  const [query, setQuery] = useState("");
  const [searched, setSearched] = useState(null);

  function handleSearch() {
    const trimmed = query.trim();
    if (!trimmed) return;
    const match = mockBlocks.find((b) => b.train_number === trimmed);
    setSearched(match || { notFound: true, query: trimmed });
  }

  return (
    <div className="max-w-md">
      <h1 className="text-xl font-semibold text-gray-800">Check Train Status</h1>
      <SearchBox value={query} onChange={setQuery} onSearch={handleSearch} />
      {searched?.notFound && <EmptyState query={searched.query} />}
      {searched && !searched.notFound && <StatusCard block={searched} />}
    </div>
  );
}