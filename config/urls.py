from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('apps.accounts.urls')),
    path('api/', include('apps.checkins.urls')),
    # Enabled app routes
    path('api/', include('apps.habits.urls')),
    # Future: study, community, pricing
    path('api/', include('apps.study.urls')),
    path('api/', include('apps.community.urls')),
    path('api/', include('apps.pricing.urls')),

    # API Docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)