import requests
from bs4 import BeautifulSoup
import re
from bs4.element import Tag
import html as ihtml

THRILLOPHILIA_URL = "https://www.thrillophilia.com/destinations/dehradun/things-to-do"
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
    "heritage": "heritage"
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
    """Create experiences data based on provided HTML structure"""
    experiences_data = [
        {
            "name": "Picnic and Fun at Malsi Deer Park",
            "img": "https://media2.thrillophilia.com/images/photos/000/142/601/original/1548920021_shutterstock_599756276.jpg?w=753&h=450&dpr=1.0",
            "desc": "What could be more amazing than making a joyful picnic in the midst of flora and fauna? Well, just hop into Malsi deer park where you can find soothing greenery, happy deer and they all are capable of making every visitor cheerful. And not only deer but you also get to see exotic birds, parrots, nilgai, 2-horned deer and much more. This wildlife picnic spot is also loaded with waterbodies, slides for kids and canteen for healthy eatables. Do not miss a chance to spend some quality time with your family and kids, while in Dehradun.",
            "location": "Dehradun zoo which is 10 km from Rajpur road",
            "timings": "10.00 AM to 5.00 PM",
            "entry_fees": "INR 20 per person",
            "category": "nature",
            "rating": 4.5,
            "duration": "3 hours",
            "price": "From ₹20"
        },
        {
            "name": "Visit the Distinct Location of Tapkeshwar Temple",
            "img": "https://media2.thrillophilia.com/images/photos/000/142/608/original/1548920984_shutterstock_395045821.jpg?w=753&h=450&dpr=1.0",
            "desc": "The temple is located on the river banks of Tons Nadi river and one of the very ancient space to offer prayers. Hosting a fair on every Shivratri, it attracts hundreds of devotees and let them relish in the peace. The major shrine is lying within the cave where water drips on the Shivling, giving the name of Tapkeshawar Mahadev. The cool sulfur water springs are an additional feature the temple where the devotees love to take a bath before they enter inside the temple.",
            "location": "Garhi Cantt, Birpur, Dehradun",
            "timings": "9 am to 1 pm and 1:30 pm to 5:30 pm all days of the week",
            "entry_fees": "None",
            "category": "spiritual",
            "rating": 4.7,
            "duration": "2 hours",
            "price": "Free"
        },
        {
            "name": "Forest Research Institute Tour",
            "img": "https://images.unsplash.com/photo-1599661046827-dacde6976549?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80",
            "desc": "Explore the magnificent colonial architecture of Forest Research Institute, one of the oldest institutions of its kind. The campus features stunning buildings, museums dedicated to forestry, and beautiful gardens. Learn about India's rich forest heritage and conservation efforts.",
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
            "desc": "Natural limestone caves with therapeutic sulfur springs and waterfalls. The name Sahastradhara means 'thousand fold spring' and the water is believed to have medicinal properties. Perfect for a refreshing day trip.",
            "location": "Sahastradhara Road, Dehradun",
            "timings": "6 AM - 6 PM",
            "entry_fees": "INR 50 per person",
            "category": "nature",
            "rating": 4.4,
            "duration": "4 hours",
            "price": "From ₹50"
        },
        {
            "name": "Robber's Cave Adventure",
            "img": "https://images.unsplash.com/photo-1559827260-dc66d52bef19?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80",
            "desc": "Explore the mysterious Robber's Cave, a natural cave formation with a stream flowing through it. Perfect for adventure seekers and nature lovers. The cave is surrounded by lush greenery and offers a unique trekking experience.",
            "location": "Anarwala, Dehradun",
            "timings": "8 AM - 5 PM",
            "entry_fees": "INR 30 per person",
            "category": "adventure",
            "rating": 4.3,
            "duration": "3 hours",
            "price": "From ₹30"
        },
        {
            "name": "Mindrolling Monastery Visit",
            "img": "https://images.unsplash.com/photo-1542810634-71277d95dcbb?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80",
            "desc": "Visit the largest Tibetan monastery in India, known for its stunning architecture and peaceful atmosphere. The monastery houses beautiful Buddhist art, prayer halls, and offers meditation sessions for visitors.",
            "location": "Clement Town, Dehradun",
            "timings": "6 AM - 6 PM",
            "entry_fees": "Free",
            "category": "spiritual",
            "rating": 4.8,
            "duration": "2 hours",
            "price": "Free"
        },
        {
            "name": "Paltan Bazaar Shopping Experience",
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
    
    return experiences_data

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
    
    with open("experience.html", "w", encoding="utf-8") as f:
        f.write(new_html)
    
    print(f"Updated experience.html with {len(experiences)} experiences.")

if __name__ == "__main__":
    experiences = fetch_experiences()
    if experiences:
        update_experience_html(experiences)
    else:
        print("No experiences found.") 