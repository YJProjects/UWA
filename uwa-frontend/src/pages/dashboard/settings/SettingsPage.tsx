import { signOut } from "firebase/auth";
import { useNavigate } from "react-router-dom";
import { getFirebaseAuth } from "../../../firebase/firebaseAuth";
import DashboardPageHeader from "../../../components/dashboard/DashboardPageHeader";
import "./SettingsPage.css";

export default function SettingsPage() {
    const navigate = useNavigate();
    const firebaseAuth = getFirebaseAuth();
    const user = firebaseAuth.currentUser;
    const displayName = user?.displayName || user?.email?.split("@")[0] || "Student";
    const email = user?.email || "No email available";
    const initial = displayName.charAt(0).toUpperCase();

    async function signOutUser() {
        await signOut(firebaseAuth);
        navigate("/", { replace: true });
    }

    return (
        <section className="settings-page">
            <DashboardPageHeader eyebrow="Preferences" title="Make alerts work for you." description="Choose how and when you want to hear about course openings." />

            <div className="settings-page__section">
                <div className="settings-page__section-heading"><h3>Notifications</h3><p>Control the updates you receive from UWA.</p></div>
                <div className="settings-page__list">
                    <label><span><strong>Email notifications</strong><small>Receive an email when a tracked class opens.</small></span><input type="checkbox" defaultChecked /></label>
                    <label><span><strong>Weekly summary</strong><small>Get a simple summary of your tracked courses each Monday.</small></span><input type="checkbox" /></label>
                </div>
                <button className="settings-page__primary-action" type="button">Save changes</button>
            </div>

            <div className="settings-page__section">
                <div className="settings-page__section-heading"><h3>Account</h3><p>Your signed-in account and session controls.</p></div>
                <article className="settings-page__account-card">
                    <div className="settings-page__account-identity">
                        <span className="settings-page__account-avatar" aria-hidden="true">{initial}</span>
                        <span><strong>{displayName}</strong><small>{email}</small></span>
                    </div>
                    <button className="settings-page__destructive-action" type="button" onClick={signOutUser}>Sign out</button>
                </article>
            </div>
        </section>
    );
}
