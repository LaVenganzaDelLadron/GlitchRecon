import { routes } from "./routes.jsx";

function App() {
  const pathname = window.location.pathname;
  const RouteComponent = routes[pathname] ?? routes["/"];

  return <RouteComponent />;
}

export default App;
