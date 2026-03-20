from datetime import datetime, timedelta

def fetch_reviews(package_name="in.indwealth", weeks=12):
    """
    Fetch reviews from the last N weeks.
    Includes rating (score) and title in the output.
    """
    logger.info(f"Fetching reviews for {package_name} from the last {weeks} weeks...")
    limit_date = datetime.now() - timedelta(weeks=weeks)
    
    all_raw_reviews = []
    continuation_token = None
    
    try:
        # We may need multiple calls to get 12 weeks of data
        # Fetching 400 at a time
        while True:
            result, continuation_token = reviews(
                package_name,
                lang='en',
                country='in',
                sort=Sort.NEWEST,
                count=400,
                continuation_token=continuation_token
            )
            
            reached_limit = False
            for r in result:
                dt = r.get("at")
                if dt and dt < limit_date:
                    reached_limit = True
                    break
                
                # Map fields: "review" (text), "date", "rating", "title"
                all_raw_reviews.append({
                    "review": r.get("content", ""),
                    "date": dt.isoformat() if dt else None,
                    "rating": r.get("score", 0),
                    "title": r.get("reviewId", "") # Play Store doesn't have titles, using ID as unique ref
                })
            
            if reached_limit or not continuation_token or len(all_raw_reviews) >= 1000:
                break
                
        logger.info(f"Successfully fetched {len(all_raw_reviews)} reviews from the last {weeks} weeks.")
        return all_raw_reviews
        
    except Exception as e:
        logger.error(f"Error while fetching reviews: {e}")
        return []

if __name__ == "__main__":
    # Test execution
    res = fetch_reviews()
    print(f"Sample review: {res[0] if res else 'None'}")
