CREATE UNIQUE INDEX IF NOT EXISTS user_saved_courses_user_course_section_unique
ON public.user_saved_courses (user_id, course, section);
