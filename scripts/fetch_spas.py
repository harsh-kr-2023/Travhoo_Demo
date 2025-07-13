import requests
from bs4 import BeautifulSoup
import re
from bs4.element import Tag
import html as ihtml

HOTELTHERIO_URL = "https://hoteltherio.com/post/top-30-spas-in-dehradun.p580"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

def extract_rating(rating_text):
    """Extract rating from text like '4.9/5 (2011 Review by google)'"""
    if not rating_text:
        return "4.0"
    
    # Extract rating using regex
    match = re.search(r'(\d+\.?\d*)/5', rating_text)
    if match:
        return match.group(1)
    return "4.0"

def extract_review_count(rating_text):
    """Extract review count from text like '4.9/5 (2011 Review by google)'"""
    if not rating_text:
        return "50"
    
    # Extract review count using regex
    match = re.search(r'\((\d+)\s+Review', rating_text)
    if match:
        return match.group(1)
    return "50"

def clean_text(text):
    """Clean and format text"""
    if not text:
        return ""
    
    # Remove extra whitespace and newlines
    text = re.sub(r'\s+', ' ', text.strip())
    # Decode HTML entities
    text = ihtml.unescape(text)
    return text

def extract_spa_details(card):
    """Extract spa details from a card element"""
    try:
        # Extract title
        title_elem = card.find('span', class_='post-items-name')
        title = clean_text(title_elem.get_text()) if title_elem else "Unknown Spa"
        
        # Extract subtitle/tagline
        subtitle_elem = card.find('h4', class_='special-point')
        subtitle = clean_text(subtitle_elem.get_text()) if subtitle_elem else ""
        
        # Extract image
        img_elem = card.find('img', class_='post-items-thumb')
        img_url = ""
        if img_elem and isinstance(img_elem, Tag):
            img_url = img_elem.get('src', '')
        
        # Extract meta information
        meta_items = card.find_all('li', class_='flex')
        rating = "4.0"
        address = ""
        timings = ""
        pros = ""
        cons = ""
        quality = ""
        staff = ""
        services = ""
        phone = ""
        website = ""
        
        for item in meta_items:
            key_elem = item.find('span', class_='meta-key')
            value_elem = item.find('span', class_='meta-value')
            
            if not key_elem or not value_elem:
                continue
                
            key = clean_text(key_elem.get_text()).lower()
            value = clean_text(value_elem.get_text())
            
            if 'rating' in key:
                rating = extract_rating(value)
            elif 'address' in key:
                address = value
            elif 'time' in key:
                timings = value
            elif 'pros' in key:
                pros = value
            elif 'cons' in key:
                cons = value
            elif 'quality' in key:
                quality = value
            elif 'staff' in key:
                staff = value
            elif 'services' in key:
                services = value
        
        # Extract phone and website from buttons
        buttons = card.find_all('a', class_='info-button')
        for button in buttons:
            href = button.get('href', '')
            if href.startswith('tel:'):
                phone = href.replace('tel:', '')
            elif 'website' in button.get_text().lower():
                website = href
        
        # Extract description
        content_elem = card.find('div', class_='post-items-content')
        description = clean_text(content_elem.get_text()) if content_elem else ""
        
        return {
            'title': title,
            'subtitle': subtitle,
            'img_url': img_url,
            'rating': rating,
            'address': address,
            'timings': timings,
            'pros': pros,
            'cons': cons,
            'quality': quality,
            'staff': staff,
            'services': services,
            'phone': phone,
            'website': website,
            'description': description
        }
        
    except Exception as e:
        print(f"Error extracting spa details: {e}")
        return None

def fetch_spas():
    """Fetch spa data from Hoteltherio"""
    try:
        print("Fetching data from Hoteltherio...")
        response = requests.get(HOTELTHERIO_URL, headers=HEADERS)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all spa cards
        spa_cards = soup.find_all('div', class_='posts')
        print(f"Found {len(spa_cards)} spa cards")
        
        spas = []
        for i, card in enumerate(spa_cards, 1):
            print(f"\nProcessing spa {i}:")
            
            spa_data = extract_spa_details(card)
            if spa_data:
                print(f"  Title: {spa_data['title']}")
                print(f"  Rating: {spa_data['rating']}")
                print(f"  Address: {spa_data['address'][:50]}...")
                spas.append(spa_data)
                print(f"  Successfully extracted: {spa_data['title']}")
            else:
                print(f"  Failed to extract spa {i}")
        
        print(f"\nSuccessfully extracted {len(spas)} spas")
        return spas
        
    except Exception as e:
        print(f"Error fetching spas: {e}")
        return get_fallback_data()

