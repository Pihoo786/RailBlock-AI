import { useLanguage } from "../context/LanguageContext";

export default function EmptyState({ query }) {
  const { t } = useLanguage();
  return (
    <p className="text-center text-gray-500 text-sm mt-10">
      {t.notFound(query)}
    </p>
  );
}