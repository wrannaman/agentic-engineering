---
keywords: kb doc, example, knowledge base, how to write, template, best practice
last_reviewed: 2026-03-26
owner: engineering
---

# What a Great KB Doc Looks Like

This is an annotated example of a high-quality knowledge base document. Use this as a template when writing your own.

---

## The Example

Below is a sanitized KB doc for a scraping service with a fallback chain. Notice the structure — it's designed so an agent can find it, understand the architecture in 30 seconds, and implement a change correctly on the first try.

```markdown
---
keywords: scraping, fallback, WebsiteScraper, ScrapeService, ScreenshotService,
  screenshot, OG tags, social links, ScrapedWebPage, ScrapeResult
---

# Scraping Fallback Infrastructure

Content extraction uses ProviderA (primary) with ProviderB as fallback.
Screenshots use ProviderB (primary) with CloudRenderer as fallback.
All providers return `ScrapeResult` — downstream code is provider-agnostic.

**CloudRenderer is NOT used for scraping.** It was the original fallback but
failed too frequently (datacenter IP reputation, limited anti-bot handling).
ProviderB replaced it because it has residential proxy rotation, JS rendering,
and anti-bot protection. CloudRenderer is only used as a last-resort screenshot
fallback.

## Fallback Chains

**Scraping:** ProviderA (3-min timeout) → ProviderB (markdown + raw HTML in
parallel). If ProviderA errors quickly, ProviderB fires immediately — no 3-min
wait.

**Screenshots:** ProviderA inline screenshot → ProviderB /screenshot →
CloudRenderer → OG image from scrape metadata.

## Adding a New Scraping Provider

Any new provider must:

1. Implement `Task<Result<ScrapeResult>> ScrapeAsync(string url, CancellationToken)`
2. Make parallel requests for markdown + HTML (use `format=raw` to preserve
   `<head>` content)
3. Parse HTML with `ScrapedWebPage.FromHtml(html)` to extract title,
   description, favicon, logo, OG tags
4. Extract social links with `ScrapeService.ExtractSocialLinks(markdown + html)`
   — pass both markdown AND raw HTML since markdown converters strip icon-only
   footer links
5. Register in the DI container with a named HttpClient
6. Wire into `WebsiteScraper.ScrapeWithFallbackAsync()` at the desired position

## Conversion Pattern (Provider → ScrapeResult)

\```cs
// 1. Two parallel requests
var markdownTask = FetchAsync(url, "markdown", ct);
var htmlTask = FetchAsync(url, "raw", ct);      // NEVER clean_html — strips OG tags
await Task.WhenAll(markdownTask, htmlTask);

// 2. Parse HTML for metadata
var page = ScrapedWebPage.FromHtml(html);
var title = page.GetTitle();
var favicon = page.GetFavicon(url);
var ogMeta = page.GetOgMeta();

// 3. Social links from BOTH markdown and HTML
var socialLinks = ScrapeService.ExtractSocialLinks(markdown + "\n" + html);

// 4. Return universal type
return new ScrapeResult
{
    Url = finalUrl, Title = title, Description = description,
    Markdown = markdown, Html = html,
    Logo = logo, Favicon = favicon,
    SocialLinks = socialLinks,
};
\```

## Gotchas

- **`format=raw` not `clean_html`** — `clean_html` strips OG meta tags and
  favicon from `<head>`. This caused missing OG images in early testing.
- **Pass both markdown AND HTML to social link extraction** — markdown converters
  strip icon-only footer links (e.g., a Twitter icon with no text). The raw HTML
  still has them.
- **ProviderA timeout is 3 minutes** — but if it errors quickly (HTTP 500, DNS
  failure), the fallback fires immediately. Don't assume the fallback always
  waits 3 minutes.

## Key Files

- `src/Infrastructure/WebsiteScraper.cs` — fallback orchestration
- `src/Infrastructure/ProviderAService.cs` — primary scraping provider
- `src/Infrastructure/ProviderBService.cs` — fallback scraping provider
- `src/Infrastructure/ScreenshotService.cs` — screenshot fallback chain
```

---

## Why This Doc Works

### 1. Keywords are dense and specific
```
keywords: scraping, fallback, WebsiteScraper, ScrapeService, ScreenshotService,
  screenshot, OG tags, social links, ScrapedWebPage, ScrapeResult
```
Includes the actual class names, not just concepts. An agent searching for `ScrapeResult` or `WebsiteScraper` or `OG tags` finds this doc instantly.

### 2. One-paragraph summary up top
You know exactly what this doc covers in 3 seconds. "ProviderA primary, ProviderB fallback. All return ScrapeResult." An agent reads this and knows whether this doc is relevant before reading further.

### 3. Bold callout for the non-obvious thing
> **CloudRenderer is NOT used for scraping.**

This is the thing an agent would get wrong without this doc. It would see CloudRenderer in the codebase and assume it's a scraping option. The bold callout prevents that.

### 4. Fallback chains as concise lists
Not prose. Not code. Just the chain with the key details (timeouts, when fallback fires). Scannable in 5 seconds.

### 5. "Adding a New Provider" is the pattern template
Numbered steps with the exact interface, exact method names, exact registration pattern. An agent following these steps would get it right on the first try.

### 6. Real code example with the conversion pattern
This is the most valuable part. Not pseudocode — actual code with actual types. Comments explain *why* (`// NEVER clean_html — strips OG tags`), not *what*.

### 7. Gotchas are specific and actionable
Not "be careful with HTML parsing." Instead: "`format=raw` not `clean_html` — `clean_html` strips OG meta tags." Specific cause, specific effect, specific fix.

### 8. Key files with exact paths
The agent knows exactly where to look. No searching, no guessing.

## The Checklist

When writing a KB doc, check:

- [ ] Keywords include the actual class/function/service names from your codebase
- [ ] Opens with a 1-3 sentence summary of what this doc covers
- [ ] Non-obvious things are called out in bold ("X is NOT used for Y")
- [ ] Patterns are numbered steps with exact interfaces and method names
- [ ] Code examples are real code with real types (not pseudocode)
- [ ] Comments in code explain WHY, not WHAT
- [ ] Gotchas are specific: cause → effect → fix
- [ ] Key files listed with exact paths
- [ ] A new engineer (or agent) could follow this doc and get it right on the first try
