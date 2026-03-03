# """
# demo_data.py — sample product data for offline / demo mode.
# Each scraper calls this when network fetching fails.
# """

# DEMO_BOOKS = [
#     {"product": "The Great Gatsby",              "price": 10.99, "rating": 4, "in_stock": True, "category": "books", "source_url": "demo"},
#     {"product": "To Kill a Mockingbird",         "price": 12.50, "rating": 5, "in_stock": True, "category": "books", "source_url": "demo"},
#     {"product": "1984",                          "price": 9.99,  "rating": 5, "in_stock": True, "category": "books", "source_url": "demo"},
#     {"product": "The Catcher in the Rye",        "price": 11.75, "rating": 3, "in_stock": True, "category": "books", "source_url": "demo"},
#     {"product": "Brave New World",               "price": 8.99,  "rating": 4, "in_stock": True, "category": "books", "source_url": "demo"},
#     {"product": "The Alchemist",                 "price": 13.00, "rating": 4, "in_stock": True, "category": "books", "source_url": "demo"},
#     {"product": "Animal Farm",                   "price": 7.50,  "rating": 4, "in_stock": True, "category": "books", "source_url": "demo"},
#     {"product": "Crime and Punishment",          "price": 14.99, "rating": 4, "in_stock": True, "category": "books", "source_url": "demo"},
#     {"product": "The Hobbit",                    "price": 15.99, "rating": 5, "in_stock": True, "category": "books", "source_url": "demo"},
#     {"product": "Harry Potter and the Sorcerer's Stone", "price": 16.99, "rating": 5, "in_stock": True, "category": "books", "source_url": "demo"},
#     {"product": "Sapiens",                       "price": 18.00, "rating": 4, "in_stock": True, "category": "books", "source_url": "demo"},
#     {"product": "Atomic Habits",                 "price": 17.50, "rating": 5, "in_stock": True, "category": "books", "source_url": "demo"},
# ]

# DEMO_LAPTOPS = [
#     {"product": "Lenovo ThinkPad X1 Carbon Gen 11",    "price": 1349.99, "rating": 5, "reviews": 312, "description": "14\" IPS, Intel Core i7, 16GB RAM, 512GB SSD", "in_stock": True, "category": "laptops", "source_url": "demo"},
#     {"product": "HP Pavilion 15 Laptop",                "price": 649.00,  "rating": 4, "reviews": 204, "description": "15.6\" FHD, Ryzen 5, 8GB RAM, 256GB SSD",     "in_stock": True, "category": "laptops", "source_url": "demo"},
#     {"product": "Dell XPS 13",                          "price": 1199.99, "rating": 5, "reviews": 520, "description": "13.4\" OLED, Core i7, 16GB, 512GB SSD",       "in_stock": True, "category": "laptops", "source_url": "demo"},
#     {"product": "ASUS VivoBook 15",                     "price": 499.99,  "rating": 3, "reviews": 150, "description": "15.6\" FHD, Core i5, 8GB, 256GB SSD",         "in_stock": True, "category": "laptops", "source_url": "demo"},
#     {"product": "Apple MacBook Air M2",                 "price": 1099.00, "rating": 5, "reviews": 980, "description": "13.6\" Liquid Retina, Apple M2, 8GB, 256GB",  "in_stock": True, "category": "laptops", "source_url": "demo"},
#     {"product": "Acer Nitro 5 Gaming Laptop",           "price": 799.99,  "rating": 4, "reviews": 340, "description": "15.6\" 144Hz, Core i5, RTX 3050, 16GB",       "in_stock": True, "category": "laptops", "source_url": "demo"},
#     {"product": "Microsoft Surface Laptop 5",           "price": 999.99,  "rating": 4, "reviews": 210, "description": "13.5\" PixelSense, Core i5, 16GB, 256GB",      "in_stock": True, "category": "laptops", "source_url": "demo"},
#     {"product": "Samsung Galaxy Book3 Pro",             "price": 1149.99, "rating": 4, "reviews": 175, "description": "14\" AMOLED, Core i7, 16GB, 512GB SSD",        "in_stock": True, "category": "laptops", "source_url": "demo"},
# ]

# DEMO_MOBILES = [
#     {"product": "iPhone 15 Pro",                     "price": 999.00,  "rating": 5, "reviews": 1200, "description": "6.1\" Super Retina, A17 Pro chip, 128GB",     "in_stock": True, "category": "mobiles", "source_url": "demo"},
#     {"product": "Samsung Galaxy S24",                "price": 799.99,  "rating": 5, "reviews": 890,  "description": "6.2\" Dynamic AMOLED, Snapdragon 8 Gen 3",    "in_stock": True, "category": "mobiles", "source_url": "demo"},
#     {"product": "Google Pixel 8",                    "price": 699.00,  "rating": 4, "reviews": 540,  "description": "6.2\" OLED, Google Tensor G3, 128GB",         "in_stock": True, "category": "mobiles", "source_url": "demo"},
#     {"product": "OnePlus 12",                        "price": 799.00,  "rating": 4, "reviews": 430,  "description": "6.82\" LTPO AMOLED 120Hz, Snapdragon 8 Gen 3","in_stock": True, "category": "mobiles", "source_url": "demo"},
#     {"product": "Xiaomi 14",                         "price": 649.99,  "rating": 4, "reviews": 310,  "description": "6.36\" AMOLED, Snapdragon 8 Gen 3, 512GB",    "in_stock": True, "category": "mobiles", "source_url": "demo"},
#     {"product": "iPhone 15",                         "price": 799.00,  "rating": 5, "reviews": 1050, "description": "6.1\" Super Retina XDR, A16 Bionic, 128GB",   "in_stock": True, "category": "mobiles", "source_url": "demo"},
#     {"product": "Samsung Galaxy A55",                "price": 449.99,  "rating": 4, "reviews": 280,  "description": "6.6\" Super AMOLED, 8GB RAM, 256GB",          "in_stock": True, "category": "mobiles", "source_url": "demo"},
#     {"product": "Motorola Edge 40",                  "price": 349.99,  "rating": 3, "reviews": 180,  "description": "6.55\" OLED 144Hz, Dimensity 8020, 256GB",    "in_stock": True, "category": "mobiles", "source_url": "demo"},
# ]

