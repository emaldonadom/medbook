import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { api } from "../api/client";

export default function ProfilePage() {
  const { token, user } = useAuth();

  const [patient, setPatient] = useState(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [form, setForm] = useState({ date_of_birth: "", phone: "", address: "" });
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const loadPatient = async () => {
    setLoading(true);
    try {
      const data = await api.getMyPatientProfile(token);
      setPatient(data);
      setForm({
        date_of_birth: data.date_of_birth,
        phone: data.phone,
        address: data.address,
      });
    } catch {
      setPatient(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPatient();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  const handleChange = (field) => (e) =>
    setForm((f) => ({ ...f, [field]: e.target.value }));

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setNotice("");
    setSubmitting(true);

    try {
      if (patient) {
        const updated = await api.updatePatientProfile(token, patient.id, form);
        setPatient(updated);
        setNotice("Perfil actualizado.");
      } else {
        const created = await api.createPatientProfile(token, form);
        setPatient(created);
        setNotice("Perfil de paciente creado.");
      }
      setEditing(false);
    } catch (err) {
      setError(err.message || "No se pudo guardar el perfil");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="page">
      <header className="page-header">
        <p className="eyebrow">Mi perfil</p>
        <h1>{user?.name}</h1>
        <p className="page-subtitle">
          {user?.email} · rol {user?.role?.name}
        </p>
      </header>

      {loading ? (
        <p>Cargando perfil…</p>
      ) : patient && !editing ? (
        <section className="card">
          <div className="card-header">
            <h2>Datos de paciente</h2>
            <button className="btn btn-secondary" onClick={() => setEditing(true)}>
              Editar
            </button>
          </div>

          <dl className="detail-list">
            <div>
              <dt>Fecha de nacimiento</dt>
              <dd>{patient.date_of_birth}</dd>
            </div>
            <div>
              <dt>Teléfono</dt>
              <dd>{patient.phone}</dd>
            </div>
            <div>
              <dt>Dirección</dt>
              <dd>{patient.address}</dd>
            </div>
          </dl>

          {notice && <p className="form-notice">{notice}</p>}
        </section>
      ) : (
        <section className="card">
          <div className="card-header">
            <h2>{patient ? "Editar datos de paciente" : "Completá tu perfil de paciente"}</h2>
          </div>

          {!patient && (
            <p className="card-hint">
              Necesitás crear este perfil antes de poder agendar una cita.
            </p>
          )}

          <form onSubmit={handleSubmit} className="form form-grid">
            <label className="field">
              <span>Fecha de nacimiento</span>
              <input
                type="date"
                value={form.date_of_birth}
                onChange={handleChange("date_of_birth")}
                required
              />
            </label>

            <label className="field">
              <span>Teléfono</span>
              <input value={form.phone} onChange={handleChange("phone")} required />
            </label>

            <label className="field field-full">
              <span>Dirección</span>
              <input value={form.address} onChange={handleChange("address")} required />
            </label>

            {error && <p className="form-error">{error}</p>}

            <div className="form-actions">
              <button className="btn btn-primary" type="submit" disabled={submitting}>
                {submitting ? "Guardando…" : "Guardar"}
              </button>
              {patient && (
                <button
                  type="button"
                  className="btn btn-ghost"
                  onClick={() => setEditing(false)}
                >
                  Cancelar
                </button>
              )}
            </div>
          </form>
        </section>
      )}
    </div>
  );
}
