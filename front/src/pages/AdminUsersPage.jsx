import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { api } from "../api/client";

const ROLE_LABELS = { 1: "Admin", 2: "Doctor", 3: "Paciente" };

const EMPTY_FORM = { name: "", email: "", password: "", role_id: "3" };

export default function AdminUsersPage() {
  const { token, user: currentUser } = useAuth();

  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [busyId, setBusyId] = useState(null);

  const [showCreateForm, setShowCreateForm] = useState(false);
  const [createForm, setCreateForm] = useState(EMPTY_FORM);
  const [createError, setCreateError] = useState("");
  const [creating, setCreating] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      const data = await api.listUsers(token);
      setUsers(data);
      setError("");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  const handleRoleChange = async (userId, newRoleId) => {
    setBusyId(userId);
    try {
      await api.updateUserRole(token, userId, Number(newRoleId));
      await load();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusyId(null);
    }
  };

  const handleDelete = async (userId) => {
    if (!window.confirm("¿Eliminar este usuario? Esta acción no se puede deshacer.")) {
      return;
    }

    setBusyId(userId);
    try {
      await api.deleteUser(token, userId);
      await load();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusyId(null);
    }
  };

  const handleCreateChange = (field) => (e) =>
    setCreateForm((f) => ({ ...f, [field]: e.target.value }));

  const handleCreateSubmit = async (event) => {
    event.preventDefault();
    setCreateError("");
    setCreating(true);

    try {
      await api.createUser(token, {
        ...createForm,
        role_id: Number(createForm.role_id),
      });
      setCreateForm(EMPTY_FORM);
      setShowCreateForm(false);
      await load();
    } catch (err) {
      setCreateError(err.message || "No se pudo crear el usuario");
    } finally {
      setCreating(false);
    }
  };

  if (currentUser && currentUser.role?.name !== "admin") {
    return (
      <div className="page">
        <p className="form-error">Esta vista es solo para administradores.</p>
      </div>
    );
  }

  return (
    <div className="page">
      <header className="page-header">
        <p className="eyebrow">Administración</p>
        <h1>Usuarios</h1>
      </header>

      {error && <p className="form-error">{error}</p>}

      <div className="admin-actions-bar">
        <button
          className="btn btn-primary"
          onClick={() => setShowCreateForm((v) => !v)}
        >
          {showCreateForm ? "Cancelar" : "+ Nuevo usuario"}
        </button>
      </div>

      {showCreateForm && (
        <section className="card">
          <h2>Crear usuario</h2>
          <form onSubmit={handleCreateSubmit} className="form form-grid">
            <label className="field">
              <span>Nombre completo</span>
              <input value={createForm.name} onChange={handleCreateChange("name")} required />
            </label>

            <label className="field">
              <span>Email</span>
              <input
                type="email"
                value={createForm.email}
                onChange={handleCreateChange("email")}
                required
              />
            </label>

            <label className="field">
              <span>Contraseña</span>
              <input
                type="password"
                value={createForm.password}
                onChange={handleCreateChange("password")}
                required
                minLength={6}
              />
            </label>

            <label className="field">
              <span>Rol</span>
              <select value={createForm.role_id} onChange={handleCreateChange("role_id")}>
                {Object.entries(ROLE_LABELS).map(([id, label]) => (
                  <option key={id} value={id}>
                    {label}
                  </option>
                ))}
              </select>
            </label>

            {createError && <p className="form-error">{createError}</p>}

            <div className="form-actions">
              <button className="btn btn-primary" type="submit" disabled={creating}>
                {creating ? "Creando…" : "Crear usuario"}
              </button>
            </div>
          </form>
        </section>
      )}

      {loading ? (
        <p>Cargando…</p>
      ) : (
        <table className="admin-table">
          <thead>
            <tr>
              <th>Nombre</th>
              <th>Email</th>
              <th>Rol</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {users.map((u) => (
              <tr key={u.id}>
                <td>{u.name}</td>
                <td>{u.email}</td>
                <td>
                  <select
                    value={u.role_id}
                    disabled={busyId === u.id || u.id === currentUser?.id}
                    onChange={(e) => handleRoleChange(u.id, e.target.value)}
                  >
                    {Object.entries(ROLE_LABELS).map(([id, label]) => (
                      <option key={id} value={id}>
                        {label}
                      </option>
                    ))}
                  </select>
                </td>
                <td>
                  <button
                    className="btn btn-ghost btn-small"
                    disabled={busyId === u.id || u.id === currentUser?.id}
                    onClick={() => handleDelete(u.id)}
                  >
                    {busyId === u.id ? "…" : "Eliminar"}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <p className="card-hint">
        No podés cambiar tu propio rol ni eliminarte a vos mismo desde acá.
      </p>
    </div>
  );
}
