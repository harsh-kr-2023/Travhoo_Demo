import requests
from bs4 import BeautifulSoup
import re
from bs4.element import Tag
import html as ihtml

TRAVELTRIANGLE_URL = "https://traveltriangle.com/blog/shopping-in-dehradun/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

CATEGORY_MAP = {
    "bazaar": "traditional",
    "market": "street",
    "road": "clothing",
    "hall": "handicraft",
    "mall": "traditional",
    "food": "food",
}

# Helper to guess category
def guess_category(name, desc):
    name = name.lower()
    desc = desc.lower()
    for key, val in CATEGORY_MAP.items():
        if key in name or key in desc:
            return val
    return "traditional"

def fetch_local_markets():
    resp = requests.get(TRAVELTRIANGLE_URL, headers=HEADERS)
    if resp.status_code != 200:
        print("Failed to fetch page:", resp.status_code)
        return []
    soup = BeautifulSoup(resp.text, "html.parser")
    markets = []
    # Find all h3 with id (market anchors)
    for h3 in soup.find_all("h3", id=True):
        name = h3.get_text(strip=True)
        # Find next image
        img = None
        sib = h3.find_next_sibling()
        while sib and not (isinstance(sib, Tag) and sib.find("img")):
            sib = sib.find_next_sibling()
        if sib and isinstance(sib, Tag):
            img_tag = sib.find("img")
            if isinstance(img_tag, Tag):
                img = img_tag.get("data-src")
                if not img:
                    img = img_tag.get("src")
                if isinstance(img, str) and img.startswith("//"):
                    img = "https:" + img
        # Find all <p> until next h3
        desc = ""
        details = {}
        p = h3.find_next("p")
        while p and isinstance(p, Tag) and p.name == "p":
            txt = p.get_text(" ", strip=True)
            # Extract details
            for field in ["Location:", "What to Buy:", "Timings:", "Speciality:"]:
                if field in txt:
                    details[field[:-1].lower()] = txt.split(field,1)[-1].strip()
            if not any(f in txt for f in ["Location:", "What to Buy:", "Timings:", "Speciality:"]):
                desc += txt + " "
            p = p.find_next_sibling()
            if p and isinstance(p, Tag) and p.name == "h3": break
        desc = desc.strip()
        # Fallbacks
        location = details.get("location", "")
        what_to_buy = details.get("what to buy", "")
        timings = details.get("timings", "")
        speciality = details.get("speciality", "")
        # Generate a random rating for demo
        import random
        rating = round(random.uniform(3.8, 4.7), 1)
        # Category
        category = guess_category(name, desc)
        markets.append({
            "name": name,
            "img": img or "https://placehold.co/400x300?text=Market",
            "desc": desc,
            "location": location,
            "what_to_buy": what_to_buy,
            "timings": timings,
            "speciality": speciality,
            "category": category,
            "rating": rating,
        })
    return markets

