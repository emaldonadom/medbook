import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setSubmitting(true);

    try {
      await login(email, password);
      navigate("/");
    } catch (err) {
      setError(err.message || "No se pudo iniciar sesión");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="auth-screen">
      <div className="auth-visual">
        <div className="ledger-stack" aria-hidden="true">
          <div className="ledger-card tab-pending">
            <span className="ledger-time">09:30</span>
            <span className="ledger-label">Control anual</span>
          </div>
          <div className="ledger-card tab-confirmed">
            <span className="ledger-time">11:00</span>
            <span className="ledger-label">Dra. Ibarra</span>
          </div>
          <div className="ledger-card tab-completed">
            <span className="ledger-time">14:15</span>
            <span className="ledger-label">Chequeo</span>
          </div>
        </div>

        <p className="eyebrow">MedBook</p>
        <h1>Tu próxima cita, siempre a la vista.</h1>
        <p className="auth-visual-copy">
          Agendá con tu doctor, seguí el estado de cada cita y llevá tu historial
          en un solo lugar.
        </p>
      </div>

      <div className="auth-form-panel">
        <div className="auth-form-card">
          <p className="eyebrow">Ingresar</p>
          <h2>Bienvenido de nuevo</h2>

          <form onSubmit={handleSubmit} className="form">
            <label className="field">
              <span>Email</span>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                autoComplete="email"
              />
            </label>

            <label className="field">
              <span>Contraseña</span>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                autoComplete="current-password"
              />
            </label>

            {error && <p className="form-error">{error}</p>}

            <button className="btn btn-primary" type="submit" disabled={submitting}>
              {submitting ? "Ingresando…" : "Ingresar"}
            </button>
          </form>

          <p className="form-footnote">
            ¿No tenés cuenta? <Link to="/register">Registrate</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