def get_fallback_data():
    """Return fallback spa data if scraping fails"""
    return [
        {
            'title': 'Sparsh Spa & Salon',
            'subtitle': 'Indulge in a tranquil escape for rejuvenation and relaxation',
            'img_url': 'https://images.unsplash.com/photo-1540555700478-4be289fbecef?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=600&q=80',
            'rating': '4.9',
            'address': 'M.K Tower, 2nd Floor, opposite Kawasaki Showroom, Majra, Dehradun, Uttarakhand 248001',
            'timings': '9 AM to 9 PM',
            'pros': 'Hygienic and professional ambience, Experienced and well-trained staff, Range of services to choose from',
            'cons': 'Can get crowded during peak hours, Appointments may be necessary to avoid waiting, Parking space is limited',
            'quality': 'High-quality spa and salon services with attention to detail',
            'staff': 'Experienced therapists, Friendly and courteous, Knowledgeable about treatments',
            'services': 'Haircuts and styling, Facials and skin treatments, Waxing and threading, Massages and body treatments, Manicures and pedicures',
            'phone': '+91 70602 00162',
            'website': 'https://sparshspaandsalon.com/',
            'description': 'Immerse yourself in a sanctuary of tranquility at Sparsh Spa & Salon, Dehradun. Our exquisite spa is renowned for its exceptional body treatments that will rejuvenate your body and mind. Our skilled therapists, armed with intricate techniques and the finest products, will guide you on a blissful journey of relaxation.'
        },
        {
            'title': 'Royal Spa & Salon',
            'subtitle': 'Your sanctuary for relaxation and rejuvenation',
            'img_url': 'https://images.unsplash.com/photo-1544161512-84f9c86cbeb4?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=600&q=80',
            'rating': '4.8',
            'address': '2nd floor, e.c road dwarika store chowk shree tower complex, Dehradun, Uttarakhand 248001',
            'timings': '9 AM to 9 PM',
            'pros': 'Experienced staff, wide range of services, value for money',
            'cons': 'Ambiance could be improved, appointment scheduling may be limited, products may not be the best quality',
            'quality': 'Quality treatments and services provided',
            'staff': 'Experienced therapists, Friendly and courteous, Knowledgeable about treatments, Professional and efficient',
            'services': 'Massages, Facials, Body treatments, Hair services, Nail services',
            'phone': '+91 99972 16502',
            'website': 'http://www.royalspadun.com/',
            'description': 'Immerse yourself in an oasis of tranquility at Royal Spa & Salon, where the moment you step through the door, you\'re enveloped in an atmosphere of warmth and serenity. Our dedicated team of skilled professionals is eager to pamper you with a tailored experience that will leave you revitalized and rejuvenated.'
        }
    ]

