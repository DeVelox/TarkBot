"""
TarkBot CLI Interface
Command-line interface for TarkBot
"""

import click
import os
from typing import Dict
from core.scraper import TarkovWikiScraper, WikiPage
from core.embeddings import TextEmbedder, TextChunker
from core.vector_store import VectorStore
from core.query_engine import QueryEngine


# Default categories
DEFAULT_CATEGORIES = {
    "weapons": "https://escapefromtarkov.fandom.com/wiki/Weapons",
    "ammunition": "https://escapefromtarkov.fandom.com/wiki/Ammunition",
    "armor": "https://escapefromtarkov.fandom.com/wiki/Armor_vests",
    "quests": "https://escapefromtarkov.fandom.com/wiki/Quests",
    "maps": "https://escapefromtarkov.fandom.com/wiki/Maps",
    # Major map pages
    "customs": "https://escapefromtarkov.fandom.com/wiki/Customs",
    "shoreline": "https://escapefromtarkov.fandom.com/wiki/Shoreline",
    "woods": "https://escapefromtarkov.fandom.com/wiki/Woods",
    "factory": "https://escapefromtarkov.fandom.com/wiki/Factory",
    "interchange": "https://escapefromtarkov.fandom.com/wiki/Interchange",
    "reserve": "https://escapefromtarkov.fandom.com/wiki/Reserve",
    "lighthouse": "https://escapefromtarkov.fandom.com/wiki/Lighthouse",
    "streets": "https://escapefromtarkov.fandom.com/wiki/Streets_of_Tarkov",
    "locations": "https://escapefromtarkov.fandom.com/wiki/Locations",
}


class TarkBotCLI:
    """Main CLI application"""

    def __init__(self):
        self.scraper = TarkovWikiScraper()
        self.embedder = TextEmbedder()
        self.chunker = TextChunker()
        self.vector_store = VectorStore()
        self.query_engine = QueryEngine(self.embedder, self.vector_store)

        # Data is automatically loaded in VectorStore.__init__

    def scrape_category(self, category_name: str, category_url: str):
        """Scrape a category and add to vector store"""
        click.echo(f"Scraping category: {category_name}")
        click.echo(f"URL: {category_url}")

        pages = self.scraper.scrape_category(category_url, category_name)

        if not pages:
            click.echo("No pages found in category")
            return

        click.echo(f"Found {len(pages)} pages")

        # Process pages
        all_chunks = []
        all_embeddings = []
        all_metadata = []

        for page in pages:
            click.echo(f"Processing: {page.title}")

            # Chunk the content
            chunks = self.chunker.chunk_document(page.content, page.title)

            for chunk in chunks:
                # Add page metadata to chunk
                chunk_metadata = {
                    **chunk,
                    "category": page.category,
                    "url": page.url,
                    "page_metadata": page.metadata,
                    "last_updated": page.last_updated,
                }

                all_chunks.append(chunk["text"])
                all_metadata.append(chunk_metadata)

        if all_chunks:
            # Generate embeddings
            click.echo("Generating embeddings...")
            embeddings = self.embedder.embed_texts(all_chunks)

            # Add to vector store
            self.vector_store.add_vectors(embeddings, all_metadata)
            self.vector_store.save_data()

            click.echo(f"Added {len(all_chunks)} chunks to vector store")

    def ask_question(self, question: str):
        """Answer a question"""
        click.echo(f"Question: {question}")

        result = self.query_engine.ask(question)

        click.echo(f"\nAnswer: {result.text}")
        click.echo(f"Confidence: {result.confidence:.2f}")

        if result.sources:
            click.echo(f"\nSources ({len(result.sources)}):")
            for source in result.sources[:3]:  # Show top 3
                click.echo(
                    f"  - {source['title']} (relevance: {source.get('relevance', 0):.2f})"
                )

    def list_categories(self):
        """List available categories"""
        click.echo("Available categories:")
        for name, url in DEFAULT_CATEGORIES.items():
            click.echo(f"  {name}: {url}")

    def get_stats(self):
        """Show vector store statistics"""
        stats = self.vector_store.get_stats()
        click.echo("Vector Store Statistics:")
        click.echo(f"  Total vectors: {stats['total_vectors']}")
        click.echo(f"  Dimension: {stats['dimension']}")
        click.echo(f"  Vectors file: {stats['vectors_file']}")
        click.echo(f"  Metadata file: {stats['metadata_file']}")


