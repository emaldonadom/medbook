import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { api } from "../api/client";

export default function BookAppointmentPage() {
  const { token } = useAuth();

  const [doctors, setDoctors] = useState([]);
  const [hasProfile, setHasProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [form, setForm] = useState({ doctor_id: "", scheduled_at: "", reason: "" });
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    const load = async () => {
      setLoading(true);

      try {
        const doctorsList = await api.listDoctors(token);
        setDoctors(doctorsList);
      } catch (err) {
        setError(err.message);
      }

      try {
        await api.getMyPatientProfile(token);
        setHasProfile(true);
      } catch {
        setHasProfile(false);
      }

      setLoading(false);
    };

    load();
  }, [token]);

  const handleChange = (field) => (e) =>
    setForm((f) => ({ ...f, [field]: e.target.value }));

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setNotice("");
    setSubmitting(true);

    try {
      await api.createAppointment(token, {
        doctor_id: Number(form.doctor_id),
        scheduled_at: form.scheduled_at,
        reason: form.reason,
      });
      setNotice('Cita agendada. Podés verla en "Mis citas".');
      setForm({ doctor_id: "", scheduled_at: "", reason: "" });
    } catch (err) {
      setError(err.message || "No se pudo agendar la cita");
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return <p>Cargando…</p>;
  }

  if (hasProfile === false) {
    return (
      <div className="page">
        <header className="page-header">
          <p className="eyebrow">Agendar cita</p>
          <h1>Completá tu perfil primero</h1>
        </header>
        <section className="card">
          <p>Necesitás crear tu perfil de paciente antes de poder agendar una cita.</p>
          <Link className="btn btn-primary" to="/perfil">
            Ir a mi perfil
          </Link>
        </section>
      </div>
    );
  }

  return (
    <div className="page">
      <header className="page-header">
        <p className="eyebrow">Agendar cita</p>
        <h1>Elegí un doctor y un horario</h1>
      </header>

      <div className="two-col">
        <section className="card">
          <h2>Doctores disponibles</h2>

          {doctors.length === 0 ? (
            <p className="card-hint">Todavía no hay doctores registrados.</p>
          ) : (
            <ul className="doctor-list">
              {doctors.map((doc) => (
                <li
                  key={doc.id}
                  className={`doctor-item${String(doc.id) === form.doctor_id ? " selected" : ""}`}
                >
                  <button
                    type="button"
                    onClick={() => setForm((f) => ({ ...f, doctor_id: String(doc.id) }))}
                  >
                    <span className="doctor-name">{doc.name}</span>
                    <span className="doctor-email">{doc.email}</span>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </section>

        <section className="card">
          <h2>Detalles de la cita</h2>

          <form onSubmit={handleSubmit} className="form">
            <label className="field">
              <span>Doctor seleccionado</span>
              <select value={form.doctor_id} onChange={handleChange("doctor_id")} required>
                <option value="" disabled>
                  Elegí un doctor
                </option>
                {doctors.map((doc) => (
                  <option key={doc.id} value={doc.id}>
                    {doc.name}
                  </option>
                ))}
              </select>
            </label>

            <label className="field">
              <span>Fecha y hora</span>
              <input
                type="datetime-local"
                value={form.scheduled_at}
                onChange={handleChange("scheduled_at")}
                required
              />
            </label>

            <label className="field">
              <span>Motivo de consulta</span>
              <textarea rows={3} value={form.reason} onChange={handleChange("reason")} required />
            </label>

            {error && <p className="form-error">{error}</p>}
            {notice && <p className="form-notice">{notice}</p>}

            <button className="btn btn-primary" type="submit" disabled={submitting}>
              {submitting ? "Agendando…" : "Agendar cita"}
            </button>
          </form>
        </section>
      </div>
    </div>
  );
}
