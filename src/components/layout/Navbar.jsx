import Button from "../ui/Button.jsx";

const navItems = [
  { href: "#/overview", label: "Overview" },
  { href: "#/scans", label: "Scans" },
  { href: "#/findings", label: "Findings" },
  { href: "#/reports", label: "Reports" },
  { href: "#/settings", label: "Settings" },
];

export function Topbar({
  activeRoute,
  apiStatus,
  onRefresh,
  onLogout,
  username = "Operator",
}) {
  return (
    <header className="dashboard-topbar">
      <nav className="topbar-nav" aria-label="Dashboard navigation">
        {navItems.map((item) => (
          <a
            className={activeRoute === item.href.slice(2) ? "active" : ""}
            href={item.href}
            key={item.href}
          >
            {item.label}
          </a>
        ))}
      </nav>

      <div className="topbar-actions">
        <Button size="sm" variant="ghost" onClick={onLogout}>
          Logout
        </Button>
      </div>
    </header>
  );
}

export default Topbar;
