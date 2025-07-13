import requests
from bs4 import BeautifulSoup
import re
from bs4.element import Tag
import html as ihtml

THRILLOPHILIA_URL = "https://www.thrillophilia.com/things-to-do-in-dehradun"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

CATEGORY_MAP = {
    "temple": "spiritual",
    "park": "nature", 
    "museum": "heritage",
    "market": "shopping",
    "food": "food",
    "adventure": "adventure",
    "trek": "adventure",
    "waterfall": "nature",
    "forest": "nature",
    "wildlife": "nature",
    "picnic": "nature",
    "shopping": "shopping",
    "culture": "culture",
    "heritage": "heritage",
    "camp": "adventure",
    "cave": "adventure",
    "monastery": "spiritual",
    "institute": "heritage",
    "bazaar": "shopping",
    "walk": "nature",
    "paragliding": "adventure",
    "rafting": "adventure",
    "yoga": "spiritual",
    "meditation": "spiritual",
    "garden": "nature",
    "lake": "nature",
    "river": "nature",
    "mountain": "adventure",
    "hiking": "adventure",
    "climbing": "adventure"
}

def guess_category(name, desc):
    name = name.lower()
    desc = desc.lower()
    for key, val in CATEGORY_MAP.items():
        if key in name or key in desc:
            return val
    return "culture"

def extract_details(text):
    """Extract location, timings, entry fees from text"""
    details = {}
    
    # Location
    location_match = re.search(r'Location:\s*([^<]+)', text, re.IGNORECASE)
    if location_match:
        details['location'] = location_match.group(1).strip()
    
    # Timings
    timing_match = re.search(r'Timings?:\s*([^<]+)', text, re.IGNORECASE)
    if timing_match:
        details['timings'] = timing_match.group(1).strip()
    
    # Entry fees
    fee_match = re.search(r'Entry\s*fees?:\s*([^<]+)', text, re.IGNORECASE)
    if fee_match:
        details['entry_fees'] = fee_match.group(1).strip()
    
    return details

