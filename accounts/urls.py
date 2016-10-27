from django.conf import settings
from django.conf.urls import url
from django.views.generic.edit import CreateView
from django.contrib.auth.forms import UserCreationForm
import django.contrib.auth.views as auth_views

urlpatterns = [
    url(r'^register/$',
        CreateView.as_view(
            template_name='accounts/form.html',
            form_class=UserCreationForm,
            success_url=settings.LOGIN_REDIRECT_URL
        ),
        name='accounts-register'),
    url(r'^login/$',
        auth_views.login, {'template_name': 'accounts/form.html'},
        name='accounts-login'),
    url(r'^logout/$',
        auth_views.logout, {'template_name': 'accounts/logout.html'},
        name='accounts-logout'),
]
