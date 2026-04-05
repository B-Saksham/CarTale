from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'is_staff', 'is_superuser')
    list_filter = ('role', 'is_staff', 'is_superuser')

    def save_model(self, request, obj, form, change):
        # Enforce rules
        if not obj.pk:  # New user
            if obj.role == 'user':
                obj.is_staff = False
                obj.is_superuser = False

        super().save_model(request, obj, form, change)
