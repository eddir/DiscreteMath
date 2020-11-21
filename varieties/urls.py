from django.urls import path

from varieties import views, api

app_name = 'varieties'

urlpatterns = [
    path('', views.index, name='index'),
    path('api/binary/<str:method>', api.binary),
    path('api/properties/<str:method>', api.properties),
    path('api/truth_table', api.truth_table),
]
