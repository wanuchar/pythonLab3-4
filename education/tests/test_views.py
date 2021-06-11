import pytest

from django import urls
from django.contrib.auth import get_user_model


@pytest.mark.parametrize('param', ('signup',))
def test_render_views(client, param):
    temp_url = urls.reverse(param)
    response = client.get(temp_url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_signup(client, user_data):
    user_model = get_user_model()
    assert user_model.objects.count() == 0
    signup_url = urls.reverse('signup')
    response = client.post(signup_url, **user_data)
    assert user_model.objects.count() == 0
    assert response.status_code == 200


@pytest.mark.django_db
def test_login(client, user, user_data):
    users = get_user_model()
    assert users.objects.count() == 1
    url_ = urls.reverse(('login'))
    response = client.post(url_, data=user_data)
    assert response.status_code == 200


@pytest.mark.django_db
def test_logout(client, user):
    url_ = urls.reverse(('logout'))
    response = client.get(url_)
    assert response.status_code == 200


@pytest.mark.django_db
@pytest.mark.parametrize('param', (
    'user_course_registration',
    'user_course_list'))
def test_user_course(client, param, user):
    url_ = urls.reverse(param)
    response = client.get(url_)
    assert response.status_code == 302


@pytest.mark.django_db
@pytest.mark.parametrize('param', (
        'user_course_list',
        'manage_course_list',
        'course_create'))
def test_authenticated_user(client, param, authenticated_user):
    url_ = urls.reverse(param)
    response = client.get(url_)
    assert response.status_code == 200


@pytest.mark.django_db
@pytest.mark.parametrize('param', (
        'course_list',
        'login',
        'signup'))
def test_anonymous_user(client, param):
    url_ = urls.reverse(param)
    response = client.get(url_)
    assert response.status_code == 200


@pytest.mark.django_db
@pytest.mark.parametrize('param', (
        'user_course_detail_module',
))
def test_user_course_detail_module(client, param, courses,
                                   modules, authenticated_user):
    url_ = urls.reverse(param, args=(courses.id, modules.id))
    response = client.get(url_)
    assert response.status_code == 404


@pytest.mark.django_db
@pytest.mark.parametrize('param', (
        'course_edit',
        'course_delete',
        'course_module_update'
))
def test_course_update(client, param,
                       courses, authenticated_user):
    url_ = urls.reverse(param, args=(courses.id,))
    response = client.get(url_)
    assert response.status_code == 200


@pytest.mark.django_db
@pytest.mark.parametrize('param', (
        'course_module_update',
        'module_content_list'
))
def test_module_update(client, param,
                       modules, authenticated_user):
    url_ = urls.reverse(param, args=(modules.id,))
    response = client.get(url_)
    assert response.status_code == 200


@pytest.mark.django_db
def test_course_create(client, authenticated_user, course_data):
    url_ = urls.reverse('course_create')
    response = client.post(url_, **course_data)
    assert response.status_code == 200


@pytest.mark.django_db
def test_course_module_update(client, authenticated_user,
                              courses, module_data, modules):
    modules.save()
    url_ = urls.reverse('course_module_update', args=(modules.id,))
    response = client.post(url_, {
        'title': 'ddd',
        'course': courses,
        'description': 'ddd'
    })
    assert response.status_code == 200
