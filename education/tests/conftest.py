import pytest
import users.models

from users.models import UserProfile
from courses.models import Subject, Course, Module


@pytest.fixture
def user_data():
    return dict(username='username',
                password='123123123!',
                email='email@email.ru',
                age=20,
                is_teacher=True)


@pytest.fixture
def user(user_data):
    return UserProfile.objects.create(**user_data)


@pytest.fixture
def authenticated_user(client, user_data):
    user = UserProfile.objects.create(**user_data)
    user.set_password(user_data.get('password'))
    user.save()
    client.login(**user_data)
    return user


@pytest.fixture
def subjects():
    return Subject.objects.create(title='subject',
                                  slug='subject')


@pytest.fixture
def course_data(authenticated_user, subjects):
    return dict(
        owner=authenticated_user,
        subject=subjects,
        title='course',
        slug='slug'
    )


@pytest.fixture
def courses(course_data):
    return Course.objects.create(**course_data)


@pytest.fixture
def module_data(courses):
    return dict(
        course=courses,
        title='module'
    )


@pytest.fixture
def modules(module_data):
    return Module.objects.create(**module_data)
