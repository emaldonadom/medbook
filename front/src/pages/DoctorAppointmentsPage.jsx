import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { api } from "../api/client";
import StatusBadge from "../components/StatusBadge";

// Qué acciones tiene sentido ofrecer según el estado actual de la cita.
// Coincide con las transiciones que el backend permite (ALLOWED_STATUS_TRANSITIONS).
const NEXT_ACTIONS = {
  pending: [
    { label: "Confirmar", value: "confirmed", variant: "btn-primary" },
    { label: "Cancelar", value: "cancelled", variant: "btn-ghost" },
  ],
  confirmed: [
    { label: "Completar", value: "completed", variant: "btn-primary" },
    { label: "Cancelar", value: "cancelled", variant: "btn-ghost" },
  ],
  completed: [],
  cancelled: [],
};

export default function DoctorAppointmentsPage() {
  const { token } = useAuth();

  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [updatingId, setUpdatingId] = useState(null);

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

  const handleStatusChange = async (appointmentId, newStatus) => {
    setUpdatingId(appointmentId);
    try {
      await api.updateAppointmentStatus(token, appointmentId, newStatus);
      await load();
    } catch (err) {
      setError(err.message);
    } finally {
      setUpdatingId(null);
    }
  };

  const formatDate = (iso) => {
    const date = new Date(iso);
    return date.toLocaleString("es-CL", { dateStyle: "medium", timeStyle: "short" });
  };

  return (
    <div className="page">
      <header className="page-header">
        <p className="eyebrow">Mis citas</p>
        <h1>Agenda de consultas</h1>
      </header>

      {loading ? (
        <p>Cargando…</p>
      ) : error ? (
        <p className="form-error">{error}</p>
      ) : appointments.length === 0 ? (
        <section className="card">
          <p>Todavía no tenés citas asignadas.</p>
        </section>
      ) : (
        <ul className="ledger-list">
          {appointments.map((appt) => (
            <li key={appt.id} className={`ledger-row status-${appt.status}`}>
              <div className="ledger-row-time">{formatDate(appt.scheduled_at)}</div>

              <div className="ledger-row-body">
                <p className="ledger-row-reason">
                  {appt.reason}
                  <span className="ledger-row-patient"> · Paciente: {appt.patient_name}</span>
                </p>
                <StatusBadge status={appt.status} />
              </div>

              <div className="ledger-row-actions">
                {NEXT_ACTIONS[appt.status].map((action) => (
                  <button
                    key={action.value}
                    className={`btn btn-small ${action.variant}`}
                    onClick={() => handleStatusChange(appt.id, action.value)}
                    disabled={updatingId === appt.id}
                  >
                    {updatingId === appt.id ? "…" : action.label}
                  </button>
                ))}
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
