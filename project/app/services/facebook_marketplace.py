from dataclasses import dataclass

from django.utils import timezone

from app.models import AutomationRun, MarketplaceGroup, MarketplaceListing


@dataclass
class AutomationStats:
    listings_posted: int = 0
    groups_shared: int = 0


class FacebookMarketplaceAutomation:
    """
    Browser-assisted workflow for posting listings and sharing them to selected groups.

    Notes:
    - The script assumes a persistent browser profile where the user is already logged in.
    - Facebook can change selectors often, so selector updates may be required.
    """

    def __init__(self, *, dry_run: bool = True):
        self.dry_run = dry_run

    def run(self) -> AutomationRun:
        run = AutomationRun.objects.create(dry_run=self.dry_run)
        stats = AutomationStats()

        for listing in MarketplaceListing.objects.filter(is_active=True):
            posted_url = self.post_listing(listing)
            if posted_url:
                stats.listings_posted += 1

            groups = MarketplaceGroup.objects.filter(listing=listing)
            for group in groups:
                if not posted_url:
                    continue
                if self.share_to_group(posted_url, group):
                    stats.groups_shared += 1

        for group in MarketplaceGroup.objects.select_related("listing"):
            if not group.needs_daily_reshare():
                continue
            if self.reshare_listing(group):
                stats.groups_shared += 1

        run.listings_posted = stats.listings_posted
        run.groups_shared = stats.groups_shared
        run.save(update_fields=["listings_posted", "groups_shared"])
        run.mark_completed("Completed posting and sharing workflow.")
        return run

    def post_listing(self, listing: MarketplaceListing) -> str | None:
        if self.dry_run:
            return f"https://www.facebook.com/marketplace/item/mock-{listing.id}"

        return self._post_listing_with_playwright(listing)

    def share_to_group(self, post_url: str, group: MarketplaceGroup) -> bool:
        if self.dry_run:
            group.last_shared_at = timezone.now()
            group.save(update_fields=["last_shared_at"])
            return True

        shared = self._share_post_with_playwright(post_url=post_url, group=group)
        if shared:
            group.last_shared_at = timezone.now()
            group.save(update_fields=["last_shared_at"])
        return shared

    def reshare_listing(self, group: MarketplaceGroup) -> bool:
        post_url = f"https://www.facebook.com/marketplace/item/mock-{group.listing_id}"
        return self.share_to_group(post_url=post_url, group=group)

    def _post_listing_with_playwright(self, listing: MarketplaceListing) -> str | None:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto("https://www.facebook.com/marketplace/create/item")
            page.fill("input[aria-label='Title']", listing.title)
            page.fill("input[aria-label='Price']", str(listing.price))
            page.fill("textarea[aria-label='Description']", listing.description)
            if listing.location:
                page.fill("input[aria-label='Location']", listing.location)
            if listing.image_path:
                page.set_input_files("input[type='file']", listing.image_path)
            page.click("text=Next")
            page.click("text=Publish")
            page.wait_for_timeout(3000)
            url = page.url
            browser.close()
            return url

    def _share_post_with_playwright(self, *, post_url: str, group: MarketplaceGroup) -> bool:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto(post_url)
            page.click("text=Share")
            page.click("text=Share to a group")
            page.fill("input[aria-label='Search groups']", group.name)
            page.click(f"text={group.name}")
            page.fill("div[role='textbox']", "Re-sharing this listing.")
            page.click("text=Post")
            page.wait_for_timeout(2000)
            browser.close()
            return True
