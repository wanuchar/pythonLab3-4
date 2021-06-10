from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('subjects/',
         views.SubjectsListView.as_view(),
         name='all_subject'),
    path('subjects/create/',
         views.SubjectCreateView.as_view(),
         name='subject_create'),
    path('subject/<int:pk>/',
         views.CourseDetailView.as_view(),
         name='course_detail'),
    path('course/<int:pk>/join/',
         views.CourseRegistrationView.as_view(),
         name='course_joined'),
]
