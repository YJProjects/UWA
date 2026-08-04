import { Check } from "lucide-react";
import type { CourseSection } from "../../../../services/courses";

interface SectionCardProps {
    section: CourseSection;
    isSelected: boolean;
    onSelect: (sectionId: string) => void;
}

export default function SectionCard({ section, isSelected, onSelect }: SectionCardProps) {
    return (
        <button
            className={`courses-page__section-card${isSelected ? " is-selected" : ""}`}
            type="button"
            aria-pressed={isSelected}
            onClick={() => onSelect(section.id)}
        >
            <span className="courses-page__section-card-marker" aria-hidden="true">
                {isSelected && <Check />}
            </span>
            <span className="courses-page__section-card-copy">
                <span className="courses-page__section-card-topline">
                    <strong>{section.section}</strong>
                    <small>Class {section.classNumber}</small>
                </span>
                <span>{section.schedule}</span>
                <small>{section.location} · {section.deliveryMode}</small>
                <small>{section.instructor}</small>
            </span>
        </button>
    );
}
