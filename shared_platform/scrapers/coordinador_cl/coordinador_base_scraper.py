#!/usr/bin/env python3
"""
Base scraper class for Coordinador.cl
Shared functionality that all domain scrapers can inherit from
"""

import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright
from abc import ABC, abstractmethod

class CoordinadorBaseScraper(ABC):
    """Base class for all coordinador.cl domain scrapers"""

    def __init__(self, domain_name: str):
        self.domain_name = domain_name
        self.base_url = "https://www.coordinador.cl"
        self.patterns = self._load_patterns()

        # Each domain saves to its own extractions folder
        project_root = Path(__file__).parent.parent.parent.parent
        self.output_dir = project_root / "domains" / domain_name / "extractions"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _load_patterns(self):
        """Load shared scraping patterns"""
        patterns_dir = Path(__file__).parent / "patterns"
        patterns = {}

        for pattern_file in patterns_dir.glob("*.json"):
            if pattern_file.exists():
                with open(pattern_file, 'r', encoding='utf-8') as f:
                    patterns[pattern_file.stem] = json.load(f)

        return patterns

    async def create_browser_context(self):
        """Create browser context with coordinador.cl optimized settings"""
        p = await async_playwright().start()

        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-gpu',
                '--disable-extensions'
            ]
        )

        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            viewport={'width': 1920, 'height': 1080}
        )

        return p, browser, context

    async def navigate_to_section(self, page, section_path: str):
        """Navigate to specific coordinador.cl section"""
        full_url = f"{self.base_url}/{section_path}"

        try:
            response = await page.goto(full_url, wait_until='domcontentloaded', timeout=30000)
            if response and response.status == 200:
                await page.wait_for_timeout(2000)  # Wait for dynamic content
                return True
            return False
        except Exception as e:
            print(f"Failed to navigate to {full_url}: {e}")
            return False

    async def extract_common_elements(self, page):
        """Extract common elements present in all coordinador.cl pages"""
        return await page.evaluate("""
            () => ({
                navigation_links: Array.from(document.querySelectorAll('nav a')).map(a => ({
                    text: a.textContent.trim(),
                    href: a.href
                })),
                search_forms: Array.from(document.querySelectorAll('form[action*="busqueda"]')).map(f => ({
                    action: f.action,
                    method: f.method,
                    inputs: Array.from(f.querySelectorAll('input')).map(i => ({
                        type: i.type,
                        name: i.name,
                        placeholder: i.placeholder
                    }))
                })),
                data_tables: Array.from(document.querySelectorAll('table')).map(t => ({
                    id: t.id,
                    classes: t.className,
                    headers: Array.from(t.querySelectorAll('th')).map(th => th.textContent.trim()),
                    rows: t.rows.length
                })),
                download_links: Array.from(document.querySelectorAll('a[href*=".pdf"], a[href*=".xls"], a[href*=".doc"]')).map(a => ({
                    text: a.textContent.trim(),
                    href: a.href,
                    type: a.href.split('.').pop()
                }))
            })
        """)

    def save_extraction(self, data: dict, filename: str):
        """Save extraction data to domain's extractions folder"""
        filepath = self.output_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"💾 Saved {self.domain_name} extraction: {filepath}")

    @abstractmethod
    async def scrape_domain_data(self, page):
        """Each domain implements its specific scraping logic"""
        pass

    async def run_scraper(self, section_paths: list):
        """Main scraper execution method"""
        p, browser, context = await self.create_browser_context()

        try:
            page = await context.new_page()

            for section_path in section_paths:
                print(f"🔍 Scraping {self.domain_name}: {section_path}")

                if await self.navigate_to_section(page, section_path):
                    # Extract common elements
                    common_data = await self.extract_common_elements(page)

                    # Extract domain-specific data
                    domain_data = await self.scrape_domain_data(page)

                    # Combine and save
                    extraction = {
                        'domain': self.domain_name,
                        'section_path': section_path,
                        'timestamp': str(Path().cwd()),
                        'common_elements': common_data,
                        'domain_specific': domain_data
                    }

                    filename = f"{self.domain_name}_{section_path.replace('/', '_')}_extraction.json"
                    self.save_extraction(extraction, filename)
                else:
                    print(f"❌ Failed to load section: {section_path}")

        finally:
            await browser.close()
            await p.stop()