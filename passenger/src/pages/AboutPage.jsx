import { useLanguage } from "../context/useLanguage";

export default function AboutPage() {
  const { t } = useLanguage();
  return (
    <div className="max-w-md">
      <h1 className="text-xl font-semibold text-gray-800">{t.aboutTitle}</h1>
      <p className="text-sm text-gray-600 mt-3 leading-relaxed">{t.aboutBody}</p>
    </div>
  );
}