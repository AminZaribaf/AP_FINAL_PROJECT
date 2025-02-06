from django.urls import path
from .views import CourseListView, AddCourseToEnrollmentView, DropCourseFromEnrollmentView, CourseDetailView, \
    StudentEnrollmentView, WeeklyScheduleView, AdminAddCourseView, AdminEditCourseView, AdminDeleteCourseView,\
    DepartmentCreateView , InstructorCreateView

urlpatterns = [
    # Add the URL pattern for the course list view
    path('', CourseListView.as_view(), name='course_list'),
    # Add the URL pattern for the add course to enrollment view
    path('add/', AddCourseToEnrollmentView.as_view(), name='add_course'),
    # Add the URL pattern for the drop course from enrollment view
    path('drop/', DropCourseFromEnrollmentView.as_view(), name='drop_course_from_enrollment'),
    # Add the URL pattern for the course list view
    path('list/', CourseListView.as_view(), name='course_list'),
    # Add the URL pattern for the course detail view
    path('detail/<int:course_id>/', CourseDetailView.as_view(), name='course_detail'),
    # Add the URL pattern for the student enrollment view
    path('enroll/', StudentEnrollmentView.as_view(), name='student_enrollment'),
    # Add the URL pattern for the weekly schedule view
    path('weekly-schedule/', WeeklyScheduleView.as_view(), name='weekly_schedule'),
    # Add the URL pattern for the admin add course view
    path('admin/add-course/', AdminAddCourseView.as_view(), name='admin_add_course'),
    # Add the URL pattern for the admin edit course view
    path('admin/edit-course/<int:course_id>/', AdminEditCourseView.as_view(), name='admin_edit_course'),
    # Add the URL pattern for the admin delete course view
    path('admin/delete-course/<int:course_id>/', AdminDeleteCourseView.as_view(), name='admin_delete_course'),

    path('departments/create/', DepartmentCreateView.as_view(), name='create_department'),
    path('instructors/create/', InstructorCreateView.as_view(), name='create_instructor'),
]
