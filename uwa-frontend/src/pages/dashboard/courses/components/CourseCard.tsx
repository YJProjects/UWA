import { Check, ChevronRight } from "lucide-react";
import type { CourseSearchResult } from "../../../../services/courses";

interface CourseCardProps {
    course: CourseSearchResult;
    isSelected: boolean;
    onSelect: (courseId: string) => void;
}

export default function CourseCard({ course, isSelected, onSelect }: CourseCardProps) {
    return (
        <article className={`courses-page__course-card${isSelected ? " is-selected" : ""}`}>
            <div className="courses-page__course-card-copy">
                <div className="courses-page__course-card-topline">
                    <span>{course.code}</span>
                    <small>{course.term}</small>
                </div>
                <h4>{course.title}</h4>
                <p>{course.school}</p>
                <span className="courses-page__section-count">
                    {course.sections.length} {course.sections.length === 1 ? "section" : "sections"}
                </span>
            </div>
            <button
                type="button"
                aria-pressed={isSelected}
                onClick={() => onSelect(course.id)}
            >
                {isSelected ? <Check aria-hidden="true" /> : <ChevronRight aria-hidden="true" />}
                {isSelected ? "Selected" : "Choose course"}
            </button>
        </article>
    );
}