def generate_market_card_html(market):
    # Clean and format data
    short_desc = (market["desc"][:100] + "...") if len(market["desc"]) > 100 else market["desc"]
    pop_items = market["what_to_buy"] or "Various items"
    speciality = market["speciality"] or "Local specialties"
    location = market["location"] or "Dehradun"
    timings = market["timings"] or "10 AM - 8 PM"
    
    # Category styling
    cat_class = f"category-{market['category']}"
    cat_emoji = {
        "traditional": "🏛️",
        "street": "🛣️", 
        "clothing": "👕",
        "handicraft": "🎨",
        "food": "🍽️"
    }.get(market['category'], "🏪")
    
    # Generate star rating
    rating = float(market['rating'])
    stars = "★" * int(rating) + "☆" * (5 - int(rating))
    
    return f'''
    <div class="market-card card-hover rounded-xl shadow-lg overflow-hidden bg-white" data-category="{market['category']}">
        <div class="relative h-48 overflow-hidden">
            <img src="{market['img']}" alt="{ihtml.escape(market['name'])}" class="card-image w-full h-full object-cover transition-transform duration-300" />
            <div class="absolute inset-0 bg-gradient-to-t from-black/20 via-transparent to-transparent"></div>
            <div class="absolute top-3 right-3">
                <button class="bg-white/90 backdrop-blur-sm p-2 rounded-full hover:bg-white transition-colors shadow-lg">
                    <i data-lucide="map-pin" class="h-4 w-4 text-primary"></i>
                </button>
            </div>
            <div class="absolute top-3 left-3">
                <span class="bg-green-500 text-white px-2 py-1 rounded-full text-xs font-medium shadow-lg">
                    <i data-lucide="clock" class="h-3 w-3 inline mr-1"></i>Open
                </span>
            </div>
            <div class="absolute bottom-3 left-3 right-3">
                <div class="bg-black/70 backdrop-blur-sm rounded-lg p-3 text-white">
                    <h3 class="text-lg font-bold mb-1">{ihtml.escape(market['name'])}</h3>
                    <div class="flex items-center space-x-2 text-sm">
                        <span class="text-yellow-400">{stars}</span>
                        <span class="text-gray-300">({market['rating']})</span>
                    </div>
                </div>
            </div>
        </div>
        <div class="p-5">
            <div class="mb-4">
                <p class="text-gray-600 text-sm leading-relaxed">{ihtml.escape(short_desc)}</p>
            </div>
            
            <div class="mb-4">
                <h4 class="font-semibold text-gray-900 mb-2 flex items-center">
                    <i data-lucide="shopping-bag" class="h-4 w-4 mr-2 text-primary"></i>
                    Popular Items
                </h4>
                <div class="flex flex-wrap gap-2">
                    <span class="bg-gradient-to-r from-orange-500 to-red-500 text-white px-3 py-1 rounded-full text-xs font-medium">
                        {ihtml.escape(pop_items)}
                    </span>
                </div>
            </div>
            
            <div class="mb-4 space-y-2">
                <div class="flex items-center text-sm text-gray-600">
                    <i data-lucide="clock" class="h-4 w-4 mr-2 text-primary"></i>
                    <span>{ihtml.escape(timings)}</span>
                </div>
                <div class="flex items-center text-sm text-gray-600">
                    <i data-lucide="map-pin" class="h-4 w-4 mr-2 text-primary"></i>
                    <span>{ihtml.escape(location)}</span>
                </div>
            </div>
            
            <div class="mb-4">
                <h4 class="font-semibold text-gray-900 mb-2 flex items-center">
                    <i data-lucide="sparkles" class="h-4 w-4 mr-2 text-primary"></i>
                    Speciality
                </h4>
                <div class="bg-gradient-to-r from-blue-500 to-purple-500 text-white p-3 rounded-lg text-sm">
                    {ihtml.escape(speciality)}
                </div>
            </div>
            
            <div class="flex items-center justify-between">
                <div class="flex items-center space-x-2">
                    <span class="{cat_class} px-3 py-1 rounded-full text-xs font-medium">
                        {cat_emoji} {market['category'].capitalize()}
                    </span>
                </div>
                <button class="view-details-btn bg-gradient-to-r from-primary to-purple text-white px-6 py-2 rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all duration-300 font-medium text-sm shadow-lg transform hover:scale-105"
                        data-market-name="{ihtml.escape(market['name'])}"
                        data-market-desc="{ihtml.escape(market['desc'])}"
                        data-market-img="{market['img']}"
                        data-market-category="{market['category']}"
                        data-market-rating="{market['rating']}"
                        data-market-location="{ihtml.escape(location)}"
                        data-market-timings="{ihtml.escape(timings)}"
                        data-market-what-to-buy="{ihtml.escape(pop_items)}"
                        data-market-speciality="{ihtml.escape(speciality)}">
                    <i data-lucide="eye" class="h-4 w-4 inline mr-2"></i>
                    View Details
                </button>
            </div>
        </div>
    </div>
    '''

def update_local_market_html(markets):
    with open("local_market.html", encoding="utf-8") as f:
        html = f.read()
    # Find the markets grid
    start_marker = '<div id="markets-grid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">'
    start = html.find(start_marker)
    if start == -1:
        print("Could not find markets grid section in HTML.")
        return
    start += len(start_marker)
    end = html.find("</div>", start)
    if end == -1:
        print("Could not find end of markets grid section.")
        return
    # Generate new cards
    cards_html = "\n".join([generate_market_card_html(m) for m in markets])
    # Update HTML
    new_html = html[:start] + "\n" + cards_html + "\n" + html[end:]
    with open("local_market.html", "w", encoding="utf-8") as f:
        f.write(new_html)
    print(f"Updated local_market.html with {len(markets)} markets.")

if __name__ == "__main__":
    markets = fetch_local_markets()
    update_local_market_html(markets) 