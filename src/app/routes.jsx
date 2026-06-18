import { useEffect } from "react";
import Landing from "../features/auth/pages/Landing.jsx";
import Login from "../features/auth/pages/Login.jsx";
import Register from "../features/auth/pages/Register.jsx";
import Dashboard from "../features/dashboard/pages/Dashboard.jsx";
import { API_BASE_URL, apiRoutes, getBackendUrl } from "../services/api.js";

function redirectTo(path) {
  return function BackendRedirect() {
    useEffect(() => {
      window.location.replace(getBackendUrl(path));
    }, []);

    return (
      <main className="redirect-page">
        <p>Opening {API_BASE_URL}{path}</p>
      </main>
    );
  };
}

export const routes = {
  "/": Landing,
  "/login": Login,
  "/register": Register,
  "/dashboard": Dashboard,
  "/docs": redirectTo(apiRoutes.docs),
  "/redoc": redirectTo(apiRoutes.redoc),
  "/openapi.json": redirectTo(apiRoutes.openapi),
};
