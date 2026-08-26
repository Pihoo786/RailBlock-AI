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
      <div className="flex min-h-screen bg-[#F7F9FB]">
        <Sidebar activePage={activePage} onNavigate={setActivePage} />
        <main className="flex-1 p-8">
          <ActiveComponent />
        </main>
      </div>
    </LanguageProvider>
  );
}