from google_play_scraper import reviews, Sort
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fetch_reviews(package_name="in.indwealth", count=200):
    """
    Fetch the latest reviews for a specific Google Play Store package.
    """
    logger.info(f"Fetching up to {count} reviews for {package_name}...")
    
    try:
        # Fetch reviews using google-play-scraper
        result, _ = reviews(
            package_name,
            lang='en', # Try to fetch English primarily from the store
            country='in',
            sort=Sort.NEWEST,
            count=count
        )
        
        raw_reviews = []
        for r in result:
            # Map the necessary fields: "review" and "date" (ISO format string)
            raw_reviews.append({
                "review": r.get("content", ""),
                "date": r.get("at").isoformat() if r.get("at") else None
            })
            
        logger.info(f"Successfully fetched {len(raw_reviews)} raw reviews.")
        return raw_reviews
        
    except Exception as e:
        logger.error(f"Error while fetching reviews: {e}")
        return []

if __name__ == "__main__":
    # Test execution
    res = fetch_reviews()
    print(f"Sample review: {res[0] if res else 'None'}")
