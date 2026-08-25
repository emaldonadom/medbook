import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function HomeRedirect() {
  const { user } = useAuth();

  if (user?.role?.name === "admin") {
    return <Navigate to="/usuarios" replace />;
  }

  return <Navigate to="/citas" replace />;
}
