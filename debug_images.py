#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campus_lostfound.settings')
django.setup()

from items.models import Item

print("=== IMAGE DEBUG INFO ===")
print(f"MEDIA_URL: {django.conf.settings.MEDIA_URL}")
print(f"MEDIA_ROOT: {django.conf.settings.MEDIA_ROOT}")

items_with_images = Item.objects.filter(image__isnull=False).exclude(image='')
print(f"\nItems with images: {items_with_images.count()}")

for item in items_with_images[:5]:  # Show first 5
    print(f"\nItem ID: {item.id}")
    print(f"Image field: {item.image}")
    print(f"Image name: {item.image.name}")
    print(f"Image URL: {item.image.url}")
    print(f"Image path: {item.image.path}")
    print(f"File exists: {os.path.exists(item.image.path)}")