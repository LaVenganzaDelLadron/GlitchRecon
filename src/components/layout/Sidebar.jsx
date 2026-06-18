const navItems = [
  { href: "#/overview", label: "Overview" },
  { href: "#/projects", label: "Projects" },
  { href: "#/targets", label: "Targets" },
  { href: "#/scans", label: "Scans" },
  { href: "#/findings", label: "Findings" },
  { href: "#/reports", label: "Reports" },
  { href: "#/settings", label: "Settings" },
];

export function SidebarNav({ activeRoute }) {
  return (
    <aside className="dashboard-sidebar">
      <a className="dashboard-brand" href="#/overview">
        <span className="brand-mark">G</span>
        <span>GlitchRecon</span>
      </a>

      <nav className="dashboard-nav" aria-label="Dashboard navigation">
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
    </aside>
  );
}

export default SidebarNav;
