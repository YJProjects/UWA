import { BellPlus, Check } from "lucide-react";
import type { CourseSearchResult, CourseSection } from "../../../../services/courses";

interface SectionAvailabilityProps {
    course: CourseSearchResult;
    section: CourseSection;
    isSaved: boolean;
    isSaving: boolean;
    saveError: string | null;
    onSaveCourse: () => void;
}

function getAvailability(section: CourseSection) {
    if (section.availableSeats === null) {
        return { label: "Availability unknown", detail: "Testudo did not provide a current seat count.", tone: "unknown" };
    }

    if (section.availableSeats === 0) {
        return { label: "Section full", detail: "No seats are currently available.", tone: "full" };
    }

    if (section.availableSeats <= 5) {
        return { label: "Limited availability", detail: `${section.availableSeats} seats remain.`, tone: "limited" };
    }

    return { label: "Seats available", detail: `${section.availableSeats} seats are currently open.`, tone: "open" };
}

export default function SectionAvailability({
    course,
    section,
    isSaved,
    isSaving,
    saveError,
    onSaveCourse,
}: SectionAvailabilityProps) {
    const availability = getAvailability(section);
    const hasCapacity = section.availableSeats !== null && section.totalSeats !== null && section.totalSeats > 0;
    const filledSeats = hasCapacity ? section.totalSeats! - section.availableSeats! : null;
    const fillPercentage = hasCapacity ? Math.round((filledSeats! / section.totalSeats!) * 100) : null;

    return (
        <section className="courses-page__availability-panel" aria-live="polite">
            <div className="courses-page__availability-heading">
                <div>
                    <p>Step 3 · Availability</p>
                    <h3>{course.code} · {section.section}</h3>
                </div>
                <span className={`courses-page__availability-status courses-page__availability-status--${availability.tone}`}>
                    {availability.label}
                </span>
            </div>

            <div className="courses-page__availability-body">
                <div className="courses-page__seat-figure">
                    <strong>{section.availableSeats ?? "—"}</strong>
                    <span>{section.totalSeats === null ? "Current capacity unavailable" : `of ${section.totalSeats} seats available`}</span>
                </div>
                <div className="courses-page__capacity">
                    <div className="courses-page__capacity-copy"><span>Section capacity</span><strong>{fillPercentage === null ? "Unavailable" : `${fillPercentage}% filled`}</strong></div>
                    <div className="courses-page__capacity-track" aria-hidden="true">
                        <span style={{ width: `${fillPercentage ?? 0}%` }} />
                    </div>
                    <p>{availability.detail} Availability is fetched live from Testudo through the UWA backend.</p>
                </div>
            </div>

            <button
                className={`courses-page__track-button${isSaved ? " is-tracked" : ""}`}
                type="button"
                disabled={isSaving || isSaved}
                onClick={onSaveCourse}
            >
                {isSaved ? <Check aria-hidden="true" /> : <BellPlus aria-hidden="true" />}
                {isSaving ? "Saving…" : isSaved ? `${course.code} ${section.classNumber} saved` : `Save ${course.code} ${section.classNumber}`}
            </button>
            {saveError && <p className="courses-page__save-error" role="alert">{saveError}</p>}
        </section>
    );
}
