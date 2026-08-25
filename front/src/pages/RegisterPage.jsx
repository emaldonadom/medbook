import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { api } from "../api/client";

export default function RegisterPage() {
  const { login } = useAuth();
  const navigate = useNavigate();

  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const handleChange = (field) => (e) =>
    setForm((f) => ({ ...f, [field]: e.target.value }));

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setSubmitting(true);

    try {
      await api.register({ ...form, role_id: 3 });
      await login(form.email, form.password);
      navigate("/perfil");
    } catch (err) {
      setError(err.message || "No se pudo completar el registro");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="auth-screen">
      <div className="auth-visual">
        <div className="ledger-stack" aria-hidden="true">
          <div className="ledger-card tab-confirmed">
            <span className="ledger-time">10:00</span>
            <span className="ledger-label">Primera consulta</span>
          </div>
          <div className="ledger-card tab-pending">
            <span className="ledger-time">16:45</span>
            <span className="ledger-label">Seguimiento</span>
          </div>
        </div>

        <p className="eyebrow">MedBook</p>
        <h1>Creá tu cuenta de paciente.</h1>
        <p className="auth-visual-copy">
          Un solo registro para agendar, cancelar y seguir todas tus consultas.
        </p>
      </div>

      <div className="auth-form-panel">
        <div className="auth-form-card">
          <p className="eyebrow">Crear cuenta</p>
          <h2>Registrate como paciente</h2>

          <form onSubmit={handleSubmit} className="form">
            <label className="field">
              <span>Nombre completo</span>
              <input value={form.name} onChange={handleChange("name")} required />
            </label>

            <label className="field">
              <span>Email</span>
              <input
                type="email"
                value={form.email}
                onChange={handleChange("email")}
                required
              />
            </label>

            <label className="field">
              <span>Contraseña</span>
              <input
                type="password"
                value={form.password}
                onChange={handleChange("password")}
                required
                minLength={6}
              />
            </label>

            {error && <p className="form-error">{error}</p>}

            <button className="btn btn-primary" type="submit" disabled={submitting}>
              {submitting ? "Creando cuenta…" : "Crear cuenta"}
            </button>
          </form>

          <p className="form-footnote">
            ¿Ya tenés cuenta? <Link to="/login">Ingresá</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
