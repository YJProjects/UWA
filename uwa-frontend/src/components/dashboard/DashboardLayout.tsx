import { useEffect, useState } from "react";
import { Outlet, useLocation, useNavigate } from "react-router-dom";
import { signOut } from "firebase/auth";
import { getFirebaseAuth } from "../../firebase/firebaseAuth";
import DashboardSidebar from "./DashboardSidebar";
import DashboardTopbar from "./DashboardTopbar";
import { dashboardPageTitles } from "./navigation";
import "./DashboardLayout.css";

export default function DashboardLayout() {
    const navigate = useNavigate();
    const location = useLocation();
    const [isMenuOpen, setIsMenuOpen] = useState(false);
    const firebaseAuth = getFirebaseAuth();
    const user = firebaseAuth.currentUser;

    useEffect(() => {
        if (user && !user.emailVerified) {
            alert("Please verify your email before logging in. App will refuse to work without a verified email.");
            void signOut(firebaseAuth).then(() => navigate("/", { replace: true }));
        }
    }, [firebaseAuth, navigate, user]);

    const displayName = user?.displayName || user?.email?.split("@")[0] || "Student";
    const initial = displayName.charAt(0).toUpperCase();
    const pageTitle = dashboardPageTitles[location.pathname] ?? "Dashboard";

    return (
        <div className="dashboard-shell">
            <DashboardSidebar
                isOpen={isMenuOpen}
                onNavigate={() => setIsMenuOpen(false)}
            />

            {isMenuOpen && (
                <button
                    className="dashboard-backdrop"
                    type="button"
                    aria-label="Close navigation"
                    onClick={() => setIsMenuOpen(false)}
                />
            )}

            <div className="dashboard-main">
                <DashboardTopbar
                    pageTitle={pageTitle}
                    initial={initial}
                    isMenuOpen={isMenuOpen}
                    onMenuToggle={() => setIsMenuOpen((open) => !open)}
                    onProfileClick={() => navigate("/dashboard/settings")}
                    onDashboardEyebrowClick={() => navigate("/dashboard")}
                />
                <main className="dashboard-content">
                    <Outlet />
                </main>
            </div>
        </div>
    );
}
