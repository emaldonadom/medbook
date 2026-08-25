import { useAuth } from "../context/AuthContext";
import AppointmentsPage from "./AppointmentsPage";
import DoctorAppointmentsPage from "./DoctorAppointmentsPage";
import AdminAppointmentsPage from "./AdminAppointmentsPage";

// La ruta /citas es la misma para todos, pero lo que se ve adentro
// depende del rol: paciente ve (y puede cancelar) sus propias citas;
// doctor ve su agenda y puede confirmar/completar/cancelar;
// admin ve todas las citas del sistema y puede eliminarlas.
export default function CitasRouterPage() {
  const { user } = useAuth();
  const role = user?.role?.name;

  if (role === "doctor") {
    return <DoctorAppointmentsPage />;
  }

  if (role === "admin") {
    return <AdminAppointmentsPage />;
  }

  return <AppointmentsPage />;
}
