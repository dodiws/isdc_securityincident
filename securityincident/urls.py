from django.conf.urls import include, patterns, url
from tastypie.api import Api
from .views import (
    getSAMParameters,
    getIncidentsRaw,
    SecurityStatisticResource,
)
from django.conf.urls import include, patterns, url
from tastypie.api import Api

api = Api(api_name='geoapi')

api.register(getSAMParameters())
api.register(getIncidentsRaw())
api.register(SecurityStatisticResource())

urlpatterns = [
    url(r'', include(api.urls)),
]
