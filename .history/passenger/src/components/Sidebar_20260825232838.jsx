const navItems = [
  { id: "status", label: "Check Status", icon: "🔎" },
  { id: "affected", label: "Affected Trains", icon: "🚧" },
  { id: "about", label: "About", icon: "ℹ️" },
];

export default function Sidebar({ activePage, onNavigate }) {
  return (
    <aside className="w-56 bg-white border-r border-gray-200 min-h-screen p-4">
      <div className="text-lg font-semibold text-[#2C5F8A] px-2 mb-6">🚆 RailBlock</div>
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
    </aside>
  );
}