from django.http import JsonResponse
from django.shortcuts import render

from app.models import AutomationRun, MarketplaceGroup, MarketplaceListing


def index(request):
    return render(request, template_name="app/index.html")


def automation_dashboard(request):
    listings = MarketplaceListing.objects.prefetch_related("groups").order_by("-created_at")
    runs = AutomationRun.objects.order_by("-started_at")[:10]

    context = {
        "listings": listings,
        "runs": runs,
        "listing_count": listings.count(),
        "group_count": MarketplaceGroup.objects.count(),
    }
    return render(request, template_name="app/automation_dashboard.html", context=context)


def automation_data_api(request):
    listings = list(
        MarketplaceListing.objects.filter(is_active=True)
        .values("id", "title", "price", "location", "created_at")
        .order_by("-created_at")
    )
    groups = list(
        MarketplaceGroup.objects.select_related("listing")
        .values(
            "id",
            "name",
            "group_url",
            "reshare_daily",
            "last_shared_at",
            "listing_id",
            "listing__title",
        )
        .order_by("name")
    )
    runs = list(
        AutomationRun.objects.values(
            "id",
            "started_at",
            "completed_at",
            "dry_run",
            "listings_posted",
            "groups_shared",
            "notes",
        ).order_by("-started_at")[:20]
    )

    return JsonResponse(
        {
            "summary": {
                "active_listings": len(listings),
                "groups": len(groups),
                "recent_runs": len(runs),
            },
            "listings": listings,
            "groups": groups,
            "runs": runs,
        }
    )
