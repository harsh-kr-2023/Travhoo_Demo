import requests
from bs4 import BeautifulSoup
import re
from bs4.element import Tag

BLOG_URL = "https://traveltriangle.com/blog/restaurants-in-dehradun/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

def fetch_restaurants_from_blog():
    response = requests.get(BLOG_URL, headers=headers)
    if response.status_code != 200:
        print("Failed to fetch blog page:", response.status_code)
        return []
    soup = BeautifulSoup(response.text, "html.parser")
    # Find all restaurant sections by <h3 id=...>
    restaurants = []
    for h3 in soup.find_all("h3", id=True):
        name = h3.get_text(strip=True)
        # Skip if it's not a restaurant (like FAQ section)
        if "Frequently Asked Questions" in name:
            continue
            
        # The next <div> is the image
        img_url = None
        must_try = location = timings = cuisine = ratings = avg_cost = desc = website = reviews = None
        
        # Find the image div
        img_div = h3.find_next_sibling("div")
        if isinstance(img_div, Tag):
            img_tag = img_div.find("img")
            if isinstance(img_tag, Tag) and img_tag.has_attr("data-src"):
                img_url = img_tag["data-src"]
            elif isinstance(img_tag, Tag) and img_tag.has_attr("src"):
                img_url = img_tag["src"]
        
        # Find description and details by looking for <p> tags after the image div
        current = img_div if isinstance(img_div, Tag) else h3
        desc_parts = []
        details_html = None
        # Look for the next few siblings to find description and details
        for i in range(20):  # Check next 20 siblings
            current = current.find_next_sibling()
            if not current:
                break
            if isinstance(current, Tag):
                if current.name == "p":
                    if isinstance(current, Tag) and current.find("strong"):
                        details_html = str(current)
                        break
                    else:
                        desc_parts.append(current.get_text(strip=True))
                elif current.name == "div":
                    p_tags = current.find_all("p") if isinstance(current, Tag) else []
                    for p in p_tags:
                        if isinstance(p, Tag) and p.find("strong"):
                            details_html = str(p)
                            break
                        elif isinstance(p, Tag):
                            desc_parts.append(p.get_text(strip=True))
                    if details_html:
                        break
        desc = " ".join(desc_parts) if desc_parts else None
        
        # Parse details if found
        if details_html:
            def extract_field(label):
                if details_html is None:
                    return None
                m = re.search(rf"<strong>{label}:</strong>\s*([^<]*)", details_html)
                return m.group(1).strip() if m else None
            
            must_try = extract_field("Must Try")
            location = extract_field("Location")
            timings = extract_field("Timings")
            cuisine = extract_field("Cuisine")
            ratings = extract_field("Zomato Ratings") or extract_field("Google Ratings")
            avg_cost = extract_field("Average Meal For Two \\(Without Alcohol\\)")
            
            # Website/Reviews links
            soup_details = BeautifulSoup(details_html, "html.parser")
            links = soup_details.find_all("a", class_="external-link")
            if links:
                website = getattr(links[0], 'get', lambda x: None)('href') if len(links) > 0 else None
                reviews = getattr(links[1], 'get', lambda x: None)('href') if len(links) > 1 else None
        
        restaurants.append({
            "name": name,
            "img_url": img_url,
            "desc": desc,
            "must_try": must_try,
            "location": location,
            "timings": timings,
            "cuisine": cuisine,
            "ratings": ratings,
            "avg_cost": avg_cost,
            "website": website,
            "reviews": reviews
        })
    return restaurants

