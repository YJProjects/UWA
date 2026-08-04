import type { ReactNode } from "react";
import "./DashboardPageHeader.css";

interface DashboardPageHeaderProps {
    eyebrow: string;
    title: string;
    description: string;
    action?: ReactNode;
}

export default function DashboardPageHeader({
    eyebrow,
    title,
    description,
    action,
}: DashboardPageHeaderProps) {
    return (
        <header className="dashboard-page-header">
            <div>
                <p className="dashboard-page-header__eyebrow">{eyebrow}</p>
                <h2>{title}</h2>
                <p className="dashboard-page-header__description">{description}</p>
            </div>
            {action}
        </header>
    );
}
