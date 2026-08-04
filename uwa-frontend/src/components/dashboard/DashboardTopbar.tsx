interface DashboardTopbarProps {
    pageTitle: string;
    initial: string;
    isMenuOpen: boolean;
    onMenuToggle: () => void;
    onProfileClick: () => void;
    onDashboardEyebrowClick: () => void,
}

export default function DashboardTopbar({
    pageTitle,
    initial,
    isMenuOpen,
    onMenuToggle,
    onProfileClick,
    onDashboardEyebrowClick,
}: DashboardTopbarProps) {
    return (
        <header className="dashboard-topbar">
            <button
                className="dashboard-menu-button"
                type="button"
                aria-label="Open navigation"
                aria-expanded={isMenuOpen}
                onClick={onMenuToggle}
            >
                <span />
                <span />
                <span />
            </button>
            <div>
                <button className="dashboard-eyebrow" onClick={onDashboardEyebrowClick}>Dashboard /</button>  <span>{pageTitle}</span>
            </div>
            <button
                className="dashboard-profile-button"
                type="button"
                aria-label="Open account settings"
                onClick={onProfileClick}
            >
                <span className="dashboard-avatar" aria-hidden="true">{initial}</span>
            </button>
        </header>
    );
}
