import { useLanguage } from "../context/LanguageContext";

export default function Sidebar({ activePage, onNavigate }) {
  const { t, lang, toggleLang } = useLanguage();

  const navItems = [
    { id: "status", label: t.navStatus, icon: "🔎" },
    { id: "affected", label: t.navAffected, icon: "🚧" },
    { id: "about", label: t.navAbout, icon: "ℹ️" },
  ];

  return (
    <aside className="w-56 bg-white border-r border-gray-200 min-h-screen p-4 flex flex-col justify-between">
      <div>
        <div className="text-lg font-semibold text-[#2C5F8A] px-2 mb-6">🚆 {t.appName}</div>
        <nav className="space-y-1">
          {navItems.map((item) => (
            <button
              key={item.id}
              onClick={() => onNavigate(item.id)}
              className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition ${
                activePage === item.id
                  ? "bg-[#2C5F8A] text-white"
                  : "text-gray-600 hover:bg-gray-100"
              }`}
            >
              <span>{item.icon}</span>
              {item.label}
            </button>
          ))}
        </nav>
      </div>

      <button
        onClick={toggleLang}
        className="text-xs font-semibold text-gray-500 border border-gray-200 rounded-lg px-3 py-2 hover:bg-gray-100"
      >
        {lang === "en" ? "हिंदी में देखें" : "View in English"}
      </button>
    </aside>
  );
}