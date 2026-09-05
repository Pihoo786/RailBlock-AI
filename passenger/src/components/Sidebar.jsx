import { useLanguage } from "../context/useLanguage";

export default function Sidebar({ activePage, onNavigate }) {
  const { t, lang, toggleLang } = useLanguage();

  const navItems = [
    { id: "status", label: t.navStatus, icon: "🔎" },
    { id: "affected", label: t.navAffected, icon: "🚧" },
    { id: "about", label: t.navAbout, icon: "ℹ️" },
  ];

  return (
    <aside className="w-full shrink-0 border-b border-slate-200 bg-white md:min-h-screen md:w-60 md:border-b-0 md:border-r">
      <div className="flex items-center justify-between p-4 md:sticky md:top-0 md:flex-col md:items-stretch md:p-5">
        <div className="text-lg font-extrabold text-blue-800">🚆 {t.appName}</div>
        <nav className="mt-0 flex gap-1 md:mt-8 md:flex-col">
          {navItems.map((item) => (
            <button
              key={item.id}
              onClick={() => onNavigate(item.id)}
              className={`flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-semibold transition md:w-full ${
                activePage === item.id
                  ? "bg-blue-800 text-white"
                  : "text-slate-600 hover:bg-slate-100"
              }`}
            >
              <span aria-hidden="true">{item.icon}</span>
              <span className="hidden sm:inline">{item.label}</span>
            </button>
          ))}
        </nav>
        <button
          onClick={toggleLang}
          className="ml-2 rounded-lg border border-slate-200 px-3 py-2 text-xs font-bold text-slate-500 hover:bg-slate-50 md:ml-0 md:mt-8"
        >
          {lang === "en" ? "हिंदी" : "English"}
        </button>
      </div>
    </aside>
  );
}
