import DashboardPageHeader from "../../../components/dashboard/DashboardPageHeader";
import "./HelpPage.css";

export default function HelpPage() {
    return (
        <section className="help-page">
            <DashboardPageHeader eyebrow="Help centre" title="How can we help?" description="Find quick answers or get in touch with the UWA team." />
            <div className="help-page__grid">
                <article><span>01</span><h3>How course alerts work</h3><p>Learn what we check and when you will be notified.</p><button type="button">Read guide →</button></article>
                <article><span>02</span><h3>Manage tracked courses</h3><p>Add, pause, or remove a course from your watchlist.</p><button type="button">Read guide →</button></article>
                <article><span>03</span><h3>Contact support</h3><p>Still stuck? Send us a note and we will help.</p><button type="button">Get in touch →</button></article>
            </div>
        </section>
    );
}
