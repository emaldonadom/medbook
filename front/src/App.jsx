import { Routes, Route, Navigate } from "react-router-dom";
import ProtectedRoute from "./components/ProtectedRoute";
import Layout from "./components/Layout";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import ProfilePage from "./pages/ProfilePage";
import BookAppointmentPage from "./pages/BookAppointmentPage";
import CitasRouterPage from "./pages/CitasRouterPage";
import AdminUsersPage from "./pages/AdminUsersPage";
import AdminPatientsPage from "./pages/AdminPatientsPage";
import HomeRedirect from "./pages/HomeRedirect";

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />

      <Route element={<ProtectedRoute />}>
        <Route element={<Layout />}>
          <Route path="/" element={<HomeRedirect />} />
          <Route path="/perfil" element={<ProfilePage />} />
          <Route path="/agendar" element={<BookAppointmentPage />} />
          <Route path="/citas" element={<CitasRouterPage />} />
          <Route path="/usuarios" element={<AdminUsersPage />} />
          <Route path="/pacientes" element={<AdminPatientsPage />} />
        </Route>
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
