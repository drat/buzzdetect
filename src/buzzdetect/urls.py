from django.conf.urls import url, include
from django.contrib import admin
from django.views import generic

urlpatterns = [
    url(r'^$', generic.TemplateView.as_view(template_name='index.html')),
    url(r'^admin/', admin.site.urls),
    url(r'^posts/', include('posts.urls', namespace='posts')),
]
