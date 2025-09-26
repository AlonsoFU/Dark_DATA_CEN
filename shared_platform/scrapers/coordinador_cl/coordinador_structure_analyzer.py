#!/usr/bin/env python3
"""
Coordinador.cl Structure Analyzer
Comprehensive analysis of the Coordinador Eléctrico Nacional website structure
"""

import asyncio
import json
import time
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright

class CoordinadorStructureAnalyzer:
    def __init__(self):
        self.base_url = "https://www.coordinador.cl/"
        self.results = {}
        self.screenshots_dir = Path(__file__).parent.parent / "data" / "screenshots"
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)

    async def analyze_page_structure(self):
        """Comprehensive analysis of the website structure"""
        print("🔍 Starting Coordinador.cl structure analysis...")

        async with async_playwright() as p:
            # Launch browser with anti-detection settings
            browser = await p.chromium.launch(
                headless=True,  # Use headless mode for better compatibility
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--disable-gpu',
                    '--disable-extensions',
                    '--disable-web-security',
                    '--ignore-certificate-errors'
                ]
            )

            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080}
            )

            page = await context.new_page()

            # Add stealth scripts
            await page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined})
                Object.defineProperty(navigator, 'languages', {get: () => ['es-ES', 'es', 'en']})
                Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})
            """)

            try:
                # Navigate to the site
                print(f"📡 Loading {self.base_url}")
                response = await page.goto(self.base_url, wait_until='domcontentloaded', timeout=60000)

                if response.status == 200:
                    print("✅ Page loaded successfully")
                    await self.full_structure_analysis(page)
                else:
                    print(f"❌ Failed to load page. Status: {response.status}")

            except Exception as e:
                print(f"❌ Error loading page: {e}")
                # Try alternative approaches
                await self.fallback_analysis(page)

            finally:
                await browser.close()

        return self.results

    async def full_structure_analysis(self, page):
        """Perform comprehensive structure analysis"""
        print("🔬 Analyzing page structure...")

        # Basic page info
        await self.get_basic_info(page)

        # Wait for content to load
        await page.wait_for_timeout(3000)

        # Navigation structure
        await self.analyze_navigation(page)

        # Content sections
        await self.analyze_content_sections(page)

        # Forms and inputs
        await self.analyze_forms(page)

        # Data tables
        await self.analyze_tables(page)

        # Dynamic content
        await self.analyze_dynamic_content(page)

        # JavaScript frameworks
        await self.detect_frameworks(page)

        # Links and resources
        await self.analyze_links(page)

        # Take screenshot
        await self.take_screenshot(page)

        # Save results
        await self.save_results()

    async def get_basic_info(self, page):
        """Get basic page information"""
        self.results['basic_info'] = {
            'url': page.url,
            'title': await page.title(),
            'timestamp': datetime.now().isoformat(),
            'viewport_size': page.viewport_size,
        }

        # Page load metrics
        self.results['performance'] = await page.evaluate("""
            () => {
                const timing = performance.timing;
                return {
                    load_time: timing.loadEventEnd - timing.navigationStart,
                    dom_ready: timing.domContentLoadedEventEnd - timing.navigationStart,
                    first_paint: performance.getEntriesByType('paint')[0]?.startTime || null
                }
            }
        """)

        print(f"📄 Page title: {self.results['basic_info']['title']}")

    async def analyze_navigation(self, page):
        """Analyze navigation structure"""
        print("🧭 Analyzing navigation...")

        nav_data = await page.evaluate("""
            () => {
                const navElements = document.querySelectorAll('nav, .nav, .navbar, .navigation, .menu');
                const links = document.querySelectorAll('a[href]');

                return {
                    nav_elements: Array.from(navElements).map(nav => ({
                        tag: nav.tagName,
                        classes: nav.className,
                        id: nav.id,
                        text: nav.textContent.substring(0, 200)
                    })),
                    total_links: links.length,
                    internal_links: Array.from(links).filter(a =>
                        a.href.includes(window.location.hostname) ||
                        a.href.startsWith('/') ||
                        a.href.startsWith('#')
                    ).length,
                    main_menu_items: Array.from(document.querySelectorAll('nav a, .nav a, .navbar a')).map(a => ({
                        text: a.textContent.trim(),
                        href: a.href,
                        classes: a.className
                    })).slice(0, 20)
                }
            }
        """)

        self.results['navigation'] = nav_data
        print(f"🔗 Found {nav_data['total_links']} total links, {nav_data['internal_links']} internal")

    async def analyze_content_sections(self, page):
        """Analyze main content sections"""
        print("📑 Analyzing content sections...")

        content_data = await page.evaluate("""
            () => {
                const sections = {
                    headers: Array.from(document.querySelectorAll('h1, h2, h3, h4, h5, h6')).map(h => ({
                        tag: h.tagName,
                        text: h.textContent.trim().substring(0, 100),
                        id: h.id,
                        classes: h.className
                    })),
                    main_sections: Array.from(document.querySelectorAll('main, section, article, .content, .main')).map(s => ({
                        tag: s.tagName,
                        id: s.id,
                        classes: s.className,
                        children_count: s.children.length
                    })),
                    data_containers: Array.from(document.querySelectorAll('.data, .chart, .graph, .table-container, [data-id], [data-url], [data-type]')).map(d => ({
                        tag: d.tagName,
                        id: d.id,
                        classes: d.className,
                        data_attributes: Array.from(d.attributes).filter(attr => attr.name.startsWith('data-')).map(attr => attr.name)
                    }))
                }
                return sections;
            }
        """)

        self.results['content_sections'] = content_data
        print(f"📋 Found {len(content_data['headers'])} headers, {len(content_data['main_sections'])} main sections")

    async def analyze_forms(self, page):
        """Analyze forms and input elements"""
        print("📝 Analyzing forms...")

        forms_data = await page.evaluate("""
            () => {
                const forms = Array.from(document.querySelectorAll('form')).map(form => ({
                    action: form.action,
                    method: form.method,
                    id: form.id,
                    classes: form.className,
                    inputs: Array.from(form.querySelectorAll('input, select, textarea')).map(input => ({
                        type: input.type || input.tagName,
                        name: input.name,
                        id: input.id,
                        placeholder: input.placeholder,
                        required: input.required
                    }))
                }));

                const searchElements = Array.from(document.querySelectorAll('input[type="search"], .search, [placeholder*="search"], [placeholder*="buscar"]')).map(el => ({
                    type: el.type,
                    placeholder: el.placeholder,
                    id: el.id,
                    classes: el.className
                }));

                return { forms, search_elements: searchElements };
            }
        """)

        self.results['forms'] = forms_data
        print(f"📄 Found {len(forms_data['forms'])} forms, {len(forms_data['search_elements'])} search elements")

    async def analyze_tables(self, page):
        """Analyze data tables"""
        print("📊 Analyzing tables...")

        tables_data = await page.evaluate("""
            () => {
                const tables = Array.from(document.querySelectorAll('table')).map(table => ({
                    id: table.id,
                    classes: table.className,
                    rows: table.rows.length,
                    columns: table.rows[0]?.cells.length || 0,
                    headers: Array.from(table.querySelectorAll('th')).map(th => th.textContent.trim()),
                    caption: table.caption?.textContent || null
                }));

                const dataGrids = Array.from(document.querySelectorAll('.grid, .data-grid, .table-responsive, [role="grid"]')).map(grid => ({
                    tag: grid.tagName,
                    id: grid.id,
                    classes: grid.className,
                    children_count: grid.children.length
                }));

                return { tables, data_grids: dataGrids };
            }
        """)

        self.results['tables'] = tables_data
        print(f"📈 Found {len(tables_data['tables'])} tables, {len(tables_data['data_grids'])} data grids")

    async def analyze_dynamic_content(self, page):
        """Analyze dynamic and JavaScript content"""
        print("⚡ Analyzing dynamic content...")

        # Wait for potential dynamic content
        await page.wait_for_timeout(2000)

        dynamic_data = await page.evaluate("""
            () => {
                const charts = document.querySelectorAll('canvas, svg, .chart, .graph, [id*="chart"], [class*="chart"]');
                const loadingElements = document.querySelectorAll('.loading, .spinner, [data-loading]');
                const ajaxContainers = document.querySelectorAll('[data-url], [data-endpoint], .ajax-content');

                // Check for common JS frameworks
                const frameworks = {
                    react: !!window.React || !!document.querySelector('[data-reactroot]'),
                    angular: !!window.angular || !!document.querySelector('[ng-app], [data-ng-app]'),
                    vue: !!window.Vue || !!document.querySelector('[data-v-]'),
                    jquery: !!window.jQuery || !!window.$
                };

                return {
                    charts_count: charts.length,
                    loading_elements: loadingElements.length,
                    ajax_containers: ajaxContainers.length,
                    frameworks_detected: frameworks,
                    dynamic_elements: Array.from(charts).map(el => ({
                        tag: el.tagName,
                        id: el.id,
                        classes: el.className
                    })).slice(0, 10)
                };
            }
        """)

        self.results['dynamic_content'] = dynamic_data
        print(f"⚡ Found {dynamic_data['charts_count']} charts/graphs")

    async def detect_frameworks(self, page):
        """Detect JavaScript frameworks and libraries"""
        print("🔧 Detecting frameworks...")

        frameworks = await page.evaluate("""
            () => {
                const detected = {};

                // Common frameworks/libraries
                const checks = {
                    'React': () => !!(window.React || document.querySelector('[data-reactroot]')),
                    'Angular': () => !!(window.angular || document.querySelector('[ng-app]')),
                    'Vue': () => !!(window.Vue || document.querySelector('[data-v-]')),
                    'jQuery': () => !!(window.jQuery || window.$),
                    'Bootstrap': () => !!document.querySelector('.container, .row, .col-'),
                    'Chart.js': () => !!window.Chart,
                    'D3.js': () => !!window.d3,
                    'Highcharts': () => !!window.Highcharts,
                    'Google Analytics': () => !!(window.gtag || window.ga),
                    'Google Maps': () => !!window.google?.maps
                };

                for (const [name, check] of Object.entries(checks)) {
                    try {
                        detected[name] = check();
                    } catch (e) {
                        detected[name] = false;
                    }
                }

                return detected;
            }
        """)

        self.results['frameworks'] = frameworks
        detected_list = [name for name, detected in frameworks.items() if detected]
        print(f"🛠️ Detected frameworks: {', '.join(detected_list) if detected_list else 'None'}")

    async def analyze_links(self, page):
        """Analyze important links and endpoints"""
        print("🔗 Analyzing links and endpoints...")

        links_data = await page.evaluate("""
            () => {
                const allLinks = Array.from(document.querySelectorAll('a[href]'));

                const categorizedLinks = {
                    api_endpoints: allLinks.filter(a =>
                        a.href.includes('/api/') ||
                        a.href.includes('.json') ||
                        a.href.includes('.xml')
                    ).map(a => a.href).slice(0, 10),

                    data_pages: allLinks.filter(a =>
                        a.textContent.toLowerCase().includes('datos') ||
                        a.textContent.toLowerCase().includes('data') ||
                        a.textContent.toLowerCase().includes('estadísticas') ||
                        a.textContent.toLowerCase().includes('mercado') ||
                        a.textContent.toLowerCase().includes('operación')
                    ).map(a => ({
                        text: a.textContent.trim(),
                        href: a.href
                    })).slice(0, 15),

                    documents: allLinks.filter(a =>
                        a.href.includes('.pdf') ||
                        a.href.includes('.doc') ||
                        a.href.includes('.xls')
                    ).map(a => ({
                        text: a.textContent.trim(),
                        href: a.href
                    })).slice(0, 10)
                };

                return categorizedLinks;
            }
        """)

        self.results['important_links'] = links_data
        print(f"🔍 Found {len(links_data['data_pages'])} data-related links")

    async def take_screenshot(self, page):
        """Take a screenshot of the page"""
        screenshot_path = self.screenshots_dir / f"coordinador_structure_{int(time.time())}.png"
        await page.screenshot(path=str(screenshot_path), full_page=True)
        self.results['screenshot_path'] = str(screenshot_path)
        print(f"📸 Screenshot saved: {screenshot_path}")

    async def fallback_analysis(self, page):
        """Fallback analysis if main page fails to load"""
        print("🔄 Attempting fallback analysis...")

        try:
            # Try with different user agent
            await page.set_extra_http_headers({
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'es-ES,es;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            })

            response = await page.goto(self.base_url, wait_until='domcontentloaded', timeout=15000)

            if response:
                self.results['fallback_analysis'] = {
                    'status': response.status,
                    'headers': await response.all_headers(),
                    'url': response.url
                }

                # Basic content analysis even if page is limited
                basic_content = await page.evaluate("""
                    () => ({
                        title: document.title,
                        links_count: document.querySelectorAll('a').length,
                        forms_count: document.querySelectorAll('form').length,
                        scripts_count: document.querySelectorAll('script').length
                    })
                """)

                self.results['basic_content'] = basic_content
                print("✅ Fallback analysis completed")

        except Exception as e:
            print(f"❌ Fallback analysis failed: {e}")
            self.results['error'] = str(e)

    async def save_results(self):
        """Save analysis results to JSON file"""
        results_dir = Path(__file__).parent.parent / "extractions"
        results_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = results_dir / f"coordinador_structure_analysis_{timestamp}.json"

        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        print(f"💾 Results saved to: {results_file}")

        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print analysis summary"""
        print("\n" + "="*60)
        print("📋 COORDINADOR.CL STRUCTURE ANALYSIS SUMMARY")
        print("="*60)

        if 'basic_info' in self.results:
            print(f"🌐 URL: {self.results['basic_info']['url']}")
            print(f"📄 Title: {self.results['basic_info']['title']}")

        if 'navigation' in self.results:
            nav = self.results['navigation']
            print(f"🔗 Links: {nav['total_links']} total, {nav['internal_links']} internal")

        if 'content_sections' in self.results:
            content = self.results['content_sections']
            print(f"📑 Content: {len(content['headers'])} headers, {len(content['main_sections'])} sections")

        if 'forms' in self.results:
            forms = self.results['forms']
            print(f"📝 Forms: {len(forms['forms'])} forms, {len(forms['search_elements'])} search elements")

        if 'tables' in self.results:
            tables = self.results['tables']
            print(f"📊 Data: {len(tables['tables'])} tables, {len(tables['data_grids'])} data grids")

        if 'dynamic_content' in self.results:
            dynamic = self.results['dynamic_content']
            print(f"⚡ Dynamic: {dynamic['charts_count']} charts/graphs")

        if 'frameworks' in self.results:
            frameworks = [name for name, detected in self.results['frameworks'].items() if detected]
            print(f"🛠️ Frameworks: {', '.join(frameworks) if frameworks else 'None detected'}")

        if 'important_links' in self.results:
            links = self.results['important_links']
            print(f"🔍 Important: {len(links['data_pages'])} data links, {len(links['documents'])} documents")

        print("="*60)

async def main():
    """Main function to run the analysis"""
    analyzer = CoordinadorStructureAnalyzer()
    await analyzer.analyze_page_structure()

if __name__ == "__main__":
    asyncio.run(main())