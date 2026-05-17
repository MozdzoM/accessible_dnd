import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import { GuestRoute, ProtectedRoute } from "../components/ProtectedRoute";
import { AuthProvider } from "../contexts/AuthContext";

function NotFoundPage() {
  return <div className="card">Not found.</div>;
}

export function App() {
  return (
    <AuthProvider>
        <BrowserRouter>
            <Routes>
                <Route element={<GuestRoute />}>
                    {/* Add routes for guests */}
                </Route>

                <Route element={<ProtectedRoute />}>
                    {/* Add routes for logged users */}
                </Route>

                <Route path="*" element={<NotFoundPage />} />
                <Route path="/home" element={<Navigate to="/" replace />} />
            </Routes>
        </BrowserRouter>
    </AuthProvider>
  );
}

