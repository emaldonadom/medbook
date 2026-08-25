import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { api } from "../api/client";
import StatusBadge from "../components/StatusBadge";

export default function AdminAppointmentsPage() {
  const { token } = useAuth();

  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [deletingId, setDeletingId] = useState(null);

  const load = async () => {
    setLoading(true);
    try {
      const data = await api.listAppointments(token);
      setAppointments(data);
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

  const handleDelete = async (id) => {
    if (!window.confirm("¿Eliminar esta cita? Esta acción no se puede deshacer.")) {
      return;
    }

    setDeletingId(id);
    try {
      await api.deleteAppointment(token, id);
      await load();
    } catch (err) {
      setError(err.message);
    } finally {
      setDeletingId(null);
    }
  };

  const formatDate = (iso) => {
    const date = new Date(iso);
    return date.toLocaleString("es-CL", { dateStyle: "medium", timeStyle: "short" });
  };

  return (
    <div className="page">
      <header className="page-header">
        <p className="eyebrow">Administración</p>
        <h1>Todas las citas</h1>
      </header>

      {error && <p className="form-error">{error}</p>}

      {loading ? (
        <p>Cargando…</p>
      ) : appointments.length === 0 ? (
        <section className="card">
          <p>No hay citas registradas todavía.</p>
        </section>
      ) : (
        <ul className="ledger-list">
          {appointments.map((appt) => (
            <li key={appt.id} className={`ledger-row status-${appt.status}`}>
              <div className="ledger-row-time">{formatDate(appt.scheduled_at)}</div>

              <div className="ledger-row-body">
                <p className="ledger-row-reason">
                  {appt.reason}
                  <span className="ledger-row-patient">
                    {" "}
                    · Paciente: {appt.patient_name} · Doctor: {appt.doctor_name}
                  </span>
                </p>
                <StatusBadge status={appt.status} />
              </div>

              <div className="ledger-row-actions">
                <button
                  className="btn btn-ghost btn-small"
                  onClick={() => handleDelete(appt.id)}
                  disabled={deletingId === appt.id}
                >
                  {deletingId === appt.id ? "…" : "Eliminar"}
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
