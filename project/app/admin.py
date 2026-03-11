from django.contrib import admin

from app.models import AutomationRun, MarketplaceGroup, MarketplaceListing


@admin.register(MarketplaceListing)
class MarketplaceListingAdmin(admin.ModelAdmin):
    list_display = ("title", "price", "location", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("title", "location")


@admin.register(MarketplaceGroup)
class MarketplaceGroupAdmin(admin.ModelAdmin):
    list_display = ("name", "listing", "reshare_daily", "last_shared_at")
    list_filter = ("reshare_daily",)
    search_fields = ("name", "listing__title")


@admin.register(AutomationRun)
class AutomationRunAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "started_at",
        "completed_at",
        "dry_run",
        "listings_posted",
        "groups_shared",
    )
    list_filter = ("dry_run",)
