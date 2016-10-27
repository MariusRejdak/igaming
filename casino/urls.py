from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.TableView.as_view(), name='table'),
    url(r'^bank/$', views.BankView.as_view(), name='bank'),
]
