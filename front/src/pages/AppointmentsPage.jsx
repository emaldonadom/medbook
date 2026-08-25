import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { api } from "../api/client";
import StatusBadge from "../components/StatusBadge";

export default function AppointmentsPage() {
  const { token } = useAuth();

  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [cancelingId, setCancelingId] = useState(null);

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

  const handleCancel = async (id) => {
    setCancelingId(id);
    try {
      await api.updateAppointmentStatus(token, id, "cancelled");
      await load();
    } catch (err) {
      setError(err.message);
    } finally {
      setCancelingId(null);
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
        <h1>Tu agenda médica</h1>
      </header>

      {loading ? (
        <p>Cargando…</p>
      ) : error ? (
        <p className="form-error">{error}</p>
      ) : appointments.length === 0 ? (
        <section className="card">
          <p>Todavía no agendaste ninguna cita.</p>
        </section>
      ) : (
        <ul className="ledger-list">
          {appointments.map((appt) => (
            <li key={appt.id} className={`ledger-row status-${appt.status}`}>
              <div className="ledger-row-time">{formatDate(appt.scheduled_at)}</div>
              <div className="ledger-row-body">
                <p className="ledger-row-reason">{appt.reason}</p>
                <StatusBadge status={appt.status} />
              </div>
              {["pending", "confirmed"].includes(appt.status) && (
                <button
                  className="btn btn-ghost btn-small"
                  onClick={() => handleCancel(appt.id)}
                  disabled={cancelingId === appt.id}
                >
                  {cancelingId === appt.id ? "Cancelando…" : "Cancelar"}
                </button>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
