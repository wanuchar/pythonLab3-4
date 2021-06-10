from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import UserProfile
from courses.models import Course


class UserProfileCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = UserProfile
        fields = ('username',
                  'email',
                  'age',
                  'is_teacher',
                  'image')


class UserProfileChangeForm(UserChangeForm):
    class Meta:
        model = UserProfile
        fields = ('username',
                  'email',
                  'age',
                  'image')


class CourseRegistrationForm(forms.Form):
    course = forms.ModelChoiceField(queryset=Course.objects.all(),
                                    widget=forms.HiddenInput)
