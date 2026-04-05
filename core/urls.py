from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include('pages.urls')),     # NEW homepage app
    path('browse/', include('cars.urls')),  # Move cars here
    # bookings
    path('bookings/', include('bookings.urls')),

    # sell car
    path('sell/', include('sell_requests.urls')),

    # store
    path('store/', include('store.urls')),

    # accounts
    path('accounts/', include('accounts.urls')),
    path('blog/', include('blog.urls')),
    
    path('chatbot/', include('chatbot.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)