import { Link } from "react-router-dom";
import DashboardPageHeader from "../../../components/dashboard/DashboardPageHeader";
import "./OverviewPage.css";

export default function OverviewPage() {
    return (
        <section className="overview-page">
            <DashboardPageHeader
                eyebrow="Your workspace"
                title="Stay ahead of course openings."
                description="Track the classes you need and get notified when a place becomes available."
                action={<Link className="overview-page__primary-action" to="/dashboard/courses">Find a course</Link>}
            />

            <div className="overview-page__stats">
                <article className="overview-page__stat"><span>Courses tracked</span><strong>0</strong><small>Ready when you are</small></article>
                <article className="overview-page__stat"><span>Open seats found</span><strong>0</strong><small>No new openings</small></article>
                <article className="overview-page__stat"><span>Alerts sent</span><strong>0</strong><small>This semester</small></article>
            </div>

            <article className="overview-page__empty-state">
                <span className="overview-page__empty-mark" aria-hidden="true">+</span>
                <div><h3>Start tracking your first course</h3><p>Search the course catalogue and turn on an alert in just a few steps.</p></div>
                <Link to="/dashboard/courses">Browse courses <span aria-hidden="true">→</span></Link>
            </article>
        </section>
    );
}
