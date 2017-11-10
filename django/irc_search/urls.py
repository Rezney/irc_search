from django.conf.urls import url, include
from django.contrib import admin
from core.views import SearchView, LookAroundView, HomeView, ResultsView
from django.conf import settings


urlpatterns = [
    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^search/', SearchView.as_view(), name='search'),
    url(r'^results/', ResultsView.as_view(), name='results'),
    url(r'^lookaround/(?P<channel>.{1,49})/(?P<message_id>\d+)$',
        LookAroundView.as_view(), name='lookaround'),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
