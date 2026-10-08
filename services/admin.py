from django.contrib import admin

from .models import ChecklistItem, Holiday, Service, SiteInfo, Step, WorkingDay


class ChecklistInline(admin.TabularInline):
    model = ChecklistItem
    extra = 1
    ordering = ("order",)


class StepInline(admin.TabularInline):
    model = Step
    extra = 1
    ordering = ("order",)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name_en", "slug", "order", "is_featured")
    prepopulated_fields = {"slug": ("name_en",)}
    inlines = [ChecklistInline, StepInline]


@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = ("date", "name_en", "name_ne")


@admin.register(WorkingDay)
class WorkingDayAdmin(admin.ModelAdmin):
    list_display = ("day", "open_time", "close_time", "note_en")


@admin.register(SiteInfo)
class SiteInfoAdmin(admin.ModelAdmin):
    list_display = ("label_en", "key", "order")
