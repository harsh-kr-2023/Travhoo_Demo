import requests
from bs4 import BeautifulSoup
import re
from bs4.element import Tag

# URL for Dehradun tourist spots on Thrillophilia
THRILLOPHILIA_URL = "https://www.thrillophilia.com/destinations/dehradun/places-to-visit"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

def fetch_tourist_spots():
    """Fetch tourist spots data from Thrillophilia"""
    response = requests.get(THRILLOPHILIA_URL, headers=headers)
    if response.status_code != 200:
        print("Failed to fetch Thrillophilia page:", response.status_code)
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    spots = []
    
    # Find all tourist spot cards
    spot_cards = soup.find_all("div", class_="base-block main-card-container attraction-main-card")
    
    for card in spot_cards:
        try:
            # Extract spot name
            title_elem = card.find("h3", class_="h3 title")
            if not title_elem:
                continue
            name = title_elem.get_text(strip=True)
            
            # Extract image URL
            img_url = None
            img_elem = card.find("img")
            if isinstance(img_elem, Tag):
                if img_elem.has_attr("data-src"):
                    img_url = img_elem["data-src"]
                elif img_elem.has_attr("src"):
                    img_url = img_elem["src"]
            
            # Extract description
            desc = ""
            desc_elem = card.find("div", class_="read-more-content")
            if isinstance(desc_elem, Tag):
                desc = desc_elem.get_text(strip=True)
            
            # Extract link
            link = ""
            link_elem = title_elem.find("a")
            if isinstance(link_elem, Tag) and link_elem.has_attr("href"):
                link = "https://www.thrillophilia.com" + str(link_elem["href"])
            
            # Extract rating and reviews from tour section if available
            rating = "No rating"
            reviews_count = "0"
            tour_section = card.find("div", class_="tour-carousel-wrapper")
            if tour_section:
                rating_elem = tour_section.find("span", class_="counter")
                if rating_elem:
                    reviews_text = rating_elem.get_text(strip=True)
                    reviews_count = re.search(r'(\d+)', reviews_text)
                    if reviews_count:
                        reviews_count = reviews_count.group(1)
            
            # Determine category based on name and description
            category = determine_category(name, desc)
            
            # Generate random rating for demo (since actual ratings aren't easily extractable)
            import random
            rating_value = round(random.uniform(3.5, 4.8), 1)
            rating = f"{rating_value} ({reviews_count} reviews)"
            
            spots.append({
                "name": name,
                "img_url": img_url,
                "desc": desc,
                "link": link,
                "rating": rating,
                "category": category,
                "entry_fee": "Free Entry",  # Default, can be enhanced
                "timing": "6:00 AM - 8:00 PM",  # Default, can be enhanced
                "duration": "2-3 hours"  # Default, can be enhanced
            })
            
        except Exception as e:
            print(f"Error parsing spot: {e}")
            continue
    
    return spots

def determine_category(name, desc):
    """Determine category based on name and description"""
    text = (name + " " + desc).lower()
    
    if any(word in text for word in ["temple", "monastery", "religious", "shiva", "buddhist"]):
        return "religious"
    elif any(word in text for word in ["trek", "mountain", "adventure", "hiking", "climbing"]):
        return "adventure"
    elif any(word in text for word in ["museum", "institute", "research", "historical", "colonial"]):
        return "historical"
    elif any(word in text for word in ["forest", "park", "wildlife", "nature", "garden"]):
        return "nature"
    else:
        return "nature"  # Default category

