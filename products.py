products = [
    {
        "id": 1,
        "name": "UI/UX Design Mastery",
        "category": "courses",
        "price": 49.99,
        "emoji": "🎓",
        "description": "Complete guide to modern UI/UX design principles and tools.",
    },
    {
        "id": 2,
        "name": "JavaScript Pro eBook",
        "category": "ebooks",
        "price": 19.99,
        "emoji": "📘",
        "description": "Deep dive into advanced JavaScript concepts and patterns.",
    },
    {
        "id": 3,
        "name": "Landing Page Templates",
        "category": "templates",
        "price": 29.99,
        "emoji": "🎨",
        "description": "10 premium responsive landing page templates for any business.",
    },
    {
        "id": 4,
        "name": "SEO Toolkit Pro",
        "category": "software",
        "price": 79.99,
        "emoji": "🔧",
        "description": "All-in-one SEO analysis and optimization software.",
    },
    {
        "id": 5,
        "name": "Python for Data Science",
        "category": "courses",
        "price": 59.99,
        "emoji": "🐍",
        "description": "Learn data science with Python from scratch to advanced.",
    },
    {
        "id": 6,
        "name": "Startup Playbook",
        "category": "ebooks",
        "price": 14.99,
        "emoji": "🚀",
        "description": "Step-by-step guide to launching your first startup.",
    },
    {
        "id": 7,
        "name": "Dashboard UI Kit",
        "category": "templates",
        "price": 39.99,
        "emoji": "📊",
        "description": "Modern admin dashboard templates with dark and light modes.",
    },
    {
        "id": 8,
        "name": "Password Manager",
        "category": "software",
        "price": 24.99,
        "emoji": "🔐",
        "description": "Secure, encrypted password manager for all your accounts.",
    },
    {
        "id": 9,
        "name": "Social Media Templates",
        "category": "templates",
        "price": 19.99,
        "emoji": "📱",
        "description": "50+ editable social media post and story templates.",
    },
    {
        "id": 10,
        "name": "Crypto Trading Guide",
        "category": "ebooks",
        "price": 24.99,
        "emoji": "💰",
        "description": "Master crypto trading strategies and risk management.",
    },
    {
        "id": 11,
        "name": "Full-Stack Web Dev",
        "category": "courses",
        "price": 89.99,
        "emoji": "💻",
        "description": "Build full-stack apps with React, Node.js, and MongoDB.",
    },
    {
        "id": 12,
        "name": "Code Editor Pro",
        "category": "software",
        "price": 34.99,
        "emoji": "⚡",
        "description": "Lightweight, blazing-fast code editor with AI autocomplete.",
    },
]


def get_categories():
    return list(sorted(set(p["category"] for p in products)))


def get_products_by_category(category):
    return [p for p in products if p["category"] == category]


def get_product_by_id(product_id):
    return next((p for p in products if p["id"] == product_id), None)


def search_products(query):
    q = query.lower()
    return [
        p
        for p in products
        if q in p["name"].lower() or q in p["description"].lower() or q in p["category"].lower()
    ]
