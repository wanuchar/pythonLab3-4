from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from ..models import Subject, Course
from .serializers import SubjectSerializer, CourseSerializer
from django.shortcuts import get_object_or_404
from .permissions import IsOwnerOrReadOnly


class SubjectMixin:
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    # permission_classes = (IsAuthenticated,)


class SubjectCreateView(SubjectMixin, CreateAPIView):
    pass


class SubjectsListView(SubjectMixin, ListAPIView):
    pass


class CourseDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = (IsOwnerOrReadOnly,)


class CourseRegistrationView(APIView):
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk, format=None):
        course = get_object_or_404(Course, pk=pk)
        course.users.add(request.user)
        return Response({'joined': True})


    # def get(self, request, format=None):
    #     content = {
    #         'user': unicode(request.user),  # `django.contrib.auth.User` instance.
    #         'auth': unicode(request.auth),  # None
    #     }
    #     return Response(content)
