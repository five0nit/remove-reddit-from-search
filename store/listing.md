# remove reddit from search — Chrome Web Store submission draft

## Package and visibility

- Upload only `remove-reddit-from-search-store.zip` as the extension package. The outer submission kit contains separate assets and is not an extension upload.
- Proposed visibility: **Unlisted** (confirm with the account owner). Turn off automatic publishing when submitting for review so approval does not put the listing live automatically.
- Upload `icon128.png` for the icon, `promo440x280.png` for the optional small promo tile, and an actual 1280 × 800 Google results screenshot showing the filter. Do not upload a fixture as a live product screenshot.
- Host `privacy.html` at a public HTTPS URL and use that URL for the privacy policy field. This file is a draft, not a hosted policy.

## Store description

The extension automatically adds `-site:reddit.com` to searches on `www.google.com` and `www.google.com.au`, asking Google to exclude Reddit links from results. It does not change Chrome’s default search engine or block direct visits to Reddit. It is independent of Reddit and Google.

## Privacy practices

**Single purpose:** Exclude Reddit links from Google Search by adding `-site:reddit.com` to the Google query.

**Site access justification:** The extension matches the search paths on `www.google.com` and `www.google.com.au`. It reads the query parameter `q`, adds the exclusion if missing, and reloads results on the same Google host. It does not run on unrelated hosts and does not change Chrome search settings.

**Remote code:** No. The content script is bundled.

**Data handling disclosure:** The search query is processed in the browser, and Google receives the modified query as a normal search request. The extension does not keep its own log or history, use analytics, or send queries to the publisher. The account owner should review Google’s current disclosure and certification prompts before certifying.

## Reviewer test instructions

1. Install and enable the extension. No extension account is required.
2. On `https://www.google.com`, search for `mechanical keyboard recommendations`. Verify the query becomes `mechanical keyboard recommendations -site:reddit.com`.
3. Reload once to verify the filter is not duplicated. Then visit `https://www.reddit.com` directly to verify the extension does not block the site.

The extension automatically rewrites Google queries; disclose this explicitly. It does not override the default provider. Chrome Web Store review determines whether that distinction satisfies the current policy.
