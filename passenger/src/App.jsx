import { useState } from "react";
import Sidebar from "./components/Sidebar";
import CheckStatusPage from "./pages/CheckStatusPage";
import AffectedTrainsPage from "./pages/AffectedTrainsPage";
import AboutPage from "./pages/AboutPage";
import LanguageProvider from "./context/LanguageProvider";

const pages = {
  status: CheckStatusPage,
  affected: AffectedTrainsPage,
  about: AboutPage,
};

export default function App() {
  const [activePage, setActivePage] = useState("status");
  const ActiveComponent = pages[activePage];

  return (
    <LanguageProvider>
      <div className="min-h-screen bg-slate-50 text-slate-900 md:flex">
        <Sidebar activePage={activePage} onNavigate={setActivePage} />
        <main className="min-w-0 flex-1">
          <header className="border-b border-slate-200 bg-white">
            <div className="mx-auto flex max-w-6xl items-center justify-between px-5 py-4 md:px-10">
              <div>
                <p className="text-xs font-bold uppercase tracking-[0.18em] text-blue-700">
                  Public passenger portal
                </p>
                <p className="mt-1 text-sm text-slate-500">
                  Clear, passenger-safe updates from RailBlock
                </p>
              </div>
              <span className="rounded-full bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-700">
                ● Service online
              </span>
            </div>
          </header>
          <div className="mx-auto max-w-6xl px-5 py-7 md:px-10 md:py-10">
            <ActiveComponent />
          </div>
        </main>
      </div>
    </LanguageProvider>
  );
}
