const configuredBackendUrl = import.meta.env.VITE_BACKEND_URL as string | undefined;

export const BACKEND_URL = configuredBackendUrl?.replace(/\/$/, "") || "http://localhost:8000";
