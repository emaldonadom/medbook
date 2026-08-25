import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { api } from "../api/client";

export default function AdminPatientsPage() {
  const { token, user: currentUser } = useAuth();
  const isAdmin = currentUser?.role?.name === "admin";
  const isDoctor = currentUser?.role?.name === "doctor";

  const [patients, setPatients] = useState([]);
  const [userMap, setUserMap] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [editingId, setEditingId] = useState(null);
  const [editForm, setEditForm] = useState({ date_of_birth: "", phone: "", address: "" });
  const [savingId, setSavingId] = useState(null);
  const [deletingId, setDeletingId] = useState(null);

  const load = async () => {
    setLoading(true);
    try {
      // Patient no trae el nombre/email (eso vive en User), así que
      // pedimos ambas listas y las cruzamos por user_id acá en el frontend.
      const [patientsList, usersList] = await Promise.all([
        api.listPatients(token),
        api.listUsers(token).catch(() => []), // un doctor no tiene permiso para listar users; no rompe la página por eso
      ]);

      setPatients(patientsList);

      const map = {};
      usersList.forEach((u) => {
        map[u.id] = u;
      });
      setUserMap(map);
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

  const startEdit = (patient) => {
    setEditingId(patient.id);
    setEditForm({
      date_of_birth: patient.date_of_birth,
      phone: patient.phone,
      address: patient.address,
    });
  };

  const handleEditChange = (field) => (e) =>
    setEditForm((f) => ({ ...f, [field]: e.target.value }));

  const handleSave = async (patientId) => {
    setSavingId(patientId);
    try {
      await api.updatePatientProfile(token, patientId, editForm);
      setEditingId(null);
      await load();
    } catch (err) {
      setError(err.message);
    } finally {
      setSavingId(null);
    }
  };

  const handleDelete = async (patientId) => {
    if (!window.confirm("¿Eliminar este perfil de paciente? Esta acción no se puede deshacer.")) {
      return;
    }

    setDeletingId(patientId);
    try {
      await api.deletePatient(token, patientId);
      await load();
    } catch (err) {
      setError(err.message);
    } finally {
      setDeletingId(null);
    }
  };

  if (currentUser && !isAdmin && !isDoctor) {
    return (
      <div className="page">
        <p className="form-error">Esta vista es solo para administradores y doctores.</p>
      </div>
    );
  }

  return (
    <div className="page">
      <header className="page-header">
        <p className="eyebrow">{isAdmin ? "Administración" : "Consulta"}</p>
        <h1>Pacientes</h1>
      </header>

      {error && <p className="form-error">{error}</p>}

      {loading ? (
        <p>Cargando…</p>
      ) : patients.length === 0 ? (
        <section className="card">
          <p>Todavía no hay pacientes registrados.</p>
        </section>
      ) : (
        <table className="admin-table">
          <thead>
            <tr>
              <th>Nombre</th>
              <th>Contacto</th>
              <th>Fecha de nacimiento</th>
              <th>Dirección</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {patients.map((p) => {
              const owner = userMap[p.user_id];
              const isEditing = editingId === p.id;

              return (
                <tr key={p.id}>
                  <td>{owner ? owner.name : `Usuario #${p.user_id}`}</td>
                  <td>
                    {isEditing ? (
                      <input value={editForm.phone} onChange={handleEditChange("phone")} />
                    ) : (
                      <>
                        {owner && <div>{owner.email}</div>}
                        <div>{p.phone}</div>
                      </>
                    )}
                  </td>
                  <td>
                    {isEditing ? (
                      <input
                        type="date"
                        value={editForm.date_of_birth}
                        onChange={handleEditChange("date_of_birth")}
                      />
                    ) : (
                      p.date_of_birth
                    )}
                  </td>
                  <td>
                    {isEditing ? (
                      <input value={editForm.address} onChange={handleEditChange("address")} />
                    ) : (
                      p.address
                    )}
                  </td>
                  <td>
                    {isEditing ? (
                      <div className="ledger-row-actions">
                        <button
                          className="btn btn-primary btn-small"
                          onClick={() => handleSave(p.id)}
                          disabled={savingId === p.id}
                        >
                          {savingId === p.id ? "…" : "Guardar"}
                        </button>
                        <button
                          className="btn btn-ghost btn-small"
                          onClick={() => setEditingId(null)}
                        >
                          Cancelar
                        </button>
                      </div>
                    ) : (
                      <div className="ledger-row-actions">
                        <button
                          className="btn btn-secondary btn-small"
                          onClick={() => startEdit(p)}
                        >
                          Editar
                        </button>
                        {isAdmin && (
                          <button
                            className="btn btn-ghost btn-small"
                            onClick={() => handleDelete(p.id)}
                            disabled={deletingId === p.id}
                          >
                            {deletingId === p.id ? "…" : "Eliminar"}
                          </button>
                        )}
                      </div>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      )}
    </div>
  );
}
