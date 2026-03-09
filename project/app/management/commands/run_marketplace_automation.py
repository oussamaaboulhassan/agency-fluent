from django.core.management.base import BaseCommand

from app.services.facebook_marketplace import FacebookMarketplaceAutomation


class Command(BaseCommand):
    help = "Post active marketplace listings, share to selected groups, and reshare due groups."

    def add_arguments(self, parser):
        parser.add_argument(
            "--live",
            action="store_true",
            help="Execute browser automation. Default mode is dry-run.",
        )

    def handle(self, *args, **options):
        dry_run = not options["live"]
        service = FacebookMarketplaceAutomation(dry_run=dry_run)
        run = service.run()
        self.stdout.write(
            self.style.SUCCESS(
                f"Run #{run.id} completed (dry_run={run.dry_run}) | "
                f"listings_posted={run.listings_posted} groups_shared={run.groups_shared}"
            )
        )