# CLI Commands
@click.group()
def cli():
    """TarkBot - Escape from Tarkov AI Assistant"""
    pass


@cli.command()
@click.argument("question")
def ask(question):
    """Ask TarkBot a question about Escape from Tarkov"""
    bot = TarkBotCLI()
    bot.ask_question(question)


@cli.group()
def category():
    """Category management commands"""
    pass


@category.command("add")
@click.option("--name", required=True, help="Category name")
@click.option("--url", required=True, help="Category URL")
def category_add(name, url):
    """Add a new category to scrape"""
    click.echo(f"Added category: {name} -> {url}")
    # In a real implementation, this would save to a config file
    click.echo("Note: This is a placeholder. Categories are currently hardcoded.")


@category.command("remove")
@click.option("--name", required=True, help="Category name to remove")
def category_remove(name):
    """Remove a category"""
    click.echo(f"Removed category: {name}")
    # In a real implementation, this would remove from config and clean up data
    click.echo("Note: This is a placeholder. Categories are currently hardcoded.")


@category.command("list")
def category_list():
    """List available categories"""
    bot = TarkBotCLI()
    bot.list_categories()


@cli.group()
def data():
    """Data management commands"""
    pass


@data.command("scrape")
@click.option("--category", help="Category name to scrape")
@click.option(
    "--all", "scrape_all", is_flag=True, help="Scrape all unscraped categories"
)
@click.option("--url", help="Category URL (optional, will use default if not provided)")
def data_scrape(category, scrape_all, url):
    """Scrape a wiki category or all unscraped categories"""
    bot = TarkBotCLI()

    if scrape_all:
        # Check which categories have been scraped
        scraped_categories = set()
        if bot.vector_store.vectors is not None:
            # Get all unique categories from metadata
            for metadata in bot.vector_store.metadata:
                category_name = metadata.get("category", "")
                if category_name:
                    scraped_categories.add(category_name)

        # Categories to scrape
        unscraped_categories = []
        for cat_name, cat_url in DEFAULT_CATEGORIES.items():
            if cat_name not in scraped_categories:
                unscraped_categories.append((cat_name, cat_url))

        if not unscraped_categories:
            click.echo("All categories have already been scraped!")
            return

        click.echo(f"Found {len(unscraped_categories)} unscraped categories:")
        for cat_name, cat_url in unscraped_categories:
            click.echo(f"  - {cat_name}")

        # Ask for confirmation
        if not click.confirm("Do you want to scrape all unscraped categories?"):
            return

        # Scrape each unscraped category
        total_pages = 0
        for cat_name, cat_url in unscraped_categories:
            click.echo(f"\nScraping {cat_name}...")
            pages = bot.scraper.scrape_category(cat_url, cat_name)

            if pages:
                # Process pages for vector storage
                all_chunks = []
                all_embeddings = []
                all_metadata = []

                for page in pages:
                    click.echo(f"  Processing: {page.title}")

                    # Chunk the content
                    chunks = bot.chunker.chunk_document(page.content, page.title)

                    for chunk in chunks:
                        # Add page metadata to chunk
                        chunk_metadata = {
                            **chunk,
                            "category": page.category,
                            "url": page.url,
                            "page_metadata": page.metadata,
                            "last_updated": page.last_updated,
                        }

                        all_chunks.append(chunk["text"])
                        all_metadata.append(chunk_metadata)

                if all_chunks:
                    # Generate embeddings
                    click.echo(
                        f"  Generating embeddings for {len(all_chunks)} chunks..."
                    )
                    embeddings = bot.embedder.embed_texts(all_chunks)

                    # Add to vector store
                    bot.vector_store.add_vectors(embeddings, all_metadata)
                    bot.vector_store.save_data()

                    click.echo(f"  Added {len(all_chunks)} chunks to vector store")
                    total_pages += len(pages)
                else:
                    click.echo(f"  No content found for {cat_name}")
            else:
                click.echo(f"  No pages found for {cat_name}")

        click.echo(
            f"\nCompleted! Scraped {total_pages} pages across {len(unscraped_categories)} categories."
        )
    else:
        # Single category scraping
        if not category:
            click.echo("Error: --category is required when not using --all")
            click.echo("Use --all to scrape all unscraped categories")
            return

        if not url:
            if category not in DEFAULT_CATEGORIES:
                click.echo(f"Unknown category: {category}")
                click.echo("Use --url to specify a custom category URL")
                return
            url = DEFAULT_CATEGORIES[category]

        bot.scrape_category(category, url)


