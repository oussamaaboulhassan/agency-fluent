# Agency Fluent - Facebook Marketplace Automation

This project now includes a Python-based automation workflow for:

1. Posting active listings to Facebook Marketplace.
2. Sharing each post to selected Facebook groups.
3. Re-sharing listings daily to selected groups.

## Data model

- `MarketplaceListing`: listing details (title, price, description, location, image path).
- `MarketplaceGroup`: groups to share into per listing + daily reshare flag.
- `AutomationRun`: history of each automation execution.

## Run the automation

Dry run (default, safe for testing):

```bash
python manage.py run_marketplace_automation
```

Live browser mode:

```bash
python manage.py run_marketplace_automation --live
```

## Important

- Live mode uses Playwright selectors that can change when Facebook updates UI.
- Keep a logged-in browser profile/session available for reliable operation.
- Ensure your usage complies with Facebook terms and local regulations.

## Schedule daily execution

Use cron (Linux) to run daily at 9 AM:

```bash
0 9 * * * cd /workspace/agency-fluent/project && /usr/bin/python3 manage.py run_marketplace_automation
```
