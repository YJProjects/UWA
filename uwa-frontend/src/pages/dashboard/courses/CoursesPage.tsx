import { useState, type FormEvent } from "react";
import { Search } from "lucide-react";
import DashboardPageHeader from "../../../components/dashboard/DashboardPageHeader";
import { getFirebaseAuth } from "../../../firebase/firebaseAuth";
import { searchCourses, type CourseSearchResult } from "../../../services/courses";
import { saveUserCourse } from "../../../services/userCourses";
import CourseCard from "./components/CourseCard";
import SectionAvailability from "./components/SectionAvailability";
import SectionCard from "./components/SectionCard";
import "./CoursesPage.css";

export default function CoursesPage() {
    const [query, setQuery] = useState("");
    const [results, setResults] = useState<CourseSearchResult[]>([]);
    const [selectedCourseId, setSelectedCourseId] = useState<string | null>(null);
    const [selectedSectionId, setSelectedSectionId] = useState<string | null>(null);
    const [savedSectionIds, setSavedSectionIds] = useState<Set<string>>(() => new Set());
    const [savingSectionId, setSavingSectionId] = useState<string | null>(null);
    const [saveError, setSaveError] = useState<string | null>(null);
    const [hasSearched, setHasSearched] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const selectedCourse = results.find((course) => course.id === selectedCourseId) ?? null;
    const selectedSection = selectedCourse?.sections.find((section) => section.id === selectedSectionId) ?? null;

    async function handleSearch(event: FormEvent<HTMLFormElement>) {
        event.preventDefault();

        const trimmedQuery = query.trim();
        if (!trimmedQuery) {
            setError("Enter at least four department letters, such as CMSC or MATH.");
            setResults([]);
            setHasSearched(false);
            return;
        }

        setIsLoading(true);
        setError(null);
        setSelectedCourseId(null);
        setSelectedSectionId(null);

        try {
            setResults(await searchCourses(trimmedQuery));
            setHasSearched(true);
        } catch (searchError) {
            setResults([]);
            setHasSearched(true);
            setError(searchError instanceof Error ? searchError.message : "Unable to search courses.");
        } finally {
            setIsLoading(false);
        }
    }

    function selectCourse(courseId: string) {
        setSelectedCourseId(courseId);
        setSelectedSectionId(null);
        setSaveError(null);
    }

    async function saveSelectedCourse() {
        if (!selectedCourse || !selectedSection) {
            return;
        }

        const user = getFirebaseAuth().currentUser;
        if (!user) {
            setSaveError("You must be signed in before saving a course.");
            return;
        }

        setSavingSectionId(selectedSection.id);
        setSaveError(null);

        try {
            await saveUserCourse(user.uid, selectedCourse.code, selectedSection.classNumber);
            setSavedSectionIds((currentIds) => new Set(currentIds).add(selectedSection.id));
        } catch (saveCourseError) {
            setSaveError(saveCourseError instanceof Error ? saveCourseError.message : "Unable to save this course.");
        } finally {
            setSavingSectionId(null);
        }
    }

    return (
        <section className="courses-page">
            <DashboardPageHeader
                eyebrow="Course catalogue"
                title="Find the right course."
                description="Search by UMD course code, choose a course and section, then check live Testudo availability."
            />

            <form className="courses-page__search" onSubmit={handleSearch}>
                <Search className="courses-page__search-icon" aria-hidden="true" strokeWidth={1.8} />
                <input
                    type="search"
                    aria-label="Search courses"
                    placeholder="Try CMSC, CMSC13, or CMSC131"
                    value={query}
                    onChange={(event) => setQuery(event.target.value)}
                    minLength={4}
                    maxLength={9}
                    pattern="[A-Za-z]{4}[0-9]{0,3}[A-Za-z]?"
                    title="Enter four department letters followed by up to three digits and an optional suffix."
                />
                <button type="submit" disabled={isLoading}>{isLoading ? "Searching…" : "Search"}</button>
            </form>

            {error && <p className="courses-page__message courses-page__message--error" role="alert">{error}</p>}

            {!hasSearched && !error && (
                <article className="courses-page__placeholder">
                    <h3>Your search results will appear here</h3>
                    <p>Enter at least four department letters or a partial course code to begin.</p>
                </article>
            )}

            {hasSearched && !error && (
                <section className="courses-page__flow" aria-live="polite" aria-busy={isLoading}>
                    <div className="courses-page__step-heading">
                        <span>1</span>
                        <div><p>Step 1</p><h3>Choose a course</h3></div>
                    </div>

                    {results.length === 0 ? (
                        <article className="courses-page__placeholder">
                            <h3>No matching courses</h3>
                            <p>Try a broader course prefix, such as CMSC instead of CMSC131.</p>
                        </article>
                    ) : (
                        <div className="courses-page__course-list">
                            {results.map((course) => (
                                <CourseCard
                                    key={course.id}
                                    course={course}
                                    isSelected={course.id === selectedCourseId}
                                    onSelect={selectCourse}
                                />
                            ))}
                        </div>
                    )}

                    {selectedCourse && (
                        <section className="courses-page__sections">
                            <div className="courses-page__step-heading">
                                <span>2</span>
                                <div><p>Step 2</p><h3>Choose a section for {selectedCourse.code}</h3></div>
                            </div>
                            <div className="courses-page__section-list">
                                {selectedCourse.sections.map((section) => (
                                    <SectionCard
                                        key={section.id}
                                        section={section}
                                        isSelected={section.id === selectedSectionId}
                                        onSelect={setSelectedSectionId}
                                    />
                                ))}
                            </div>
                        </section>
                    )}

                    {selectedCourse && selectedSection && (
                        <SectionAvailability
                            course={selectedCourse}
                            section={selectedSection}
                            isSaved={savedSectionIds.has(selectedSection.id)}
                            isSaving={savingSectionId === selectedSection.id}
                            saveError={saveError}
                            onSaveCourse={saveSelectedCourse}
                        />
                    )}
                </section>
            )}
        </section>
    );
}