def generate_spa_card_html(spa, index):
    """Generate HTML for a single spa card"""
    # Clean up the description for display
    short_desc = spa['description'][:150] + "..." if len(spa['description']) > 150 else spa['description']
    
    # Generate category based on services
    category = "wellness"
    if "massage" in spa['services'].lower():
        category = "massage"
    elif "facial" in spa['services'].lower():
        category = "facial"
    elif "hair" in spa['services'].lower():
        category = "salon"
    
    # Generate price range based on rating
    if float(spa['rating']) >= 4.5:
        price = "Premium"
        price_class = "bg-purple-500"
    elif float(spa['rating']) >= 4.0:
        price = "Mid Range"
        price_class = "bg-orange-500"
    else:
        price = "Budget"
        price_class = "bg-green-500"
    
    # Generate duration based on services
    if "massage" in spa['services'].lower():
        duration = "1-2 hours"
    elif "facial" in spa['services'].lower():
        duration = "45-90 mins"
    else:
        duration = "1-3 hours"
    
    return f'''
    <div class="masonry-item experience-card bg-white rounded-2xl shadow-lg overflow-hidden" data-category="{category}">
        <div class="image-placeholder h-48 flex items-center justify-center relative">
            <img src="{spa['img_url']}" alt="{spa['title']}" class="w-full h-full object-cover" />
            <div class="category-badge absolute top-4 left-4 bg-wellness/20 text-wellness px-3 py-1 rounded-full text-sm font-medium">
                <i class="fas fa-spa mr-1"></i>Wellness
            </div>
            <div class="absolute top-4 right-4 bg-black/50 backdrop-blur-sm rounded-lg p-2 text-white text-xs">
                <div class="text-yellow-400">{'★' * int(float(spa['rating']))}{'☆' * (5 - int(float(spa['rating'])))}</div>
                <div class="text-center">({spa['rating']})</div>
            </div>
        </div>
        <div class="p-6">
            <h3 class="text-xl font-bold text-gray-900 mb-3">{spa['title']}</h3>
            <p class="text-gray-600 text-sm mb-4 leading-relaxed">{short_desc}</p>
            
            <div class="flex items-center justify-between mb-4">
                <div class="duration-badge text-white px-3 py-1 rounded-full text-sm font-medium">
                    <i class="fas fa-clock mr-1"></i>{duration}
                </div>
                <div class="{price_class} text-white px-3 py-1 rounded-full text-sm font-medium">
                    {price}
                </div>
            </div>
            
            <button class="view-details-btn w-full bg-primary text-white py-3 rounded-lg hover:bg-primary-light transition-colors font-medium"
                    data-experience-name="{spa['title']}"
                    data-experience-desc="{spa['description']}"
                    data-experience-img="{spa['img_url']}"
                    data-experience-category="{category}"
                    data-experience-rating="{spa['rating']}"
                    data-experience-location="{spa['address']}"
                    data-experience-timings="{spa['timings']}"
                    data-experience-entry-fees="Varies"
                    data-experience-duration="{duration}"
                    data-experience-price="{price}">
                <i class="fas fa-eye mr-2"></i>View Details
            </button>
        </div>
    </div>
    '''

