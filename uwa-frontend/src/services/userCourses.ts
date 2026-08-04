import { BACKEND_URL } from "../config";

interface SaveUserCourseRequest {
    user_id: string;
    course: string;
    section: string;
}

interface SaveUserCourseResponse {
    status?: number;
    detail?: string;
    message?: string;
}

export async function saveUserCourse(userId: string, courseCode: string, sectionNumber: string): Promise<void> {
    const requestBody: SaveUserCourseRequest = {
        user_id: userId,
        course: courseCode,
        section: sectionNumber,
    };

    const response = await fetch(`${BACKEND_URL}/user_data/save_user_course`, {
        method: "POST",
        headers: {
            Accept: "application/json",
            "Content-Type": "application/json",
        },
        body: JSON.stringify(requestBody),
    });

    let responseBody: SaveUserCourseResponse = {};

    try {
        responseBody = await response.json() as SaveUserCourseResponse;
    } catch {
        // An empty success response is valid; errors use the fallback below.
    }

    const bodyReportsFailure = typeof responseBody.status === "number" && responseBody.status >= 400;
    if (!response.ok || bodyReportsFailure) {
        const errorMessage = responseBody.detail
            || responseBody.message
            || `Unable to save ${courseCode}. Please try again.`;
        throw new Error(errorMessage);
    }
}
