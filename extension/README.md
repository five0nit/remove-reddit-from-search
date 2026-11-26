# remove reddit from search

Desktop Chrome and Microsoft Edge extension. It adds `-site:reddit.com` to Google searches on `www.google.com` and `www.google.com.au` and opens the filtered results in the same tab.

## Install

1. Extract the ZIP to a folder you can keep.
2. Open `chrome://extensions` in Chrome or `edge://extensions` in Edge.
3. Enable **Developer mode** and click **Load unpacked**.
4. Select the extracted `remove-reddit-from-search` folder containing `manifest.json`.
5. Run a Google search. The search box or address bar should show `-site:reddit.com`.

To search without the filter, turn off the extension on the browser's Extensions page and run a new search. Turning it off does not remove the operator from an already filtered query.

## Scope

This extension asks Google to exclude `reddit.com` results. It does not block visits to Reddit or remove Reddit mentions from other websites or Google-generated summaries. It runs only on the listed Google Search hosts, has no background process, and does not store queries or send them anywhere other than Google as part of the search.