def update_spa_html(spas):
    """Update the spa.html file with fetched data"""
    try:
        # Read the template HTML file
        with open('spa.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Find the experiences grid section
        start_marker = '<!-- Masonry Grid -->'
        end_marker = '<!-- Experience Details Modal -->'
        
        start_index = html_content.find(start_marker)
        end_index = html_content.find(end_marker)
        
        if start_index == -1 or end_index == -1:
            print("Could not find markers in HTML file")
            return
        
        # Generate new content
        new_content = f'''
        <!-- Masonry Grid -->
        <div class="masonry-grid" id="experiences-grid">
'''
        
        for i, spa in enumerate(spas, 1):
            new_content += generate_spa_card_html(spa, i)
        
        new_content += '''
        </div>
'''
        
        # Replace the content
        before_content = html_content[:start_index]
        after_content = html_content[end_index:]
        
        updated_html = before_content + new_content + after_content
        
        # Update the results count
        updated_html = updated_html.replace('id="results-count">29<', f'id="results-count">{len(spas)}<')
        
        # Write the updated HTML
        with open('spa.html', 'w', encoding='utf-8') as f:
            f.write(updated_html)
        
        print(f"Updated spa.html with {len(spas)} spas.")
        
    except Exception as e:
        print(f"Error updating HTML file: {e}")

def create_spa_html_template():
    """Create the initial spa.html template file"""
    html_template = '''<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Top 30 Spas in Dehradun - Wanderly</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link
      rel="stylesheet"
      href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"
    />
    <script>
      tailwind.config = {
        theme: {
          extend: {
            colors: {
              primary: "#059669",
              "primary-light": "#10b981",
              secondary: "#0ea5e9",
              accent: "#f59e0b",
              earth: "#92400e",
              nature: "#16a34a",
              adventure: "#dc2626",
              heritage: "#7c3aed",
              food: "#ea580c",
              spiritual: "#8b5cf6",
              culture: "#ec4899",
              shopping: "#0891b2",
              wellness: "#06b6d4",
              massage: "#8b5cf6",
              facial: "#ec4899",
              salon: "#f59e0b",
              surface: "#f8fafc",
              "surface-dark": "#e2e8f0",
            },
            fontFamily: {
              sans: ["Inter", "system-ui", "sans-serif"],
            },
          },
        },
      };
    </script>
    <style>
      .experience-card {
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
      }
      .experience-card:hover {
        transform: translateY(-12px);
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
      }
      .hero-bg {
        background-image: linear-gradient(
            rgba(0, 0, 0, 0.4),
            rgba(0, 0, 0, 0.6)
          ),
          url("https://images.unsplash.com/photo-1544161512-84f9c86cbeb4?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
      }
      .filter-button {
        transition: all 0.3s ease;
      }
      .filter-button.active {
        background: linear-gradient(135deg, #059669, #10b981);
        color: white;
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(5, 150, 105, 0.3);
      }
      .category-badge {
        backdrop-filter: blur(10px);
      }
      .price-badge {
        background: linear-gradient(135deg, #f59e0b, #d97706);
      }
      .duration-badge {
        background: linear-gradient(135deg, #0ea5e9, #0284c7);
      }
      .navbar-blur {
        backdrop-filter: blur(20px);
        background: rgba(255, 255, 255, 0.95);
      }
      .masonry-grid {
        column-count: 1;
        column-gap: 1.5rem;
      }
      @media (min-width: 640px) {
        .masonry-grid {
          column-count: 2;
        }
      }
      @media (min-width: 1024px) {
        .masonry-grid {
          column-count: 3;
        }
      }
      @media (min-width: 1280px) {
        .masonry-grid {
          column-count: 4;
        }
      }
      .masonry-item {
        break-inside: avoid;
        margin-bottom: 1.5rem;
        height: 500px; /* Fixed height for all cards */
        display: flex;
        flex-direction: column;
      }
      
      .experience-card {
        height: 100%;
        display: flex;
        flex-direction: column;
      }
      
      .experience-card .p-6 {
        flex: 1;
        display: flex;
        flex-direction: column;
      }
      
      .experience-card p {
        flex: 1;
        overflow: hidden;
        display: -webkit-box;
        -webkit-line-clamp: 3;
        -webkit-box-orient: vertical;
      }
      .image-placeholder {
        background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
        position: relative;
        overflow: hidden;
      }
      .image-placeholder::before {
        content: "";
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(
          90deg,
          transparent,
          rgba(255, 255, 255, 0.4),
          transparent
        );
        animation: shimmer 2s infinite;
      }
      @keyframes shimmer {
        0% {
          left: -100%;
        }
        100% {
          left: 100%;
        }
      }
      .floating-stats {
        position: fixed;
        bottom: 2rem;
        right: 2rem;
        z-index: 40;
      }
    </style>
  </head>
  <body class="bg-surface font-sans">
    <!-- Navigation -->
    <nav class="navbar-blur sticky top-0 z-50 border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <!-- Logo -->
          <div class="flex items-center space-x-3">
            <div
              class="w-10 h-10 bg-primary rounded-xl flex items-center justify-center"
            >
              <i class="fas fa-compass text-white text-lg"></i>
            </div>
            <div>
              <span class="text-xl font-bold text-gray-900">Wanderly</span>
              <div class="text-xs text-gray-500">
                Explore. Discover. Wander.
              </div>
            </div>
          </div>

          <!-- Navigation Links -->
          <div class="hidden md:flex items-center space-x-8">
            <a
              href="#"
              class="text-gray-600 hover:text-primary transition-colors font-medium"
              >Home</a
            >
            <a
              href="#"
              class="text-gray-600 hover:text-primary transition-colors font-medium"
              >Explore</a
            >
            <a
              href="#"
              class="text-primary font-semibold border-b-2 border-primary pb-1"
              >Spas</a
            >
            <a
              href="#"
              class="text-gray-600 hover:text-primary transition-colors font-medium"
              >My Account</a
            >
          </div>

          <!-- CTA Button -->
          <div class="flex items-center space-x-4">
            <button
              class="bg-primary text-white px-6 py-2 rounded-lg hover:bg-primary-light transition-colors font-medium"
            >
              <i class="fas fa-heart mr-2"></i>Wishlist
            </button>

            <!-- Mobile Menu Button -->
            <button class="md:hidden text-gray-600 hover:text-gray-900">
              <i class="fas fa-bars text-xl"></i>
            </button>
          </div>
        </div>
      </div>
    </nav>

    <!-- Hero Section -->
    <section
      class="hero-bg min-h-[70vh] flex items-center justify-center text-white relative overflow-hidden"
    >
      <div
        class="absolute inset-0 bg-gradient-to-r from-primary/30 to-secondary/30"
      ></div>
      <div class="text-center max-w-6xl px-4 relative z-10">
        <!-- Location Badge -->
        <div
          class="inline-flex items-center space-x-2 bg-white/20 backdrop-blur-md rounded-full px-4 py-2 mb-6"
        >
          <i class="fas fa-map-marker-alt text-accent"></i>
          <span class="text-sm font-medium">Dehradun, Uttarakhand</span>
        </div>

        <!-- Main Heading -->
        <h1 class="text-5xl md:text-7xl font-bold mb-6">
          Top 30 Spas in Dehradun
        </h1>

        <!-- Subheading -->
        <p
          class="text-xl md:text-2xl text-blue-100 max-w-4xl mx-auto leading-relaxed mb-12"
        >
          Discover the best spas and wellness centers for ultimate relaxation and rejuvenation.
        </p>

        <!-- Hero Stats -->
        <div class="flex flex-wrap justify-center gap-6 text-sm mb-8">
          <div class="bg-white/20 backdrop-blur-md px-6 py-3 rounded-full">
            <i class="fas fa-spa mr-2"></i>
            <span class="font-semibold">30 Curated Spas</span>
          </div>
          <div class="bg-white/20 backdrop-blur-md px-6 py-3 rounded-full">
            <i class="fas fa-star mr-2"></i>
            <span class="font-semibold">Top Rated</span>
          </div>
          <div class="bg-white/20 backdrop-blur-md px-6 py-3 rounded-full">
            <i class="fas fa-clock mr-2"></i>
            <span class="font-semibold">Updated Daily</span>
          </div>
        </div>

        <!-- Scroll Indicator -->
        <div class="animate-bounce">
          <i class="fas fa-chevron-down text-2xl"></i>
        </div>
      </div>
    </section>

    <!-- Filters Section -->
    <section class="py-8 bg-white sticky top-16 z-40 border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex flex-wrap justify-center gap-3">
          <button
            class="filter-button active px-6 py-3 rounded-full bg-gray-100 text-gray-700 hover:bg-gray-200 font-medium"
            data-filter="all"
          >
            <i class="fas fa-th-large mr-2"></i>All
          </button>
          <button
            class="filter-button px-6 py-3 rounded-full bg-gray-100 text-gray-700 hover:bg-gray-200 font-medium"
            data-filter="wellness"
          >
            <i class="fas fa-spa mr-2"></i>Wellness
          </button>
          <button
            class="filter-button px-6 py-3 rounded-full bg-gray-100 text-gray-700 hover:bg-gray-200 font-medium"
            data-filter="massage"
          >
            <i class="fas fa-hands mr-2"></i>Massage
          </button>
          <button
            class="filter-button px-6 py-3 rounded-full bg-gray-100 text-gray-700 hover:bg-gray-200 font-medium"
            data-filter="facial"
          >
            <i class="fas fa-smile mr-2"></i>Facial
          </button>
          <button
            class="filter-button px-6 py-3 rounded-full bg-gray-100 text-gray-700 hover:bg-gray-200 font-medium"
            data-filter="salon"
          >
            <i class="fas fa-cut mr-2"></i>Salon
          </button>
        </div>
      </div>
    </section>

    <!-- Spas Grid -->
    <section class="py-16 bg-gradient-to-br from-surface to-white">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <!-- Results Counter -->
        <div class="text-center mb-12">
          <h2 class="text-3xl font-bold text-gray-900 mb-4">
            Explore Amazing Spas
          </h2>
          <p class="text-gray-600">
            Showing
            <span id="results-count" class="font-semibold text-primary"
              >30</span
            >
            spas
          </p>
        </div>

        <!-- Masonry Grid -->
        <div class="masonry-grid" id="experiences-grid">
          <!-- Spa cards will be inserted here -->
        </div>
      </div>
    </section>

    <!-- Experience Details Modal -->
    <div id="experience-modal" class="fixed inset-0 bg-black bg-opacity-50 z-50 hidden flex items-center justify-center p-4">
        <div class="bg-white rounded-3xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div class="relative">
                <button id="close-modal" class="absolute top-4 right-4 z-10 bg-white/80 backdrop-blur-sm rounded-full p-2 hover:bg-white transition-colors">
                    <i class="fas fa-times text-gray-600"></i>
                </button>
                <div id="modal-image" class="h-64 bg-cover bg-center rounded-t-3xl relative">
                    <div class="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent"></div>
                    <div class="absolute bottom-4 left-4 text-white">
                        <h2 id="modal-title" class="text-3xl font-bold mb-2"></h2>
                        <div class="flex items-center gap-4">
                            <span id="modal-category" class="bg-white/20 backdrop-blur-sm px-3 py-1 rounded-full text-sm"></span>
                            <div id="modal-rating" class="flex items-center">
                                <i class="fas fa-star text-yellow-400 mr-1"></i>
                                <span id="modal-rating-value"></span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="p-8">
                <div id="modal-description" class="text-gray-700 leading-relaxed text-lg mb-6"></div>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                    <div class="space-y-4">
                        <div class="flex items-center gap-3">
                            <i class="fas fa-map-marker-alt text-red-500 text-lg"></i>
                            <div>
                                <div class="font-semibold text-gray-900">Location</div>
                                <div id="modal-location" class="text-gray-600"></div>
                            </div>
                        </div>
                        <div class="flex items-center gap-3">
                            <i class="fas fa-clock text-blue-500 text-lg"></i>
                            <div>
                                <div class="font-semibold text-gray-900">Timings</div>
                                <div id="modal-timings" class="text-gray-600"></div>
                            </div>
                        </div>
                        <div class="flex items-center gap-3">
                            <i class="fas fa-hourglass-half text-green-500 text-lg"></i>
                            <div>
                                <div class="font-semibold text-gray-900">Duration</div>
                                <div id="modal-duration" class="text-gray-600"></div>
                            </div>
                        </div>
                    </div>
                    <div class="space-y-4">
                        <div class="flex items-center gap-3">
                            <i class="fas fa-ticket-alt text-orange-500 text-lg"></i>
                            <div>
                                <div class="font-semibold text-gray-900">Entry Fees</div>
                                <div id="modal-entry-fees" class="text-gray-600"></div>
                            </div>
                        </div>
                        <div class="flex items-center gap-3">
                            <i class="fas fa-indian-rupee-sign text-purple-500 text-lg"></i>
                            <div>
                                <div class="font-semibold text-gray-900">Price</div>
                                <div id="modal-price" class="text-gray-600"></div>
                            </div>
                        </div>
                        <div class="flex items-center gap-3">
                            <i class="fas fa-tag text-teal-500 text-lg"></i>
                            <div>
                                <div class="font-semibold text-gray-900">Category</div>
                                <div id="modal-category-text" class="text-gray-600"></div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="flex gap-4">
                    <button class="bg-primary text-white px-6 py-3 rounded-lg font-semibold hover:bg-primary-light transition-colors flex items-center">
                        <i class="fas fa-map-marker-alt mr-2"></i>Get Directions
                    </button>
                    <button class="bg-secondary text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors flex items-center">
                        <i class="fas fa-share mr-2"></i>Share
                    </button>
                    <button class="bg-accent text-white px-6 py-3 rounded-lg font-semibold hover:bg-orange-600 transition-colors flex items-center">
                        <i class="fas fa-heart mr-2"></i>Add to Wishlist
                    </button>
                </div>
            </div>
        </div>
    </div>

    <!-- JavaScript -->
    <script>
        // Filter functionality
        document.addEventListener("DOMContentLoaded", function () {
            const filterButtons = document.querySelectorAll(".filter-button");
            const experienceCards = document.querySelectorAll(".experience-card");
            const resultsCount = document.getElementById("results-count");

            filterButtons.forEach((button) => {
                button.addEventListener("click", function () {
                    const filter = this.getAttribute("data-filter");

                    // Remove active class from all buttons
                    filterButtons.forEach((btn) => btn.classList.remove("active"));
                    // Add active class to clicked button
                    this.classList.add("active");

                    // Filter experience cards
                    let visibleCount = 0;
                    experienceCards.forEach((card) => {
                        const category = card.getAttribute("data-category");

                        if (filter === "all" || category === filter) {
                            card.style.display = "block";
                            visibleCount++;
                        } else {
                            card.style.display = "none";
                        }
                    });

                    // Update results count
                    if (resultsCount) {
                        resultsCount.textContent = visibleCount;
                    }
                });
            });

            // Modal functionality
            const modal = document.getElementById("experience-modal");
            const closeModal = document.getElementById("close-modal");
            const modalTitle = document.getElementById("modal-title");
            const modalDescription = document.getElementById("modal-description");
            const modalImage = document.getElementById("modal-image");
            const modalCategory = document.getElementById("modal-category");
            const modalRatingValue = document.getElementById("modal-rating-value");
            const modalLocation = document.getElementById("modal-location");
            const modalTimings = document.getElementById("modal-timings");
            const modalDuration = document.getElementById("modal-duration");
            const modalEntryFees = document.getElementById("modal-entry-fees");
            const modalPrice = document.getElementById("modal-price");
            const modalCategoryText = document.getElementById("modal-category-text");

            // Add event listeners to all view details buttons
            document.addEventListener("click", function(e) {
                if (e.target.classList.contains("view-details-btn")) {
                    const experienceName = e.target.getAttribute("data-experience-name");
                    const experienceDesc = e.target.getAttribute("data-experience-desc");
                    const experienceImg = e.target.getAttribute("data-experience-img");
                    const experienceCategory = e.target.getAttribute("data-experience-category");
                    const experienceRating = e.target.getAttribute("data-experience-rating");
                    const experienceLocation = e.target.getAttribute("data-experience-location");
                    const experienceTimings = e.target.getAttribute("data-experience-timings");
                    const experienceDuration = e.target.getAttribute("data-experience-duration");
                    const experienceEntryFees = e.target.getAttribute("data-experience-entry-fees");
                    const experiencePrice = e.target.getAttribute("data-experience-price");

                    // Populate modal with experience data
                    modalTitle.textContent = experienceName;
                    modalDescription.textContent = experienceDesc;
                    modalImage.style.backgroundImage = `url(${experienceImg})`;
                    modalCategory.textContent = experienceCategory.charAt(0).toUpperCase() + experienceCategory.slice(1);
                    modalRatingValue.textContent = experienceRating;
                    modalLocation.textContent = experienceLocation;
                    modalTimings.textContent = experienceTimings;
                    modalDuration.textContent = experienceDuration;
                    modalEntryFees.textContent = experienceEntryFees;
                    modalPrice.textContent = experiencePrice;
                    modalCategoryText.textContent = experienceCategory.charAt(0).toUpperCase() + experienceCategory.slice(1);

                    // Show modal
                    modal.classList.remove("hidden");
                    document.body.style.overflow = "hidden";
                }
            });

            // Close modal functionality
            closeModal.addEventListener("click", function() {
                modal.classList.add("hidden");
                document.body.style.overflow = "auto";
            });

            // Close modal when clicking outside
            modal.addEventListener("click", function(e) {
                if (e.target === modal) {
                    modal.classList.add("hidden");
                    document.body.style.overflow = "auto";
                }
            });

            // Close modal with Escape key
            document.addEventListener("keydown", function(e) {
                if (e.key === "Escape" && !modal.classList.contains("hidden")) {
                    modal.classList.add("hidden");
                    document.body.style.overflow = "auto";
                }
            });
        });
    </script>
  </body>
</html>'''
    
    with open('spa.html', 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    print("Created spa.html template file.")

if __name__ == "__main__":
    # Create the template file if it doesn't exist
    try:
        with open('spa.html', 'r', encoding='utf-8') as f:
            pass
    except FileNotFoundError:
        create_spa_html_template()
    
    # Fetch spa data and update HTML
    spas = fetch_spas()
    if spas:
        update_spa_html(spas)
    else:
        print("Failed to fetch spa data.") 