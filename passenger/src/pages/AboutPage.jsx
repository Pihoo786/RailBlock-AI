import { useLanguage } from "../context/useLanguage";

export default function AboutPage() {
  const { t } = useLanguage();
  return (
    <section className="max-w-3xl">
      <p className="text-sm font-semibold text-blue-700">Privacy by design</p>
      <h1 className="mt-1 text-3xl font-bold tracking-tight text-slate-900">{t.aboutTitle}</h1>
      <p className="mt-4 rounded-2xl border border-slate-200 bg-white p-6 text-sm leading-7 text-slate-600 shadow-sm">
        {t.aboutBody}
      </p>
      <div className="mt-5 grid gap-4 md:grid-cols-3">
        {[
          ["Public status", "Scheduled, approved and active passenger updates."],
          ["Sanitized data", "Risk scores, penalties, asset IDs and internal notes stay private."],
          ["Stable codes", "Public reason codes keep explanations consistent across the portal."],
        ].map(([title, body]) => (
          <div key={title} className="rounded-2xl border border-slate-200 bg-white p-5">
            <h2 className="font-bold text-slate-800">{title}</h2>
            <p className="mt-2 text-sm leading-6 text-slate-500">{body}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
