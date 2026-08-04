export const dashboardNavigation = [
    { label: "Overview", to: "/dashboard", end: true, icon: "overview" },
    { label: "Find courses", to: "/dashboard/courses", icon: "search" },
    { label: "Settings", to: "/dashboard/settings", icon: "settings" },
    { label: "Help", to: "/dashboard/help", icon: "help" },
] as const;

export const dashboardPageTitles: Record<string, string> = {
    "/dashboard": "Overview",
    "/dashboard/courses": "Find courses",
    "/dashboard/settings": "Settings",
    "/dashboard/help": "Help & support",
};

export type DashboardNavigationIcon = (typeof dashboardNavigation)[number]["icon"];
