import AuthProvider from "./context/AuthProvider";
import { useAuth } from "./context/useAuth";
import LoginPage from "./pages/LoginPage";

function AppContent() {
  const { user } = useAuth();

  if (!user) return <LoginPage />;

  return (
    <div className="min-h-screen bg-[#F8FAFC] flex items-center justify-center">
      <p className="text-gray-600">
        Logged in as <strong>{user.username}</strong> ({user.role}) — dashboard coming next.
      </p>
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