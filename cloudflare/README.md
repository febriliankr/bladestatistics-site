# R2 website hosting

`bladestatistics.com` and `www.bladestatistics.com` are routed to the
`blade-website` Cloudflare Worker. It reads the private `blade-website` R2 bucket.
The `SITE_RELEASE` variable selects an immutable `releases/<hash>/` prefix.
The separate installer bucket and `dl.skalatec.com` update feeds are unchanged.

`build.py` stages only public pages, translations, assets, and social images.
It excludes the repository, source templates, credentials, and deployment tools.
`deploy.py` uploads all public files before switching the Worker to the new prefix.
A failed upload leaves the current site serving its existing release.

From this repository, with the existing Cloudflare credentials loaded:

```sh
set -a
. ../blade/secret/cloudflare.env
set +a
python3 cloudflare/deploy.py
```

R2 uploads use `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID`.
The Worker deployment with public routes uses the existing
`CLOUDFLARE_GLOBAL_API_KEY` and `CLOUDFLARE_EMAIL` from the local secret store;
none of these values belongs in Git. Wrangler is pinned in `deploy.py`.
The Blade repository's `make website-deploy` publishes an export of pushed
`origin/master`, so uncommitted work cannot slip into a desktop release.
GitHub Pages is no longer the production host; pushing alone does not deploy.

Verification:

- Every public URL has `X-Blade-Site-Release: <hash>`.
- All thirteen language homepages carry four current installer links.
- `/login/`, `/account/`, and `/billing/success` return `Cache-Control: no-store`.
- `/pricing` redirects to `/pricing/`; billing return URLs work without `.html`.
- `www` and HTTP redirect to the HTTPS apex, preserving paths and query strings.
- Missing paths return 404. Source and deployment files are never staged.

Run routing tests with `node --test cloudflare/worker.test.mjs`.

## Rollback

Old R2 prefixes are retained. To roll back site content, deploy the previous
release value without rebuilding or reuploading (load credentials first):

```sh
unset CLOUDFLARE_API_TOKEN
export CLOUDFLARE_API_KEY="$CLOUDFLARE_GLOBAL_API_KEY"
npx --yes wrangler@4.130.0 deploy --config cloudflare/wrangler.jsonc \
  --var SITE_RELEASE:PREVIOUS_RELEASE_HASH
```

Record the chosen release in `wrangler.jsonc` if keeping it as the baseline.

The initial routing change saved `cloudflare/rollback-dns.json` locally and
ignored it in Git. To restore the previous GitHub Pages DNS/proxy settings and
remove these Worker routes, run `python3 cloudflare/route.py --rollback` with
credentials loaded. Files in R2 and unrelated DNS records are retained.
`route.py` can re-enable the R2 routing. Regular content deployments do not
change DNS. The original GitHub A/CNAME targets remain underneath the proxied
records to make the hosting rollback reversible.

## Initial deployment

On 2026-10-23, release `d3cb1a1ece70f682f0ed` staged 70 public files, including
0.2.33 download links and the sign-in theme toggle from source `bae643c`.
All 70 preview files matched their build SHA-256 before the domain cutover.
Universal SSL was already active. Only apex A records and the `www` CNAME were
proxied; email, API, admin, and other DNS records were preserved.
