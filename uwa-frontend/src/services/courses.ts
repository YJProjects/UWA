import { BACKEND_URL } from "../config";

export interface CourseSection {
    id: string;
    classNumber: string;
    section: string;
    schedule: string;
    campus: string;
    location: string;
    deliveryMode: string;
    instructor: string;
    availableSeats: number | null;
    totalSeats: number | null;
}

export interface CourseSearchResult {
    id: string;
    code: string;
    title: string;
    school: string;
    term: string;
    sections: CourseSection[];
}

interface ApiErrorResponse {
    detail?: string | Array<{ msg?: string }>;
}

function getErrorMessage(errorResponse: ApiErrorResponse, status: number): string {
    if (typeof errorResponse.detail === "string") {
        return errorResponse.detail;
    }

    if (Array.isArray(errorResponse.detail)) {
        const validationMessage = errorResponse.detail.find((item) => item.msg)?.msg;
        if (validationMessage) {
            return validationMessage;
        }
    }

    return `Course search failed with status ${status}.`;
}

export async function searchCourses(query: string): Promise<CourseSearchResult[]> {
    const searchParams = new URLSearchParams({ query: query.trim() });
    const response = await fetch(`${BACKEND_URL}/umd-api/courses?${searchParams}`, {
        headers: { Accept: "application/json" },
    });

    if (!response.ok) {
        let errorResponse: ApiErrorResponse = {};

        try {
            errorResponse = await response.json() as ApiErrorResponse;
        } catch {
            // The fallback below handles non-JSON upstream errors.
        }

        throw new Error(getErrorMessage(errorResponse, response.status));
    }

    return await response.json() as CourseSearchResult[];
}
