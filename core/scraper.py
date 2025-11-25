"""
TarkBot Wiki Scraper
Scrapes Escape from Tarkov wiki pages
"""

import requests
from bs4 import BeautifulSoup
import json
import os
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class WikiPage:
    """Represents a scraped wiki page"""

    title: str
    category: str
    content: str
    metadata: Dict
    url: str
    last_updated: str


class TarkovWikiScraper:
    """Scraper for Escape from Tarkov Fandom wiki"""

    BASE_URL = "https://escapefromtarkov.fandom.com"

    def __init__(self, cache_dir: str = "data/cache"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)

    def scrape_page(self, url: str, category: str) -> Optional[WikiPage]:
        """Scrape a single wiki page"""
        try:
            response = requests.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")

            # Extract title
            title = soup.find("h1", {"class": "page-header__title"}).text.strip()

            # Extract main content
            content_div = soup.find("div", {"class": "mw-parser-output"})
            if not content_div:
                return None

            # Clean content
            content = self._clean_content(content_div)

            # Extract metadata (placeholder)
            metadata = self._extract_metadata(content_div)

            return WikiPage(
                title=title,
                category=category,
                content=content,
                metadata=metadata,
                url=url,
                last_updated=self._get_last_updated(soup),
            )

        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return None

    def _clean_content(self, content_div) -> str:
        """Clean and extract text from wiki content"""
        # Remove unwanted elements
        for unwanted in content_div.find_all(["script", "style", "table", "nav"]):
            unwanted.decompose()

        # Extract text
        text = content_div.get_text(separator="\n", strip=True)

        # Clean up whitespace
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        return "\n".join(lines)

    def _extract_metadata(self, content_div) -> Dict:
        """Extract structured metadata from page"""
        metadata = {}

        # Look for infoboxes/tables with stats
        infobox = content_div.find("table", {"class": "wikitable"})
        if infobox:
            # Extract key-value pairs from table
            rows = infobox.find_all("tr")
            for row in rows:
                cells = row.find_all(["td", "th"])
                if len(cells) >= 2:
                    key = cells[0].get_text(strip=True)
                    value = cells[1].get_text(strip=True)
                    metadata[key.lower().replace(" ", "_")] = value

        return metadata

    def _get_last_updated(self, soup) -> str:
        """Extract last updated timestamp"""
        # Placeholder - would need to parse wiki history
        return "2024-01-01"

    def scrape_category(self, category_url: str, category_name: str) -> List[WikiPage]:
        """Scrape all items in a category"""
        pages = []

        try:
            response = requests.get(category_url)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")

            if category_name == "weapons":
                # Special handling for weapons page - extract from tables
                pages = self._scrape_weapons_from_table(soup, category_url)
            else:
                # Default category scraping
                pages = self._scrape_category_links(soup, category_name, category_url)

        except Exception as e:
            print(f"Error scraping category {category_url}: {e}")

        return pages

    def _scrape_weapons_from_table(self, soup, base_url: str) -> List[WikiPage]:
        """Extract weapon data from wiki tables"""
        pages = []

        # Find all weapon tables
        tables = soup.find_all("table", {"class": "wikitable"})

        for table in tables:
            rows = table.find_all("tr")

            # Skip header row
            for row in rows[1:]:
                cells = row.find_all(["td", "th"])
                if len(cells) >= 6:  # Name, Image, Cartridge, Modes, RoF, Description
                    try:
                        name = cells[0].get_text().strip()
                        cartridge = cells[2].get_text().strip()
                        firing_modes = cells[3].get_text().strip()
                        rate_of_fire = cells[4].get_text().strip()
                        description = cells[5].get_text().strip()

                        # Create content
                        content = f"""Weapon: {name}
Cartridge: {cartridge}
Firing Modes: {firing_modes}
Rate of Fire: {rate_of_fire} RPM

Description: {description}"""

                        # Extract metadata
                        metadata = {
                            "cartridge": cartridge,
                            "firing_modes": firing_modes,
                            "rate_of_fire": rate_of_fire,
                            "type": "weapon",
                        }

                        page = WikiPage(
                            title=name,
                            category="weapons",
                            content=content,
                            metadata=metadata,
                            url=base_url,
                            last_updated="2024-01-01",
                        )

                        pages.append(page)

                    except Exception as e:
                        print(f"Error parsing weapon row: {e}")
                        continue

        return pages[:20]  # Limit for testing

    def _scrape_category_links(
        self, soup, category_name: str, base_url: str
    ) -> List[WikiPage]:
        """Scrape pages from category links (fallback method)"""
        pages = []

        # Find all wiki page links
        links = soup.find_all("a", href=True)

        wiki_links = []
        for link in links:
            href = link["href"]
            if href.startswith("/wiki/") and not any(
                skip in href for skip in ["Category:", "File:", "Special:"]
            ):
                full_url = self.BASE_URL + href if href.startswith("/") else href
                wiki_links.append((link.get_text().strip(), full_url))

        # Remove duplicates and limit
        seen = set()
        unique_links = []
        for text, url in wiki_links:
            if text and url not in seen:
                seen.add(url)
                unique_links.append((text, url))

        for title, page_url in unique_links[:10]:  # Limit for testing
            page = self.scrape_page(page_url, category_name)
            if page:
                pages.append(page)

        return pages


if __name__ == "__main__":
    # Test scraper
    scraper = TarkovWikiScraper()
    test_url = "https://escapefromtarkov.fandom.com/wiki/AK-74N"
    page = scraper.scrape_page(test_url, "weapons")

    if page:
        print(f"Title: {page.title}")
        print(f"Category: {page.category}")
        print(f"Content length: {len(page.content)}")
        print(f"Metadata: {page.metadata}")
    else:
        print("Failed to scrape page")
