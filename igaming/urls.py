from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = [
    url(r'^', include('casino.urls')),
    url(r'^accounts/', include('accounts.urls')),
    url(r'^admin/', admin.site.urls),
]