@data.command("stats")
def data_stats():
    """Show database statistics"""
    bot = TarkBotCLI()
    bot.get_stats()


@data.command("status")
def data_status():
    """Show scraping status for all categories"""
    bot = TarkBotCLI()

    # Check which categories have been scraped
    scraped_categories = set()
    category_counts = {}

    if bot.vector_store.vectors is not None:
        # Get all unique categories from metadata
        for metadata in bot.vector_store.metadata:
            category = metadata.get("category", "")
            if category:
                scraped_categories.add(category)
                category_counts[category] = category_counts.get(category, 0) + 1

    click.echo("Category Scraping Status:")
    click.echo("=" * 40)

    all_categories = list(DEFAULT_CATEGORIES.keys())
    all_categories.sort()

    for category in all_categories:
        status = "✅ Scraped" if category in scraped_categories else "❌ Not scraped"
        count = (
            f"({category_counts.get(category, 0)} items)"
            if category in scraped_categories
            else ""
        )
        click.echo(f"  {category:<12} {status} {count}")

    scraped_count = len(scraped_categories)
    total_count = len(DEFAULT_CATEGORIES)

    click.echo(f"\nSummary: {scraped_count}/{total_count} categories scraped")
    if scraped_count < total_count:
        click.echo(
            f"Run 'uv run main.py data scrape-all' to scrape remaining categories"
        )

    # Check which categories have been scraped
    scraped_categories = set()
    if bot.vector_store.vectors is not None:
        # Get all unique categories from metadata
        for metadata in bot.vector_store.metadata:
            category = metadata.get("category", "")
            if category:
                scraped_categories.add(category)

    # Categories to scrape
    unscraped_categories = []
    for category, url in DEFAULT_CATEGORIES.items():
        if category not in scraped_categories:
            unscraped_categories.append((category, url))

    if not unscraped_categories:
        click.echo("All categories have already been scraped!")
        return

    click.echo(f"Found {len(unscraped_categories)} unscraped categories:")
    for category, url in unscraped_categories:
        click.echo(f"  - {category}")

    # Ask for confirmation
    if not click.confirm("Do you want to scrape all unscraped categories?"):
        return

    # Scrape each unscraped category
    total_pages = 0
    for category, url in unscraped_categories:
        click.echo(f"\nScraping {category}...")
        pages = bot.scraper.scrape_category(url, category)

        if pages:
            # Process pages for vector storage
            all_chunks = []
            all_embeddings = []
            all_metadata = []

            for page in pages:
                click.echo(f"  Processing: {page.title}")

                # Chunk the content
                chunks = bot.chunker.chunk_document(page.content, page.title)

                for chunk in chunks:
                    # Add page metadata to chunk
                    chunk_metadata = {
                        **chunk,
                        "category": page.category,
                        "url": page.url,
                        "page_metadata": page.metadata,
                        "last_updated": page.last_updated,
                    }

                    all_chunks.append(chunk["text"])
                    all_metadata.append(chunk_metadata)

            if all_chunks:
                # Generate embeddings
                click.echo(f"  Generating embeddings for {len(all_chunks)} chunks...")
                embeddings = bot.embedder.embed_texts(all_chunks)

                # Add to vector store
                bot.vector_store.add_vectors(embeddings, all_metadata)
                bot.vector_store.save_data()

                click.echo(f"  Added {len(all_chunks)} chunks to vector store")
                total_pages += len(pages)
            else:
                click.echo(f"  No content found for {category}")
        else:
            click.echo(f"  No pages found for {category}")

    click.echo(
        f"\nCompleted! Scraped {total_pages} pages across {len(unscraped_categories)} categories."
    )


if __name__ == "__main__":
    cli()
