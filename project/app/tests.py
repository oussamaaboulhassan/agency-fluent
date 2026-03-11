from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from app.models import MarketplaceGroup, MarketplaceListing
from app.services.facebook_marketplace import FacebookMarketplaceAutomation


class MarketplaceAutomationTests(TestCase):
    def test_daily_reshare_detection(self):
        listing = MarketplaceListing.objects.create(
            title="Desk Lamp",
            price="20.00",
            description="Like new",
        )
        group = MarketplaceGroup.objects.create(
            listing=listing,
            name="City Buy/Sell",
            group_url="https://example.com/group",
            reshare_daily=True,
        )

        self.assertTrue(group.needs_daily_reshare())
        group.last_shared_at = timezone.now()
        group.save(update_fields=["last_shared_at"])
        self.assertFalse(group.needs_daily_reshare())

    def test_dry_run_workflow_updates_share_time(self):
        listing = MarketplaceListing.objects.create(
            title="Bicycle",
            price="120.00",
            description="Good condition",
        )
        group = MarketplaceGroup.objects.create(
            listing=listing,
            name="Local Market",
            group_url="https://example.com/local-market",
        )

        run = FacebookMarketplaceAutomation(dry_run=True).run()

        group.refresh_from_db()
        self.assertEqual(run.listings_posted, 1)
        self.assertGreaterEqual(run.groups_shared, 1)
        self.assertIsNotNone(group.last_shared_at)

    def test_management_command_runs(self):
        MarketplaceListing.objects.create(
            title="Chair",
            price="35.00",
            description="Wooden chair",
        )

        call_command("run_marketplace_automation")

    def test_automation_dashboard_url(self):
        response = self.client.get("/automation/")
        self.assertEqual(response.status_code, 200)

    def test_automation_data_api_url(self):
        response = self.client.get("/automation/data/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("summary", response.json())
