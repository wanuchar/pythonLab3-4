from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UserProfile
from .forms import UserProfileCreationForm, UserProfileChangeForm


class UserProfileAdmin(UserAdmin):
    add_form = UserProfileCreationForm
    form = UserProfileChangeForm
    list_display = ('email',
                    'username',
                    'age',
                    'is_teacher',
                    'image')
    model = UserProfile


admin.site.register(UserProfile, UserProfileAdmin)
