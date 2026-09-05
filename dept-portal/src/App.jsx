import { useState } from "react";
import AuthProvider from "./context/AuthProvider";
import { useAuth } from "./context/useAuth";
import LoginPage from "./pages/LoginPage";
import Sidebar from "./components/Sidebar";
import DashboardPage from "./pages/DashboardPage";
import NewRequestPage from "./pages/NewRequestPage";
import HistoryPage from "./pages/HistoryPage";
import AnalyticsPage from "./pages/AnalyticsPage";

function AppContent() {
  const { user } = useAuth();
  const [activePage, setActivePage] = useState("dashboard");
  const [refreshKey, setRefreshKey] = useState(0);

  if (!user) return <LoginPage />;

  return (
    <div className="flex min-h-screen bg-[#F8FAFC]">
      <Sidebar activePage={activePage} onNavigate={setActivePage} />
      <main className="flex-1 p-8">
        {activePage === "dashboard" && <DashboardPage refreshKey={refreshKey} />}
        {activePage === "new-request" && (
          <NewRequestPage onSubmitted={() => { setRefreshKey((k) => k + 1); setActivePage("dashboard"); }} />
        )}
        {activePage === "history" && <HistoryPage refreshKey={refreshKey} />}
        {activePage === "analytics" && <AnalyticsPage refreshKey={refreshKey} />}
      </main>
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}