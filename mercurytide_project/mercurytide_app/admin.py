from django.contrib import admin
from mercurytide_app.models import Category, Page, UserProfile


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('name',)}

admin.site.register(Category)
admin.site.register(Page)
admin.site.register(UserProfile)