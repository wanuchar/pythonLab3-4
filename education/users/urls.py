from django.urls import path
from . import views


urlpatterns = [
    path('signup/',
         views.SignUpView.as_view(),
         name='signup'),
    path('course-registration/',
         views.UserRegistrationCoursesView.as_view(),
         name='user_course_registration'),
    path('courses/',
         views.UserCourseListView.as_view(),
         name='user_course_list'),
    path('course/<pk>/',
         views.UserCourseDetailView.as_view(),
         name='user_course_detail'),
    path('course/<pk>/<module_id>/',
         views.UserCourseDetailView.as_view(),
         name='user_course_detail_module'),
]
