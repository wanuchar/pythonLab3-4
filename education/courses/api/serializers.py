from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from ..models import Subject, Course, Module, Content


class ContentSerializer(ModelSerializer):
    class Meta:
        model = Content
        fields = ['content_type']


class ModuleSerializer(ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    contents = ContentSerializer(many=True, read_only=True)

    class Meta:
        model = Module
        fields = ['owner', 'title', 'description', 'order', 'contents']


class CourseSerializer(ModelSerializer):
    modules = ModuleSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'owner', 'subject', 'title',
                  'slug', 'overview', 'created', 'modules']


class SubjectSerializer(ModelSerializer):
    courses = CourseSerializer(many=True, read_only=True)

    class Meta:
        model = Subject
        fields = ['id', 'title', 'slug', 'courses']


