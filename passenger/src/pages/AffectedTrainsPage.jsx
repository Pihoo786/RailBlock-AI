import { useState, useEffect } from "react";
import StatusCard from "../components/StatusCard";
import { getAllBlocks } from "../api/passengerApi";
import { useLanguage } from "../context/useLanguage";

export default function AffectedTrainsPage() {
  const { t } = useLanguage();
  const [blocks, setBlocks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    getAllBlocks()
      .then(setBlocks)
      .catch(() => setError(true))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="max-w-md">
      <h1 className="text-xl font-semibold text-gray-800">{t.affectedTitle}</h1>
      <p className="text-sm text-gray-500 mt-1">{t.affectedSub}</p>
      {loading && <p className="text-sm text-gray-400 mt-6">{t.loading}</p>}
      {error && <p className="text-sm text-red-500 mt-6">{t.errorMsg}</p>}
      {blocks.map((item) => (
        <StatusCard key={item.train_number} trainNumber={item.train_number} block={item} />
      ))}
    </div>
  );
}