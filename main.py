import random

def generate_backup_content_ideas():
    ideas = [
        "Top 5 things people don't know about history",
        "Mistakes new digital creators make",
        "How to start selling digital products with zero money",
        "Hidden facts about popular culture",
        "How AI is changing online business",
        "Secrets behind viral short videos",
        "Daily habits of successful creators",
        "How to grow small audience into buyers",
        "Content ideas nobody is using yet",
        "How to turn knowledge into digital products"
    ]
    return random.sample(ideas, 5)

def generate_backup_products():
    products = [
        "Content Idea Ebook",
        "Caption Template Pack",
        "Beginner Digital Product Guide",
        "Viral Content Checklist",
        "AI Prompt Pack for Creators",
        "Social Media Growth Guide",
        "Digital Product Starter Kit",
        "Creator Money Tracker Template"
    ]
    return random.sample(products, 3)


print("Welcome to AI Creator Business Assistant")

name = input("Enter your name: ")
content_type = input("What content do you create? ")
problem = input("What is your biggest struggle right now? ")

print("\n--- AI Assistant Response ---")
print("Hello", name)

print("\n🔥 5 Content Ideas For You:")
for idea in generate_backup_content_ideas():
    print("-", idea)

print("\n💰 3 Digital Products You Can Sell:")
for product in generate_backup_products():
    print("-", product)

print("\nFocus on consistency and understanding your audience.")
