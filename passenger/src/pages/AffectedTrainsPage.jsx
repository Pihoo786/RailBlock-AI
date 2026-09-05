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
    <section className="max-w-3xl">
      <div>
        <p className="text-sm font-semibold text-blue-700">Live passenger view</p>
        <h1 className="mt-1 text-3xl font-bold tracking-tight text-slate-900">{t.affectedTitle}</h1>
        <p className="mt-2 text-sm leading-6 text-slate-500">{t.affectedSub}</p>
      </div>
      {loading && <p className="mt-8 text-sm text-slate-500">{t.loading}</p>}
      {error && <p className="mt-8 rounded-xl bg-red-50 p-4 text-sm text-red-700">{t.errorMsg}</p>}
      {!loading && !error && blocks.length === 0 && (
        <div className="mt-8 rounded-2xl border border-dashed border-slate-300 bg-white p-8 text-center">
          <p className="font-semibold text-slate-800">No affected trains right now</p>
          <p className="mt-1 text-sm text-slate-500">Normal service information is currently available.</p>
        </div>
      )}
      <div className="mt-5 grid gap-4 md:grid-cols-2">
        {blocks.map((item, index) => (
          <StatusCard
            key={`${item.train_number}-${item.section}-${index}`}
            trainNumber={item.train_number}
            block={item}
          />
        ))}
      </div>
    </section>
  );
}
