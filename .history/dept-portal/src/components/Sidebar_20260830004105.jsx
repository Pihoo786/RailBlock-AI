import { LayoutDashboard, FilePlus, History, LogOut, TrainFront } from "lucide-react";
import { useAuth } from "../context/useAuth";

export default function Sidebar({ activePage, onNavigate }) {
  const { user, logout } = useAuth();
  const initial = user.username.charAt(0).toUpperCase();

  const navItems = [
    { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
    { id: "new-request", label: "New Request", icon: FilePlus },
    { id: "history", label: "Request History", icon: History },
  ];

  return (
    <aside className="w-60 bg-white border-r border-gray-200 min-h-screen p-4 flex flex-col justify-between">
      <div>
        <div className="flex items-center gap-2.5 px-2 mb-1">
          <div className="w-9 h-9 rounded-xl bg-[#1E3A5F] flex items-center justify-center shrink-0">
            <TrainFront size={18} className="text-white" />
          </div>
          <div>
            <div className="text-base font-extrabold text-[#1E3A5F] tracking-tight leading-tight">RailBlock</div>
            <div className="text-[11px] text-gray-400 capitalize leading-tight">{user.role} Portal</div>
          </div>
        </div>

        <nav className="space-y-1 mt-6">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <button
                key={item.id}
                onClick={() => onNavigate(item.id)}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition ${
                  activePage === item.id
                    ? "bg-[#1E3A5F] text-white shadow-sm"
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

      <div>
        <div className="flex items-center gap-2.5 px-2 py-2 mb-2 border-t border-gray-100 pt-4">
          <div className="w-8 h-8 rounded-full bg-[#2563EB]/10 text-[#1E3A5F] flex items-center justify-center text-sm font-bold shrink-0">
            {initial}
          </div>
          <div className="min-w-0">
            <p className="text-sm font-semibold text-gray-800 truncate">{user.username}</p>
            <p className="text-[11px] text-gray-400 capitalize">{user.role}</p>
          </div>
        </div>
        <button
          onClick={logout}
          className="w-full flex items-center gap-2 text-xs font-semibold text-gray-500 border border-gray-200 rounded-lg px-3 py-2 hover:bg-gray-100"
        >
          <LogOut size={14} /> Log Out
        </button>
      </div>
    </aside>
  );
}