import logging
from django.contrib.auth.models import Group
from django.shortcuts import redirect
from django.urls import reverse_lazy
from .forms import UserProfileCreationForm, CourseRegistrationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views import generic
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from courses.models import Course
from .models import UserProfile
from django.contrib import messages

logger = logging.getLogger(__name__)
message_ = '| user: %s | used: %s | method: %s'


class SignUpView(generic.CreateView):
    template_name = 'users/signup.html'
    form_class = UserProfileCreationForm
    success_url = reverse_lazy('user_course_list')

    def post(self, request, *args, **kwargs):
        form = UserProfileCreationForm(request.POST)
        email = request.POST.get('email')
        if UserProfile.objects.filter(email=email).exists():
            logger.error(f'{self.request.user} | already registered')
            messages.error(request, 'Вы уже зарегистрированы.')
        else:
            if form.is_valid():
                logger.info(message_ % (f'{self.request.user}',
                                        f'{self.__class__.__name__}',
                                        'form is valid'))
                user = form.save(commit=False)
                user.save()
                if request.POST.get('is_teacher'):
                    user_group = Group.objects.get(name='Преподаватель')
                    user.groups.add(user_group)
                return redirect('login')
            logger.warning(f'user: {self.request.user} | form is not valid')
        return self.render_to_response({'form': form})

    def form_valid(self, form):
        result = super().form_valid(form)
        cd = form.cleaned_data
        user = authenticate(username=cd['username'],
                            password=cd['password1'])
        login(self.request, user)
        return result


class UserRegistrationCoursesView(LoginRequiredMixin, FormView):
    course = None
    form_class = CourseRegistrationForm

    def form_valid(self, form):
        logger.info(message_ % (f'{self.request.user}',
                                f'{self.__class__.__name__}',
                                'form_valid'))
        self.course = form.cleaned_data['course']
        self.course.users.add(self.request.user)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('user_course_detail',
                            args=[self.course.id])


class UserCourseListView(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'users/course/list.html'

    def get_queryset(self):
        logger.info(message_ % (f'{self.request.user}',
                                f'{self.__class__.__name__}',
                                'get_queryset'))
        qs = super().get_queryset()
        return qs.filter(users__in=[self.request.user])


class UserCourseDetailView(DetailView):
    model = Course
    template_name = 'users/course/detail.html'

    def get_queryset(self):
        logger.info(message_ % (f'{self.request.user}',
                                f'{self.__class__.__name__}',
                                'get_queryset'))
        qs = super().get_queryset()
        return qs.filter(users__in=[self.request.user])

    def get_context_data(self, **kwargs):
        logger.info(message_ % (f'{self.request.user}',
                                f'{self.__class__.__name__}',
                                'get_queryset'))
        context = super().get_context_data(**kwargs)
        course = self.get_object()
        if 'module_id' in self.kwargs:
            context['module'] = course.modules.get(id=self.kwargs['module_id'])
        else:
            context['module'] = course.modules.all().first()
        return context
