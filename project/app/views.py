from django.contrib import messages
from django.core.management import call_command
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

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


@require_POST
def run_automation_from_web(request):
    live_mode = request.POST.get("mode") == "live"
    command_args = ["run_marketplace_automation"]
    if live_mode:
        command_args.append("--live")

    call_command(*command_args)

    mode_label = "LIVE" if live_mode else "DRY-RUN"
    messages.success(request, f"Automation executed from web ({mode_label} mode).")
    return redirect("automation-dashboard")


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
