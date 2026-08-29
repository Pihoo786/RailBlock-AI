import { LayoutDashboard, FilePlus, History, LogOut } from "lucide-react";
import { useAuth } from "../context/useAuth";

export default function Sidebar({ activePage, onNavigate }) {
  const { user, logout } = useAuth();

  const navItems = [
    { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
    { id: "new-request", label: "New Request", icon: FilePlus },
    { id: "history", label: "Request History", icon: History },
  ];

  return (
    <aside className="w-56 bg-white border-r border-gray-200 min-h-screen p-4 flex flex-col justify-between">
      <div>
        <div className="mb-1 px-2">
          <div className="text-lg font-extrabold text-[#1E3A5F] tracking-tight">RailBlock</div>
          <div className="text-xs text-gray-400 capitalize">{user.role} Portal</div>
        </div>
        <nav className="space-y-1 mt-6">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <button
                key={item.id}
                onClick={() => onNavigate(item.id)}
                className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition ${
                  activePage === item.id
                    ? "bg-[#1E3A5F] text-white"
                    : "text-gray-600 hover:bg-gray-100"
                }`}
              >
                <Icon size={16} />
                {item.label}
              </button>
            );
          })}
        </nav>
      </div>

      <button
        onClick={logout}
        className="flex items-center gap-2 text-xs font-semibold text-gray-500 border border-gray-200 rounded-lg px-3 py-2 hover:bg-gray-100"
      >
        <LogOut size={14} /> Log Out
      </button>
    </aside>
  );
}