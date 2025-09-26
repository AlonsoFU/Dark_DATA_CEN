#!/usr/bin/env python3
"""
Operaciones domain scraper for coordinador.cl
Inherits from shared base scraper
"""

import asyncio
import sys
from pathlib import Path

# Add shared platform to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

from shared_platform.scrapers.coordinador_cl.coordinador_base_scraper import CoordinadorBaseScraper

class OperacionesCoordinadorScraper(CoordinadorBaseScraper):
    """Scraper specifically for operations data from coordinador.cl"""

    def __init__(self):
        super().__init__("operaciones")

    async def scrape_domain_data(self, page):
        """Extract operations-specific data"""
        return await page.evaluate("""
            () => {
                // Operations-specific scraping logic
                const operacionesData = {
                    programas_operacion: Array.from(document.querySelectorAll('a[href*="programa"]')).map(a => ({
                        text: a.textContent.trim(),
                        href: a.href
                    })),

                    graficos_operacion: Array.from(document.querySelectorAll('.chart, canvas, svg')).map(chart => ({
                        id: chart.id,
                        classes: chart.className,
                        type: chart.tagName
                    })),

                    documentos_operacion: Array.from(document.querySelectorAll('a[href*="operacion"]')).map(a => ({
                        text: a.textContent.trim(),
                        href: a.href,
                        is_document: a.href.includes('.pdf') || a.href.includes('.xls')
                    })),

                    indicadores_tiempo_real: Array.from(document.querySelectorAll('.indicator, .metric, [class*="real-time"]')).map(el => ({
                        text: el.textContent.trim(),
                        classes: el.className,
                        id: el.id
                    }))
                };

                return operacionesData;
            }
        """)

    async def scrape_operaciones_sections(self):
        """Scrape all operations-related sections"""
        sections = [
            "operacion/documentos/",
            "operacion/graficos/operacion-programada/generacion-programada/",
            "operacion/graficos/operacion-real/",
            "reportes-y-estadisticas/"
        ]

        await self.run_scraper(sections)

async def main():
    """Run operations scraper"""
    scraper = OperacionesCoordinadorScraper()
    await scraper.scrape_operaciones_sections()

if __name__ == "__main__":
    asyncio.run(main())