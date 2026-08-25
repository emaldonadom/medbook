import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const SUPPORTED_ROLES = ["patient", "doctor", "admin"];

export default function Layout() {
  const { user, logout } = useAuth();
  const role = user?.role?.name;

  if (user && !SUPPORTED_ROLES.includes(role)) {
    return (
      <div className="role-gate">
        <div className="role-gate-card">
          <p className="eyebrow">Acceso restringido</p>
          <h1>Todavía no hay panel para tu rol</h1>
          <p>
            Iniciaste sesión como <strong>{user.name}</strong>, con rol{" "}
            <strong>{role}</strong>. Este frontend no tiene un panel para
            ese rol.
          </p>
          <button className="btn btn-secondary" onClick={logout}>
            Cerrar sesión
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-mark">MB</span>
          <span className="brand-name">MedBook</span>
        </div>

        <nav className="nav">
          {role === "patient" && (
            <>
              <NavLink to="/perfil" className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}>
                Mi perfil
              </NavLink>
              <NavLink to="/agendar" className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}>
                Agendar cita
              </NavLink>
            </>
          )}
          {role === "admin" && (
            <NavLink to="/usuarios" className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}>
              Usuarios
            </NavLink>
          )}
          {(role === "admin" || role === "doctor") && (
            <NavLink to="/pacientes" className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}>
              Pacientes
            </NavLink>
          )}
          <NavLink to="/citas" className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}>
            {role === "admin" ? "Todas las citas" : "Mis citas"}
          </NavLink>
        </nav>

        <div className="sidebar-footer">
          <div className="user-chip">
            <span className="user-name">{user?.name}</span>
            <span className="user-email">{user?.email}</span>
          </div>
          <button className="btn btn-ghost" onClick={logout}>
            Cerrar sesión
          </button>
        </div>
      </aside>

      <main className="content">
        <Outlet />
      </main>
    </div>
  );
}
