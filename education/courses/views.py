import logging

from django.db import transaction
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.views.generic.list import ListView
from .models import Course, Subject
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import redirect, get_object_or_404, render
from django.views.generic.base import TemplateResponseMixin, View, TemplateView
from .forms import ModuleFormSet
from django.forms.models import modelform_factory
from django.apps import apps
from .models import Module, Content
from django.db.models import Count
from django.views.generic.detail import DetailView
from users.forms import CourseRegistrationForm
from .mixins import OwnerCourseEditMixin, OwnerEditMixin, OwnerCourseMixin, OwnerMixin

logger = logging.getLogger(__name__)
message_ = '| user: %s | used: %s | method: %s'


class ManageCourseListView(ListView):
    model = Course
    # model = Module
    template_name = 'courses/manage/course/list.html'

    def get_queryset(self):
        logger.info(message_ % (f'{self.request.user}',
                                f'{self.__class__.__name__}',
                                'get_queryset'))
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user)


class CourseCreateView(OwnerCourseEditMixin,
                       OwnerEditMixin,
                       CreateView,
                       PermissionRequiredMixin):
    permission_required = 'courses.add_course'


class CourseUpdateView(OwnerCourseEditMixin,
                       UpdateView,
                       PermissionRequiredMixin):
    permission_required = 'courses.change_course'


class CourseDeleteView(OwnerCourseMixin,
                       DeleteView,
                       PermissionRequiredMixin):
    template_name = 'courses/manage/course/delete.html'
    success_url = reverse_lazy('manage_course_list')
    permission_required = 'courses.delete_course'


class CourseModuleUpdateView(TemplateResponseMixin, View):
    template_name = 'courses/manage/module/formset.html'
    course = None

    def get_formset(self, data=None):
        logger.info(message_ % (f'{self.request.user}',
                                f'{self.__class__.__name__}',
                                'get_queryset'))
        return ModuleFormSet(instance=self.course,
                             data=data)

    def dispatch(self, request, pk):
        logger.info(message_ % (f'{self.request.user}',
                                f'{self.__class__.__name__}',
                                'dispatch'))
        try:
            self.course = Course.objects.get(id=pk,
                                             owner=request.user)
        except Course.DoesNotExist:
            logger.warning('')
        return super().dispatch(request, pk)

    def get(self, request, *args, **kwargs):
        logger.info(message_ % (f'{self.request.user}',
                                f'{self.__class__.__name__}',
                                'get'))
        formset = self.get_formset()
        return self.render_to_response(
            {'course': self.course,
             'formset': formset}
        )

    def post(self, request, *args, **kwargs):
        logger.info(message_ % (f'{self.request.user}',
                                f'{self.__class__.__name__}',
                                'post'))
        formset = self.get_formset(data=request.POST)
        if formset.is_valid():
            formset.save()
            return redirect('manage_course_list')
        logger.warning(f'user: {self.request.user} | form is not valid')
        return self.render_to_response(
            {'course': self.course,
             'formset': formset}
        )


class ContentCreateUpdateView(TemplateResponseMixin, View):
    module = None
    model = None
    obj = None
    template_name = 'courses/manage/content/form.html'

    def dispatch(self, request, module_id, model_name, id=None):
        logger.info(message_ % (f'{self.request.user}',
                                f'{self.__class__.__name__}',
                                'dispatch'))
        try:
            self.module = Module.objects.get(id=module_id,
                                             course__owner=request.user)
        except Module.DoesNotExist:
            logger.warning(f'user: {self.request.user} | '
                           f'no {self.model} matches the given query')
            return HttpResponse(status=400)
        self.model = self.get_model(model_name)
        if id:
            try:
                self.obj = self.model.objects.get(id=id,
                                                  owner=request.user)
            except self.model.DoesNotExist:
                logger.warning(f'user: {self.request.user} | '
                               f'no {self.model} matches the given query')
                return HttpResponse(status=400)
        return super().dispatch(request, module_id, model_name, id)

    def get(self, request, module_id, model_name, id=None):
        logger.info(message_ % (f'{self.request.user}',
                                f'{self.__class__.__name__}',
                                'get'))
        form = self.get_form(self.model,
                             instance=self.obj)
        return self.render_to_response(
            {'form': form,
             'object': self.obj}
        )

    def post(self, request, module_id, model_name, id=None):
        logger.info(message_ % (f'{self.request.user}',
                                f'{self.__class__.__name__}',
                                'post'))
        form = self.get_form(self.model,
                             instance=self.obj,
                             data=request.POST,
                             files=request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            obj.save()
            if not id:
                Content.objects.create(module=self.module,
                                       item=obj)
            return redirect('module_content_list',
                            self.module.id)
        logger.warning(f'user: {self.request.user} | form is not valid')
        return self.render_to_response(
            {'form': form,
             'object': self.obj}
        )

    @staticmethod
    def get_model(model_name):
        if model_name in ('text', 'picture', 'video', 'file'):
            return apps.get_model(app_label='courses',
                                  model_name=model_name)
        logger.warning(f'model {model_name} does not exist')
        return None

    @staticmethod
    def get_form(model, *args, **kwargs):
        form_ = modelform_factory(model, exclude=('owner',
                                                  'order',
                                                  'created',
                                                  'updated'))
        return form_(*args, **kwargs)


class ContentDeleteView(View):
    def post(self, request, id):
        try:
            content = Content.objects.get(id=id,
                                          module__course__owner=request.user)
        except Content.DoesNotExist:
            logger.info(message_ % (f'{self.request.user}',
                                    f'{self.__class__.__name__}',
                                    'post'))
            return HttpResponse('Error', status=404)
        logger.info(message_ % (f'{self.request.user}',
                                f'{self.__class__.__name__}',
                                'post'))
        module = content.module
        content.item.delete()
        content.delete()
        return redirect('module_content_list', module.id)


class ModuleContentListView(TemplateResponseMixin, View):
    template_name = 'courses/manage/module/content_list.html'

    def get(self, request, module_id):
        try:
            module = Module.objects.get(id=module_id,
                                        course__owner=request.user)
            logger.info(message_ % (f'{self.request.user}',
                                    f'{self.__class__.__name__}',
                                    'get'))
            return self.render_to_response({'module': module})
        except Module.DoesNotExist:
            logger.warning(f'user: {self.request.user} | '
                           f'no {Module} matches the given query')
            return HttpResponseRedirect('course_list')


class CourseListView(TemplateResponseMixin, View):
    model = Course
    template_name = 'courses/course/list.html'

    def get(self, request, subject=None):
        logger.info(message_ % (f'{self.request.user}',
                                f'{self.__class__.__name__}',
                                'get'))
        courses = Course.objects.annotate(
            total_modules=Count('modules')
        )
        if subject:
            with transaction.atomic():
                try:
                    subject = Subject.objects.get(slug=subject)
                    courses = courses.filter(subject=subject)
                except Subject.DoesNotExist:
                    logger.warning(f'user: {self.request.user} | '
                                   f'no {subject} matches the given query')
                    return HttpResponse('Error', status=404)
        return self.render_to_response({'subject': subject,
                                        'courses': courses})


class CourseDetailView(DetailView):
    model = Course
    template_name = 'courses/course/detail.html'

    def get_context_data(self, **kwargs):
        logger.info(message_ % (f'{self.request.user}',
                                f'{self.__class__.__name__}',
                                'get_context_data'))
        context = super().get_context_data(**kwargs)
        context['registration_form'] = CourseRegistrationForm(
            initial={'course': self.object})
        return context