# DEMO_PAINTS = [
#     {"product": "Premium Acrylic Paint Set 24 Colors",  "price": 24.99, "rating": 5, "description": "Professional-grade acrylics, vibrant, fast-drying",   "in_stock": True, "category": "paints", "source_url": "demo"},
#     {"product": "Artist Watercolor Palette 36 Pans",    "price": 34.99, "rating": 4, "description": "High-transparency watercolors for fine art",           "in_stock": True, "category": "paints", "source_url": "demo"},
#     {"product": "Interior Latex Paint Eggshell White 1gal","price": 42.00,"rating": 4,"description": "Premium wall paint, low-VOC, washable",              "in_stock": True, "category": "paints", "source_url": "demo"},
#     {"product": "Chalk Paint Vintage Blue 1L",          "price": 19.99, "rating": 5, "description": "Furniture chalk paint, no-prep required",              "in_stock": True, "category": "paints", "source_url": "demo"},
#     {"product": "Spray Paint Matte Black 400ml",        "price": 8.99,  "rating": 4, "description": "Multi-surface spray, dries in 20 minutes",             "in_stock": True, "category": "paints", "source_url": "demo"},
#     {"product": "Exterior Weather Shield 5L",           "price": 55.00, "rating": 5, "description": "Weatherproof masonry paint, 10-year durability",       "in_stock": True, "category": "paints", "source_url": "demo"},
#     {"product": "Oil Paint Studio Kit 12 Tubes",        "price": 38.50, "rating": 4, "description": "Artist-grade oil paints, 37ml tubes",                 "in_stock": True, "category": "paints", "source_url": "demo"},
#     {"product": "Glow-in-Dark Paint Set 8 Colors",      "price": 15.99, "rating": 4, "description": "Non-toxic luminescent paints for crafts & decor",     "in_stock": True, "category": "paints", "source_url": "demo"},
#     {"product": "Metallic Craft Paint Bundle 6pc",      "price": 12.50, "rating": 3, "description": "Gold, silver, copper metallic craft paints",           "in_stock": True, "category": "paints", "source_url": "demo"},
#     {"product": "Fabric Textile Paint 10 Colors",       "price": 18.99, "rating": 4, "description": "Permanent, machine-wash-safe fabric paint",            "in_stock": True, "category": "paints", "source_url": "demo"},
# ]

# DEMO_ELECTRONICS = [
#     {"product": "Sony WH-1000XM5 Wireless Headphones",  "price": 349.99, "rating": 5, "reviews": 2100, "description": "Industry-leading ANC, 30hr battery",          "in_stock": True, "category": "electronics", "source_url": "demo"},
#     {"product": "iPad Air (5th Gen) 64GB",               "price": 599.00, "rating": 5, "reviews": 880,  "description": "10.9\" Liquid Retina, M1 chip",                "in_stock": True, "category": "electronics", "source_url": "demo"},
#     {"product": "Sony Alpha A7 IV Mirrorless Camera",    "price": 2499.00,"rating": 5, "reviews": 430,  "description": "33MP full-frame, 4K60p video",                 "in_stock": True, "category": "electronics", "source_url": "demo"},
#     {"product": "LG 27\" 4K UHD Monitor",               "price": 349.00, "rating": 4, "reviews": 560,  "description": "IPS panel, HDR600, USB-C connectivity",         "in_stock": True, "category": "electronics", "source_url": "demo"},
#     {"product": "JBL Charge 5 Portable Speaker",        "price": 179.99, "rating": 4, "reviews": 740,  "description": "IP67 waterproof, 20hr battery, PartyBoost",    "in_stock": True, "category": "electronics", "source_url": "demo"},
#     {"product": "Samsung 65\" QLED 4K TV",              "price": 897.99, "rating": 5, "reviews": 1200, "description": "Quantum HDR, 120Hz, Smart TV",                  "in_stock": True, "category": "electronics", "source_url": "demo"},
#     {"product": "Logitech MX Master 3S Mouse",           "price": 99.99,  "rating": 5, "reviews": 1800, "description": "8K DPI, MagSpeed scroll, silent clicks",       "in_stock": True, "category": "electronics", "source_url": "demo"},
#     {"product": "Amazon Echo Show 10",                   "price": 249.99, "rating": 4, "reviews": 650,  "description": "10.1\" HD screen, 360° rotating, Alexa",       "in_stock": True, "category": "electronics", "source_url": "demo"},
# ]

# DEMO_DATA = {
#     "books":       DEMO_BOOKS,
#     "laptops":     DEMO_LAPTOPS,
#     "mobiles":     DEMO_MOBILES,
#     "paints":      DEMO_PAINTS,
#     "electronics": DEMO_ELECTRONICS,
# }