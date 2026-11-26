(() => {
  const exclusion = '-site:reddit.com';
  const url = new URL(location.href);
  if (url.pathname !== '/search') return;

  const query = url.searchParams.get('q');
  if (!query?.trim()) return;

  // A literal inside a quoted phrase is not an active search operator.
  const unquoted = query.replace(/"[^"]*(?:"|$)/gu, '"');
  if (/(?:^|\s)-site:reddit\.com(?=\s|$)/iu.test(unquoted)) return;

  const hasOpenQuote = query.split('"').length % 2 === 0;
  url.searchParams.set('q', hasOpenQuote ? `${exclusion} ${query}` : `${query.trimEnd()} ${exclusion}`);
  // Replace the unfiltered entry so Back doesn't re-trigger the redirect.
  location.replace(url.href);
})();
