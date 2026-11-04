#!/usr/bin/env python3
"""Optional browser checks/screenshots; requires Playwright, not needed to build."""
import asyncio
import json
import os
from pathlib import Path
from playwright.async_api import async_playwright

URL = os.environ.get('DIARIO_PREVIEW_URL', 'http://127.0.0.1:8790')
OUT = Path('/workspace/diario-preview')

async def main():
    OUT.mkdir(parents=True, exist_ok=True)
    checks = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        for label, size in [('desktop', dict(width=1440,height=1050)), ('mobile',dict(width=390,height=844))]:
            context = await browser.new_context(viewport=size, device_scale_factor=1, is_mobile=label=='mobile', has_touch=label=='mobile')
            page = await context.new_page()
            errors, remote, failures = [], [], []
            page.on('pageerror', lambda e: errors.append(str(e)))
            page.on('request', lambda r: remote.append(r.url) if not r.url.startswith(URL) else None)
            page.on('response', lambda r: failures.append((r.url,r.status)) if r.status>=400 else None)
            await page.goto(URL, wait_until='networkidle')
            await page.wait_for_selector('#news:not([hidden])')
            assert await page.locator('html').get_attribute('data-theme') == 'dark'
            assert await page.locator('.news-section').count() == 8
            assert await page.locator('.lead h1').count() == 1
            assert await page.locator('#featured article').count() in range(4,7)
            for theme, screenshot in [('dark','noche'),('light','dia')]:
                # Load all lazy thumbnails before taking the full page capture.
                await page.evaluate("async () => { for (const img of document.images) { img.loading='eager'; } await Promise.all([...document.images].map(i => i.decode().catch(()=>{}))); }")
                assert await page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'), 'Horizontal overflow'
                assert await page.evaluate('[...document.images].every(i => i.complete && i.naturalWidth > 0)'), 'Broken image'
                await page.screenshot(path=str(OUT/f'{label}-{screenshot}.png'), full_page=True)
                if theme == 'dark':
                    await page.get_by_role('button',name='Activar modo día').click()
                    await page.reload(wait_until='networkidle')
                    await page.wait_for_selector('#news:not([hidden])')
                    assert await page.locator('html').get_attribute('data-theme') == 'light', 'Theme persistence'
            await page.get_by_role('button',name='Costa Rica',exact=True).click()
            assert 'Costa Rica' in await page.locator('#region-results').text_content()
            await page.get_by_role('link',name='Ediciones anteriores').click()
            await page.wait_for_selector('.archive-card')
            await page.locator('.archive-card').first.click()
            await page.wait_for_selector('#archive-banner:not([hidden])')
            assert 'fecha=' in page.url
            await page.goto(URL+'/fuentes.html',wait_until='networkidle')
            assert await page.locator('.source-region').count() == 5
            assert not errors, errors
            assert not remote, remote
            assert not failures, failures
            checks.append(dict(viewport=label,console_errors=errors,external_requests=remote,http_errors=failures,theme_persistence=True,archive=True,region_filter=True,no_overflow=True))
            await context.close()
        # Relative URLs must also work under a GitHub project Pages subdirectory.
        context = await browser.new_context()
        page = await context.new_page()
        async def route_project(route):
            request = route.request
            rewritten = request.url.replace('/diario-test/', '/', 1)
            response = await context.request.get(rewritten)
            await route.fulfill(response=response)
        await page.route(URL+'/diario-test/**', route_project)
        await page.goto(URL+'/diario-test/index.html', wait_until='networkidle')
        await page.wait_for_selector('#news:not([hidden])')
        checks.append(dict(project_subpath=True))
        # A missing archive is a clear error state, not a silent current-edition fallback.
        await page.goto(URL+'/index.html?fecha=1900-01-01', wait_until='networkidle')
        assert await page.locator('[role=alert]').count() == 1
        checks.append(dict(missing_archive_error=True))
        await browser.close()
    (OUT/'browser-checks.json').write_text(json.dumps(checks,indent=2))
    print(json.dumps(checks,indent=2))

if __name__ == '__main__': asyncio.run(main())
