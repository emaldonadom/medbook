export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

async function request(path, { method = "GET", body, token, isForm = false } = {}) {
  const headers = {};

  if (!isForm && body !== undefined) {
    headers["Content-Type"] = "application/json";
  }

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    method,
    headers,
    body: body === undefined ? undefined : isForm ? body : JSON.stringify(body),
  });

  const text = await response.text();
  let data = null;

  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      data = text;
    }
  }

  if (!response.ok) {
    const detail = data?.detail;
    let message = `Error ${response.status}`;

    if (typeof detail === "string") {
      message = detail;
    } else if (Array.isArray(detail)) {
      // Errores de validación de Pydantic vienen como una lista de objetos
      message = detail.map((d) => d.msg).join(". ");
    }

    throw new Error(message);
  }

  return data;
}

export const api = {
  register: (payload) => request("/users/", { method: "POST", body: payload }),

  login: (email, password) => {
    const form = new URLSearchParams();
    form.append("username", email);
    form.append("password", password);
    return request("/auth/login", { method: "POST", body: form, isForm: true });
  },

  me: (token) => request("/auth/me", { token }),

  getMyPatientProfile: (token) => request("/patients/me", { token }),
  createPatientProfile: (token, payload) =>
    request("/patients/", { method: "POST", body: payload, token }),
  updatePatientProfile: (token, patientId, payload) =>
    request(`/patients/${patientId}`, { method: "PUT", body: payload, token }),
  listPatients: (token) => request("/patients/", { token }),
  deletePatient: (token, patientId) =>
    request(`/patients/${patientId}`, { method: "DELETE", token }),

  listDoctors: (token) => request("/users/doctors", { token }),

  listUsers: (token) => request("/users/", { token }),
  createUser: (token, payload) => request("/users/", { method: "POST", body: payload, token }),
  updateUserRole: (token, userId, roleId) =>
    request(`/users/${userId}`, { method: "PUT", body: { role_id: roleId }, token }),
  deleteUser: (token, userId) =>
    request(`/users/${userId}`, { method: "DELETE", token }),

  listAppointments: (token) => request("/appointments/", { token }),
  createAppointment: (token, payload) =>
    request("/appointments/", { method: "POST", body: payload, token }),
  updateAppointmentStatus: (token, appointmentId, status) =>
    request(`/appointments/${appointmentId}/status`, {
      method: "PATCH",
      body: { status },
      token,
    }),
  deleteAppointment: (token, appointmentId) =>
    request(`/appointments/${appointmentId}`, { method: "DELETE", token }),
};
