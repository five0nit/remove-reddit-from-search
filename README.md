# remove reddit from search

A Chrome extension that adds `-site:reddit.com` to searches on `www.google.com` and `www.google.com.au`. It does not change your default search engine or block direct visits to Reddit.

## Install on Chrome

**Chrome Web Store: not live yet.** Once published, open the [Chrome Web Store listing](https://chromewebstore.google.com/detail/lckbehoejpjlgaoeameonanmdoilagkk), click **Add to Chrome**, and confirm. No Developer mode needed for the Store install.

**Manual install now:** [Download `remove-reddit-from-search.zip`](https://github.com/five0nit/remove-reddit-from-search/releases/download/v1.0.3/remove-reddit-from-search.zip).

1. Extract the ZIP to a folder you can keep.
2. Open `chrome://extensions` in desktop Chrome.
3. Turn on **Developer mode**, choose **Load unpacked**, and select the extracted `remove-reddit-from-search` folder containing `manifest.json`.
4. Run a new Google search and look for `-site:reddit.com` in the query.

The GitHub download is not a Chrome Web Store installer. To pause the filter, switch off the extension in `chrome://extensions`, then run a new search.

## Privacy

The filter reads the query from the Google search URL in your browser. Google receives the modified query as a normal search request. The extension does not log queries or send them to the developer. See the [privacy policy](PRIVACY.md).

## Build and test

Source is in [`extension/`](extension/). The extension has no runtime dependencies. For building, use Python 3.10+, Pillow, and the DejaVu Sans fonts. For tests, use Node.js 18+ and, for the offline browser smoke test, Chromium, OpenSSL, and the Python `websockets` package (14+).

```sh
node --test test/filter-search.test.cjs
python3 store/build-store.py
python3 test/browser-smoke.py /path/to/chromium remove-reddit-from-search.zip
```

The build produces `remove-reddit-from-search.zip` for manual installation and `store/remove-reddit-from-search-store.zip` for the Chrome Web Store Developer Dashboard. Only run the smoke test against a trusted build. It uses a disposable browser profile and offline fixtures, not live Google results.

Independent of Google and Reddit.