def fetch_experiences():
    """Fetch experiences from Thrillophilia website"""
    try:
        print("Fetching data from Thrillophilia...")
        response = requests.get(THRILLOPHILIA_URL, headers=HEADERS, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all experience cards - try different selectors
        experience_cards = []
        
        # Try different selectors to find experience cards
        selectors = [
            'div.base-block.main-card-container',
            'div.main-card-container',
            'div[data-id]',
            'div.base-block',
            'article',
            '.content-main-card'
        ]
        
        for selector in selectors:
            cards = soup.select(selector)
            if cards:
                print(f"Found {len(cards)} cards with selector: {selector}")
                experience_cards = cards
                break
        
        if not experience_cards:
            # Try finding by looking for numbered sections
            numbered_divs = soup.find_all('div', string=re.compile(r'^\d+$'))
            print(f"Found {len(numbered_divs)} numbered divs")
            
            # Look for parent containers of numbered divs
            for div in numbered_divs:
                parent = div.find_parent('div', class_=re.compile(r'card|block|container'))
                if parent and isinstance(parent, Tag) and parent not in experience_cards:
                    experience_cards.append(parent)
        
        print(f"Total experience cards found: {len(experience_cards)}")
        
        experiences_data = []
        
        for i, card in enumerate(experience_cards[:30]):  # Limit to 30 experiences
            try:
                print(f"\nProcessing card {i+1}:")
                
                # Extract title - try multiple selectors
                title = ""
                title_selectors = ['h3.title', 'h3', 'h2', '.title', 'h4']
                for selector in title_selectors:
                    title_elem = card.select_one(selector)
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        if title and len(title) > 5:
                            break
                
                if not title:
                    print("  No title found")
                    continue
                
                print(f"  Title: {title}")
                
                # Extract image - try multiple approaches
                img_url = ""
                img_elem = card.find('img')
                if img_elem and isinstance(img_elem, Tag):
                    img_url = img_elem.get('data-src') or img_elem.get('src')
                    if not img_url:
                        # Try to get from source elements
                        source_elem = card.find('source')
                        if source_elem and isinstance(source_elem, Tag):
                            srcset = source_elem.get('data-srcset', '')
                            if srcset and isinstance(srcset, str):
                                img_url = srcset.split(' ')[0]
                
                if not img_url:
                    # Use placeholder image
                    img_url = f"https://images.unsplash.com/photo-1506905925346-21bda4d32df4?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80"
                
                print(f"  Image URL: {img_url[:50]}...")
                
                # Extract description - try multiple selectors
                description = ""
                desc_selectors = ['.read-more-content', '.description', 'p', '.text-holder', '.content']
                for selector in desc_selectors:
                    desc_elem = card.select_one(selector)
                    if desc_elem:
                        description = desc_elem.get_text(strip=True)
                        if description and len(description) > 20:
                            break
                
                print(f"  Description length: {len(description)}")
                
                # Extract details from description
                details = extract_details(description)
                print(f"  Location: {details.get('location', 'Not found')}")
                print(f"  Timings: {details.get('timings', 'Not found')}")
                print(f"  Entry fees: {details.get('entry_fees', 'Not found')}")
                
                # Generate rating based on position (higher position = higher rating)
                rating = max(4.0, 5.0 - (i * 0.05))
                
                # Generate duration based on activity type
                duration_options = ["2 hours", "3 hours", "4 hours", "6 hours", "Full day", "Flexible"]
                duration = duration_options[i % len(duration_options)]
                
                # Generate price based on activity type
                if "free" in description.lower() or "no entry" in description.lower():
                    price = "Free"
                elif "camp" in title.lower():
                    price = "From ₹1200"
                elif "adventure" in title.lower() or "paragliding" in title.lower():
                    price = f"From ₹{500 + (i * 100)}"
                else:
                    price = f"From ₹{50 + (i * 25)}"
                
                # Determine category
                category = guess_category(title, description)
                
                # Create experience data
                experience = {
                    "name": title,
                    "img": img_url,
                    "desc": description,
                    "location": details.get('location', 'Dehradun, Uttarakhand'),
                    "timings": details.get('timings', '9 AM - 6 PM'),
                    "entry_fees": details.get('entry_fees', 'Varies'),
                    "category": category,
                    "rating": round(rating, 1),
                    "duration": duration,
                    "price": price
                }
                
                experiences_data.append(experience)
                print(f"  Successfully extracted: {title}")
                
            except Exception as e:
                print(f"  Error extracting experience {i+1}: {e}")
                continue
        
        print(f"\nSuccessfully extracted {len(experiences_data)} experiences")
        
        if not experiences_data:
            print("No experiences extracted, using fallback data")
            return get_fallback_data()
            
        return experiences_data
        
    except Exception as e:
        print(f"Error fetching data: {e}")
        # Fallback to hardcoded data if scraping fails
        return get_fallback_data()

def get_fallback_data():
    """Fallback data if web scraping fails"""
    return [
        {
            "name": "Visit the Ancient Robber's Cave",
            "img": "https://media2.thrillophilia.com/images/photos/000/143/071/original/1549105270_shutterstock_1099141991.jpg?w=753&h=450&dpr=1.0",
            "desc": "Witness the miracle of Nature at the Robber's Cave, which is approximately 8km from Dehradun. Robber's Cave is a 600 M elongated naturally formed cave. A river passes through this cave making this place a perfect picnic spot for family and friends.",
            "location": "Gucchupani, Malsi, Dehradun, Uttarakhand 248003",
            "timings": "7 AM to 6 PM",
            "entry_fees": "INR 25 per person",
            "category": "adventure",
            "rating": 4.5,
            "duration": "3 hours",
            "price": "From ₹25"
        },
        {
            "name": "Camp in Peace and Tranquil Atmosphere of Dehradun",
            "img": "https://media2.thrillophilia.com/images/photos/000/142/599/original/1548919341_shutterstock_1016911477.jpg?w=753&h=450&dpr=1.0",
            "desc": "Rejuvenate your inner self with camping in the verdant valleys of Dehradun. Since the city is one of the gateways to adventures, a small stopover with camp having delicious food and bonfire will be perfect for all.",
            "location": "Raipur, Dehradun, Uttarakhand 248008",
            "timings": "Opens 24 hours",
            "entry_fees": "Starting from Rs 1200/-",
            "category": "adventure",
            "rating": 4.6,
            "duration": "Flexible",
            "price": "From ₹1200"
        },
        {
            "name": "Paragliding in Dehradun",
            "img": "https://images.unsplash.com/photo-1551632811-561732d1e306?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80",
            "desc": "Feel the adrenaline rush as you soar through the skies of Dehradun. Experience the thrill of paragliding with professional instructors and enjoy breathtaking aerial views of the valley.",
            "location": "Various locations around Dehradun",
            "timings": "6 AM - 6 PM",
            "entry_fees": "INR 2500 per person",
            "category": "adventure",
            "rating": 4.8,
            "duration": "2 hours",
            "price": "From ₹2500"
        },
        {
            "name": "Visit Mindrolling Monastery",
            "img": "https://images.unsplash.com/photo-1542810634-71277d95dcbb?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80",
            "desc": "Visit the largest Tibetan monastery in India, known for its stunning architecture and peaceful atmosphere. The monastery houses beautiful Buddhist art and offers meditation sessions.",
            "location": "Clement Town, Dehradun",
            "timings": "6 AM - 6 PM",
            "entry_fees": "Free",
            "category": "spiritual",
            "rating": 4.7,
            "duration": "2 hours",
            "price": "Free"
        },
        {
            "name": "Explore Forest Research Institute",
            "img": "https://images.unsplash.com/photo-1599661046827-dacde6976549?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80",
            "desc": "Explore the magnificent colonial architecture of Forest Research Institute, one of the oldest institutions of its kind. The campus features stunning buildings and beautiful gardens.",
            "location": "Forest Research Institute, Dehradun",
            "timings": "9 AM - 5 PM",
            "entry_fees": "INR 150 per person",
            "category": "heritage",
            "rating": 4.6,
            "duration": "2 hours",
            "price": "From ₹150"
        },
        {
            "name": "Sahastradhara Waterfalls",
            "img": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80",
            "desc": "Natural limestone caves with therapeutic sulfur springs and waterfalls. The name Sahastradhara means 'thousand fold spring' and the water is believed to have medicinal properties.",
            "location": "Sahastradhara Road, Dehradun",
            "timings": "6 AM - 6 PM",
            "entry_fees": "INR 50 per person",
            "category": "nature",
            "rating": 4.4,
            "duration": "4 hours",
            "price": "From ₹50"
        },
        {
            "name": "Paltan Bazaar Shopping",
            "img": "https://images.unsplash.com/photo-1441986300917-64674bd600d8?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80",
            "desc": "Experience the vibrant local market culture at Paltan Bazaar. Shop for traditional handicrafts, woolens, and local produce. The market is famous for its Basmati rice and Pahari handicrafts.",
            "location": "Paltan Bazaar, Dehradun",
            "timings": "10 AM - 10 PM",
            "entry_fees": "Free",
            "category": "shopping",
            "rating": 4.2,
            "duration": "Flexible",
            "price": "Free Entry"
        },
        {
            "name": "Local Food Walk",
            "img": "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80",
            "desc": "Embark on a culinary journey through Dehradun's best street food spots. Taste authentic local dishes, traditional sweets, and regional specialties. A must-do for food lovers.",
            "location": "Various locations in Dehradun",
            "timings": "6 PM - 9 PM",
            "entry_fees": "INR 500 per person",
            "category": "food",
            "rating": 4.6,
            "duration": "3 hours",
            "price": "From ₹500"
        }
    ]

def generate_experience_card_html(experience):
    """Generate HTML for experience card"""
    # Clean and format data
    short_desc = (experience["desc"][:120] + "...") if len(experience["desc"]) > 120 else experience["desc"]
    
    # Category styling
    cat_class = f"bg-{experience['category']}/20 text-{experience['category']}"
    cat_icon = {
        "spiritual": "fas fa-om",
        "nature": "fas fa-leaf", 
        "heritage": "fas fa-landmark",
        "shopping": "fas fa-shopping-bag",
        "food": "fas fa-utensils",
        "adventure": "fas fa-mountain",
        "culture": "fas fa-theater-masks"
    }.get(experience['category'], "fas fa-star")
    
    # Generate star rating
    rating = float(experience['rating'])
    stars = "★" * int(rating) + "☆" * (5 - int(rating))
    
    # Price badge styling
    if "Free" in experience['price']:
        price_badge_class = "bg-green-500 text-white"
    else:
        price_badge_class = "price-badge text-white"
    
    return f'''
    <div class="masonry-item experience-card bg-white rounded-2xl shadow-lg overflow-hidden" data-category="{experience['category']}">
        <div class="image-placeholder h-48 flex items-center justify-center relative">
            <img src="{experience['img']}" alt="{ihtml.escape(experience['name'])}" class="w-full h-full object-cover" />
            <div class="category-badge absolute top-4 left-4 {cat_class} px-3 py-1 rounded-full text-sm font-medium">
                <i class="{cat_icon} mr-1"></i>{experience['category'].capitalize()}
            </div>
            <div class="absolute top-4 right-4 bg-black/50 backdrop-blur-sm rounded-lg p-2 text-white text-xs">
                <div class="text-yellow-400">{stars}</div>
                <div class="text-center">({experience['rating']})</div>
            </div>
        </div>
        <div class="p-6">
            <h3 class="text-xl font-bold text-gray-900 mb-3">{ihtml.escape(experience['name'])}</h3>
            <p class="text-gray-600 text-sm mb-4 leading-relaxed">{ihtml.escape(short_desc)}</p>
            
            <div class="flex items-center justify-between mb-4">
                <div class="duration-badge text-white px-3 py-1 rounded-full text-sm font-medium">
                    <i class="fas fa-clock mr-1"></i>{experience['duration']}
                </div>
                <div class="{price_badge_class} px-3 py-1 rounded-full text-sm font-medium">
                    {experience['price']}
                </div>
            </div>
            
            <button class="view-details-btn w-full bg-primary text-white py-3 rounded-lg hover:bg-primary-light transition-colors font-medium"
                    data-experience-name="{ihtml.escape(experience['name'])}"
                    data-experience-desc="{ihtml.escape(experience['desc'])}"
                    data-experience-img="{experience['img']}"
                    data-experience-category="{experience['category']}"
                    data-experience-rating="{experience['rating']}"
                    data-experience-location="{ihtml.escape(experience['location'])}"
                    data-experience-timings="{ihtml.escape(experience['timings'])}"
                    data-experience-entry-fees="{ihtml.escape(experience['entry_fees'])}"
                    data-experience-duration="{experience['duration']}"
                    data-experience-price="{experience['price']}">
                <i class="fas fa-eye mr-2"></i>View Details
            </button>
        </div>
    </div>
    '''

def update_experience_html(experiences):
    """Update experience.html with fetched data"""
    with open("experience.html", "r", encoding="utf-8") as f:
        html = f.read()
    
    # Find the experiences grid section
    start_marker = 'id="experiences-grid"'
    start = html.find(start_marker)
    
    if start == -1:
        print("Could not find experiences grid section in HTML.")
        return
    
    # Find the opening div tag
    start = html.find("<div", start)
    if start == -1:
        print("Could not find experiences grid div.")
        return
    
    # Find the closing div for the grid
    end_marker = '</div>'
    end = html.find(end_marker, start)
    
    if end == -1:
        print("Could not find end of experiences grid section.")
        return
    
    # Generate new experiences HTML
    experiences_html = '\n'.join([generate_experience_card_html(exp) for exp in experiences])
    
    # Update the HTML
    new_html = html[:start] + '\n' + experiences_html + '\n' + html[end:]
    
    # Update the results count
    new_html = new_html.replace('>30<', f'>{len(experiences)}<')
    
    with open("experience.html", "w", encoding="utf-8") as f:
        f.write(new_html)
    
    print(f"Updated experience.html with {len(experiences)} experiences.")

if __name__ == "__main__":
    experiences = fetch_experiences()
    if experiences:
        update_experience_html(experiences)
    else:
        print("No experiences found.") 