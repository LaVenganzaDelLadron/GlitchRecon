import { useEffect, useRef, useState } from "react";
import SidebarNav from "./Sidebar.jsx";
import Topbar from "./Navbar.jsx";

const DEFAULT_SIDEBAR_WIDTH = 268;
const MIN_SIDEBAR_WIDTH = 220;
const MAX_SIDEBAR_WIDTH = 500;
const SIDEBAR_STORAGE_KEY = "glitchrecon.sidebarWidth";

function clampSidebarWidth(width) {
  return Math.min(MAX_SIDEBAR_WIDTH, Math.max(MIN_SIDEBAR_WIDTH, width));
}

function getInitialSidebarWidth() {
  const storedWidth = Number(window.localStorage.getItem(SIDEBAR_STORAGE_KEY));

  if (!Number.isFinite(storedWidth)) {
    return DEFAULT_SIDEBAR_WIDTH;
  }

  return clampSidebarWidth(storedWidth);
}

function DashboardLayout({
  activeRoute,
  apiStatus,
  children,
  onAddProject,
  onClearSelection,
  onLogout,
  onRefresh,
  onSelectProject,
  onSelectTarget,
  projects,
  selectedProjectId,
  selectedTargetId,
  targets,
  username,
}) {
  const shellRef = useRef(null);
  const cleanupResizeRef = useRef(null);
  const [sidebarWidth, setSidebarWidth] = useState(getInitialSidebarWidth);
  const [isResizingSidebar, setIsResizingSidebar] = useState(false);

  useEffect(() => () => {
    cleanupResizeRef.current?.();
  }, []);

  function updateSidebarWidth(width) {
    const nextWidth = clampSidebarWidth(width);
    setSidebarWidth(nextWidth);
    window.localStorage.setItem(SIDEBAR_STORAGE_KEY, String(nextWidth));
  }

  function startSidebarResize(event) {
    if (event.button !== 0) {
      return;
    }

    event.preventDefault();
    setIsResizingSidebar(true);
    document.body.style.cursor = "col-resize";
    document.body.style.userSelect = "none";

    function resizeSidebar(moveEvent) {
      const shellRect = shellRef.current?.getBoundingClientRect();

      if (!shellRect) {
        return;
      }

      updateSidebarWidth(moveEvent.clientX - shellRect.left);
    }

    function stopSidebarResize() {
      setIsResizingSidebar(false);
      document.body.style.cursor = "";
      document.body.style.userSelect = "";
      window.removeEventListener("pointermove", resizeSidebar);
      window.removeEventListener("pointerup", stopSidebarResize);
      window.removeEventListener("pointercancel", stopSidebarResize);
      cleanupResizeRef.current = null;
    }

    cleanupResizeRef.current = stopSidebarResize;
    window.addEventListener("pointermove", resizeSidebar);
    window.addEventListener("pointerup", stopSidebarResize);
    window.addEventListener("pointercancel", stopSidebarResize);
  }

  function resizeSidebarWithKeyboard(event) {
    if (event.key === "ArrowLeft") {
      event.preventDefault();
      updateSidebarWidth(sidebarWidth - 16);
    }

    if (event.key === "ArrowRight") {
      event.preventDefault();
      updateSidebarWidth(sidebarWidth + 16);
    }

    if (event.key === "Home") {
      event.preventDefault();
      updateSidebarWidth(MIN_SIDEBAR_WIDTH);
    }

    if (event.key === "End") {
      event.preventDefault();
      updateSidebarWidth(MAX_SIDEBAR_WIDTH);
    }
  }

  function resetSidebarWidth() {
    updateSidebarWidth(DEFAULT_SIDEBAR_WIDTH);
  }

  return (
    <div
      className={`dashboard-shell ${isResizingSidebar ? "resizing-sidebar" : ""}`}
      ref={shellRef}
      style={{ "--dashboard-sidebar-width": `${sidebarWidth}px` }}
    >
      <SidebarNav
        onAddProject={onAddProject}
        onClearSelection={onClearSelection}
        onSelectProject={onSelectProject}
        onSelectTarget={onSelectTarget}
        projects={projects}
        selectedProjectId={selectedProjectId}
        selectedTargetId={selectedTargetId}
        targets={targets}
      />
      <button
        aria-label="Resize sidebar"
        aria-orientation="vertical"
        aria-valuemax={MAX_SIDEBAR_WIDTH}
        aria-valuemin={MIN_SIDEBAR_WIDTH}
        aria-valuenow={sidebarWidth}
        className="sidebar-resize-handle"
        role="separator"
        title="Drag to resize sidebar. Double-click to reset."
        type="button"
        onDoubleClick={resetSidebarWidth}
        onKeyDown={resizeSidebarWithKeyboard}
        onPointerDown={startSidebarResize}
      />
      <div className="dashboard-main">
        <Topbar
          activeRoute={activeRoute}
          apiStatus={apiStatus}
          onLogout={onLogout}
          onRefresh={onRefresh}
          username={username}
        />
        <main className="dashboard-content">{children}</main>
      </div>
    </div>
  );
}

export default DashboardLayout;
