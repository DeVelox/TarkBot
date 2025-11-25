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
            elif category_name in ["maps", "locations", "customs"]:
                # Special handling for map/location pages
                pages = self._scrape_maps_and_locations(
                    soup, category_url, category_name
                )
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

                        # Extract attachments first
                        attachments = self._extract_weapon_attachments(soup, name)

                        # Create content with attachments
                        attachment_text = ""
                        if attachments:
                            attachment_text = (
                                f"\n\nCompatible Attachments:\n"
                                + "\n".join(f"- {att}" for att in attachments[:10])
                            )  # Limit to 10

                        content = f"""Weapon: {name}
Cartridge: {cartridge}
Firing Modes: {firing_modes}
Rate of Fire: {rate_of_fire} RPM

Description: {description}{attachment_text}"""

                        # Extract metadata
                        metadata = {
                            "cartridge": cartridge,
                            "firing_modes": firing_modes,
                            "rate_of_fire": rate_of_fire,
                            "type": "weapon",
                            "attachments": attachments,
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

    def _scrape_maps_and_locations(
        self, soup, base_url: str, category_name: str
    ) -> List[WikiPage]:
        """Extract map and location data from wiki pages"""
        pages = []

        # Look for map/location sections
        content_div = soup.find("div", {"class": "mw-parser-output"})
        if not content_div:
            return pages

        # Extract text content for general information
        content_text = self._clean_content(content_div)

        # Look for specific map/location information
        map_sections = content_div.find_all(["h2", "h3", "h4"])

        for section in map_sections:
            section_title = section.get_text().strip()
            if any(
                keyword in section_title.lower()
                for keyword in [
                    "map",
                    "location",
                    "extract",
                    "dorm",
                    "customs",
                    "shoreline",
                    "woods",
                    "factory",
                ]
            ):
                # Get the content following this section
                section_content = []
                current = section.find_next_sibling()

                while current and current.name not in ["h2", "h3", "h4"]:
                    if current.name in ["p", "ul", "ol", "table"]:
                        section_content.append(current.get_text().strip())
                    current = current.find_next_sibling()

                if section_content:
                    full_content = f"{section_title}\n\n" + "\n\n".join(section_content)

                    page = WikiPage(
                        title=f"{category_name.title()}: {section_title}",
                        category=category_name,
                        content=full_content,
                        metadata={"section": section_title, "type": "location_info"},
                        url=base_url,
                        last_updated="2024-01-01",
                    )
                    pages.append(page)

        # If no specific sections found, create a general page
        if not pages and content_text:
            page = WikiPage(
                title=f"{category_name.title()} Overview",
                category=category_name,
                content=content_text,
                metadata={"type": "general_info"},
                url=base_url,
                last_updated="2024-01-01",
            )
            pages.append(page)

        # Extract interactive map data (extract locations)
        script_tags = soup.find_all("script")
        for script in script_tags:
            if script.string and "interactiveMaps" in script.string:
                try:
                    # Parse the JavaScript object to extract extract information
                    map_extracts = self._parse_interactive_map_data(script.string)
                    for extract in map_extracts:
                        # Create more searchable content
                        location_hint = ""
                        if "dorm" in extract["title"].lower():
                            location_hint = "This extract is located near the dormitories on the Customs map. "
                        elif "boat" in extract["title"].lower():
                            location_hint = "This extract is located at the waterfront on the Customs map. "
                        elif "bunker" in extract["title"].lower():
                            location_hint = "This extract is located underground in a bunker on the Customs map. "

                        content = f"""Extract Location: {extract["title"]}

{location_hint}This is an extraction point on the {extract.get("map", "Customs")} map in Escape from Tarkov.

Description: {extract.get("description", "No description available")}

Requirements: {extract.get("requirements", "None")}

To use this extract, navigate to the location shown on the interactive map and activate the extraction when ready to leave the raid."""

                        page = WikiPage(
                            title=f"Extract: {extract['title']}",
                            category="extracts",
                            content=content,
                            metadata={
                                "type": "extract_location",
                                "map": extract.get("map", "Unknown"),
                                "requirements": extract.get("requirements", "None"),
                                "coordinates": extract.get("position", []),
                                "location_hint": location_hint.strip(),
                            },
                            url=base_url,
                            last_updated="2024-01-01",
                        )
                        pages.append(page)
                except Exception as e:
                    print(f"Error parsing map data: {e}")

        return pages[:20]  # Limit for testing

    def _extract_weapon_attachments(self, soup, weapon_name: str) -> List[str]:
        """Extract attachment/modification information for a weapon"""
        attachments = []

        # Find attachments table
        tables = soup.find_all("table", {"class": "wikitable"})
        for table in tables:
            headers = table.find_all("th")
            header_texts = [h.get_text().strip() for h in headers]
            if "Attachments" in header_texts:
                # Found attachments table
                rows = table.find_all("tr")
                for row in rows[1:]:  # Skip header
                    cells = row.find_all(["td", "th"])
                    if len(cells) >= 3:  # Images, Variants, Attachments
                        attachment_text = cells[2].get_text().strip()
                        if attachment_text:
                            # Split by newlines and clean up
                            mods = [
                                mod.strip()
                                for mod in attachment_text.split("\n")
                                if mod.strip()
                            ]
                            attachments.extend(mods)

        # Also look for compatibility sections
        compat_sections = soup.find_all(
            ["h2", "h3", "h4"],
            string=lambda text: text
            and ("compatibility" in text.lower() or "mods" in text.lower()),
        )
        for section in compat_sections:
            # Get content following the section
            current = section.find_next_sibling()
            while current and current.name not in ["h2", "h3", "h4"]:
                if current.name in ["ul", "ol"]:
                    items = current.find_all("li")
                    for item in items:
                        text = item.get_text().strip()
                        if text and len(text) > 10:  # Filter out short items
                            attachments.append(text)
                current = current.find_next_sibling()

        return list(set(attachments))  # Remove duplicates

    def _parse_interactive_map_data(self, script_content: str) -> List[Dict]:
        """Parse interactive map JavaScript to extract extract locations"""
        extracts = []

        try:
            import re

            # Find all exfil_pmc entries (PMC extract points)
            exfil_pattern = r'"categoryId":"exfil_pmc".*?"title":"([^"]*)".*?"description":"([^"]*)"'
            matches = re.findall(exfil_pattern, script_content, re.DOTALL)

            for title, description in matches:
                # Clean up HTML entities and tags
                clean_title = re.sub(
                    r"<[^>]+>", "", title.replace("\\n", " ").replace("\\", "")
                )
                clean_desc = re.sub(
                    r"<[^>]+>", "", description.replace("\\n", " ").replace("\\", "")
                )

                # Extract requirements from description
                requirements = "None"
                if "requires" in clean_desc.lower():
                    requirements = clean_desc

                extracts.append(
                    {
                        "title": clean_title.strip(),
                        "description": clean_desc.strip(),
                        "requirements": requirements,
                        "map": "Customs",  # Assuming this is for Customs based on the script
                    }
                )

        except Exception as e:
            print(f"Error parsing interactive map: {e}")

        return extracts

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
