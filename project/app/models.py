from django.db import models
from django.utils import timezone


class MarketplaceListing(models.Model):
    title = models.CharField(max_length=150)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    location = models.CharField(max_length=120, blank=True)
    image_path = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.title


class MarketplaceGroup(models.Model):
    listing = models.ForeignKey(
        MarketplaceListing,
        on_delete=models.CASCADE,
        related_name="groups",
    )
    name = models.CharField(max_length=150)
    group_url = models.URLField()
    reshare_daily = models.BooleanField(default=True)
    last_shared_at = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.name} -> {self.listing.title}"

    def needs_daily_reshare(self, now=None) -> bool:
        if not self.reshare_daily:
            return False

        now = now or timezone.now()
        if self.last_shared_at is None:
            return True

        return (now - self.last_shared_at).total_seconds() >= 24 * 60 * 60


class AutomationRun(models.Model):
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    dry_run = models.BooleanField(default=True)
    listings_posted = models.PositiveIntegerField(default=0)
    groups_shared = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True)

    def mark_completed(self, notes: str = "") -> None:
        self.completed_at = timezone.now()
        self.notes = notes
        self.save(update_fields=["completed_at", "notes"])