def generate_spot_card_html(spot):
    """Generate HTML card for a tourist spot"""
    img = spot["img_url"] or "https://images.unsplash.com/photo-1449824913935-59a10b8d2000?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80"
    
    # Generate star rating
    rating_value = float(re.search(r'([0-9.]+)', spot["rating"]).group(1)) if re.search(r'([0-9.]+)', spot["rating"]) else 4.0
    full_stars = int(rating_value)
    half_star = 1 if rating_value - full_stars >= 0.5 else 0
    empty_stars = 5 - full_stars - half_star
    
    stars_html = '<i class="fas fa-star"></i>' * full_stars
    if half_star:
        stars_html += '<i class="fas fa-star-half-alt"></i>'
    stars_html += '<i class="far fa-star"></i>' * empty_stars
    
    # Category colors
    category_colors = {
        "nature": "bg-green-100 text-green-800",
        "religious": "bg-orange-100 text-orange-800", 
        "adventure": "bg-blue-100 text-blue-800",
        "historical": "bg-red-100 text-red-800"
    }
    
    category_color = category_colors.get(spot["category"], "bg-gray-100 text-gray-800")
    
    return f'''
    <div class="spot-card bg-white rounded-3xl shadow-lg overflow-hidden cursor-pointer" data-category="{spot['category']}">
        <div class="relative h-48 overflow-hidden">
            <img src="{img}" alt="{spot['name']}" class="spot-image w-full h-full object-cover" />
            <div class="entry-badge absolute top-3 right-3 bg-green-500/90 text-white px-2 py-1 rounded-full text-xs font-semibold">
                {spot['entry_fee']}
            </div>
            <div class="overlay absolute inset-0 flex items-center justify-center">
                <div class="cta-button bg-white/20 backdrop-blur-sm border border-white/30 text-white px-6 py-3 rounded-full font-semibold">
                    <i class="fas fa-eye mr-2"></i>View Details
                </div>
            </div>
        </div>
        <div class="p-5">
            <h4 class="text-lg font-bold text-gray-900 mb-2">{spot['name']}</h4>
            <p class="text-gray-600 text-sm mb-3">{spot['desc'][:150]}{'...' if len(spot['desc']) > 150 else ''}</p>
            
            <div class="flex flex-wrap gap-1 mb-3">
                <span class="{category_color} px-2 py-1 rounded-full text-xs">{spot['category'].title()}</span>
            </div>
            
            <div class="flex items-center justify-between text-xs mb-3">
                <span class="timing-badge px-2 py-1 rounded-full">{spot['timing']}</span>
                <span class="duration-badge px-2 py-1 rounded-full">{spot['duration']}</span>
            </div>
            
            <div class="flex items-center justify-between">
                <div class="rating-stars text-sm">
                    {stars_html}
                    <span class="text-gray-600 ml-1">{rating_value}</span>
                </div>
                <button class="view-details-btn bg-green-600 text-white px-4 py-2 rounded-lg text-xs font-medium hover:bg-green-700 transition-colors" 
                        data-spot-name="{spot['name']}" 
                        data-spot-desc="{spot['desc'].replace('"', '&quot;')}" 
                        data-spot-img="{img}" 
                        data-spot-category="{spot['category']}" 
                        data-spot-rating="{rating_value}">
                    View Details
                </button>
            </div>
        </div>
    </div>
    '''

def update_tourist_spots_html(spots):
    """Update tourist_spots.html with fetched data"""
    with open("tourist_spots.html", "r", encoding="utf-8") as f:
        html = f.read()
    
    # Find the spots grid section
    start_marker = 'id="spots-grid"'
    start = html.find(start_marker)
    
    if start == -1:
        print("Could not find spots grid section in HTML.")
        return
    
    # Find the opening div tag
    div_start = html.rfind('<div', 0, start)
    if div_start == -1:
        print("Could not find opening div tag.")
        return
    
    # Find the closing div for the grid (look for the matching closing div)
    open_divs = 1
    i = start + len(start_marker)
    while open_divs > 0 and i < len(html):
        if html[i:i+4] == '<div':
            open_divs += 1
        elif html[i:i+6] == '</div>':
            open_divs -= 1
        i += 1
    
    if open_divs > 0:
        print("Could not find matching closing div.")
        return
    
    end = i - 6  # Position after the closing </div>
    
    # Generate new spots HTML
    spots_html = '\n'.join([generate_spot_card_html(spot) for spot in spots])
    
    # Update the HTML
    new_html = html[:div_start] + '<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8" id="spots-grid">\n' + spots_html + '\n</div>' + html[end:]
    
    with open("tourist_spots.html", "w", encoding="utf-8") as f:
        f.write(new_html)
    
    print(f"Updated tourist_spots.html with {len(spots)} tourist spots from Thrillophilia.")

if __name__ == "__main__":
    print("Fetching tourist spots from Thrillophilia...")
    spots = fetch_tourist_spots()
    
    if spots:
        print(f"Found {len(spots)} tourist spots:")
        for i, spot in enumerate(spots, 1):
            print(f"{i}. {spot['name']}")
        
        update_tourist_spots_html(spots)
    else:
        print("No tourist spots found.") 