def generate_card_html_blog(resto):
    img = resto["img_url"] or "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80"
    rating = resto["ratings"] or "No rating"
    cuisine = resto["cuisine"] or "-"
    must_try = f'<p class="text-sm text-gray-600 mb-1"><strong>Must Try:</strong> {resto["must_try"]}</p>' if resto["must_try"] else ""
    location = f'<p class="text-sm text-gray-600 mb-1"><strong>Location:</strong> {resto["location"]}</p>' if resto["location"] else ""
    timings = f'<p class="text-sm text-gray-600 mb-1"><strong>Timings:</strong> {resto["timings"]}</p>' if resto["timings"] else ""
    avg_cost = f'<p class="text-sm text-gray-600 mb-1"><strong>Avg Cost:</strong> {resto["avg_cost"]}</p>' if resto["avg_cost"] else ""
    website = f'<a href="{resto["website"]}" target="_blank" class="text-blue-600 underline mr-2">Website</a>' if resto["website"] else ""
    reviews = f'<a href="{resto["reviews"]}" target="_blank" class="text-blue-600 underline">Reviews</a>' if resto["reviews"] else ""
    desc = f'<p class="text-gray-600 mb-4 italic">{resto["desc"]}</p>' if resto["desc"] else ""
    # Simple star rating extraction
    stars = ""
    match = re.search(r"([0-9.]+)[/ ]*5", str(rating))
    if match:
        val = float(match.group(1))
        full = int(val)
        half = 1 if val - full >= 0.5 else 0
        empty = 5 - full - half
        stars = '<div class="rating-stars text-xl mr-2">' + \
            '<i class="fas fa-star"></i>' * full + \
            ('<i class="fas fa-star-half-alt"></i>' if half else '') + \
            '<i class="far fa-star"></i>' * empty + '</div>'
    else:
        stars = '<div class="rating-stars text-xl mr-2">' + '<i class="far fa-star"></i>' * 5 + '</div>'
    # Card HTML
    return f'''
    <div class="restaurant-card bg-white rounded-2xl shadow-lg overflow-hidden mb-12 grid md:grid-cols-2 gap-0">
      <div class="relative overflow-hidden">
        <img src="{img}" alt="{resto['name']}" class="w-full h-full object-cover" />
        <div class="absolute top-4 left-4">
          <span class="cuisine-tag bg-green-500/90 text-white px-3 py-1 rounded-full text-sm font-medium">
            <i class="fas fa-leaf mr-1"></i>{cuisine}
          </span>
        </div>
      </div>
      <div class="p-8 flex flex-col justify-center">
        <h3 class="text-2xl font-bold text-gray-800 mb-2">{resto['name']}</h3>
        {desc}
        <div class="flex items-center mb-4">
          {stars}
          <span class="text-gray-600 font-medium">{rating}</span>
        </div>
        {must_try}
        {location}
        {timings}
        {avg_cost}
        <div class="mb-2">{website}{reviews}</div>
        <button class="bg-gradient-to-r from-amber-500 to-orange-500 text-white px-6 py-3 rounded-lg font-semibold hover:from-amber-600 hover:to-orange-600 transition-all transform hover:scale-105">
          <i class="fas fa-calendar-check mr-2"></i>Book a Table
        </button>
      </div>
    </div>
    '''

def update_html_blog(restaurants):
    with open("restaurant_dehradun.html", "r", encoding="utf-8") as f:
        html = f.read()
    start_marker = '<div class="container mx-auto px-4 max-w-6xl">'
    start = html.find(start_marker)
    if start == -1:
        print("Could not find start marker in HTML.")
        return
    start += len(start_marker)
    # Find the matching closing div for the container
    open_divs = 1
    i = start
    while open_divs > 0 and i < len(html):
        if html[i:i+5] == '<div ':
            open_divs += 1
        elif html[i:i+6] == '</div>':
            open_divs -= 1
        i += 1
    cards_end = i - 6
    new_html = html[:start] + '\n' + '\n'.join([generate_card_html_blog(r) for r in restaurants]) + '\n' + html[cards_end:]
    with open("restaurant_dehradun.html", "w", encoding="utf-8") as f:
        f.write(new_html)
    print(f"Updated restaurant_dehradun.html with {len(restaurants)} restaurants from blog.")

if __name__ == "__main__":
    restaurants = fetch_restaurants_from_blog()
    if restaurants:
        update_html_blog(restaurants)
    else:
        print("No restaurants found from blog.")
