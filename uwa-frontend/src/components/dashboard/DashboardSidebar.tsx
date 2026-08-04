import { NavLink } from "react-router-dom";
import { CircleHelp, LayoutDashboard, Search, Settings } from "lucide-react";
import { dashboardNavigation, type DashboardNavigationIcon } from "./navigation";

interface DashboardSidebarProps {
    isOpen: boolean;
    onNavigate: () => void;
}

function NavigationIcon({ name }: { name: DashboardNavigationIcon }) {
    const icons = {
        overview: LayoutDashboard,
        search: Search,
        settings: Settings,
        help: CircleHelp,
    };
    const Icon = icons[name];

    return <Icon className="dashboard-nav-icon" aria-hidden="true" strokeWidth={1.8} />;
}

export default function DashboardSidebar({
    isOpen,
    onNavigate,
}: DashboardSidebarProps) {
    return (
        <aside className={`dashboard-sidebar${isOpen ? " is-open" : ""}`} aria-label="Primary navigation">
            <div className="dashboard-brand">
                <span className="dashboard-brand-mark" aria-hidden="true">U</span>
                <span className="dashboard-brand-name">UWA</span>
            </div>

            <nav className="dashboard-nav">
                <p className="dashboard-nav-label">Workspace</p>
                {dashboardNavigation.map((item) => (
                    <NavLink
                        key={item.to}
                        to={item.to}
                        end={"end" in item ? item.end : false}
                        className={({ isActive }) => `dashboard-nav-link${isActive ? " is-active" : ""}`}
                        onClick={onNavigate}
                    >
                        <NavigationIcon name={item.icon} />
                        <span>{item.label}</span>
                    </NavLink>
                ))}
            </nav>

        </aside>
    );
}
