#!/usr/bin/env python3
from PIL import Image
import os

uploads_dir = '/home/ubuntu/.cursor/projects/workspace/uploads'
output_dir = '/workspace/assets/images'

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

images = {
    'hero': ('02-hero-bosch_e671.jpg', [(1920, 'hero.jpg'), (1440, 'hero-desktop.jpg'), (768, 'hero-tablet.jpg'), (480, 'hero-mobile.jpg')]),
    'solar': ('03-solar_d990.jpg', [(800, 'solar.jpg'), (600, 'solar-mobile.jpg')]),
    'truck-yard': ('04-truck-yard_fab3.jpg', [(800, 'truck-yard.jpg'), (600, 'truck-yard-mobile.jpg')]),
    'control-room': ('05-control-room_b84c.jpg', [(600, 'control-room.jpg'), (400, 'control-room-mobile.jpg')]),
    'store-monitoring': ('06-store-monitoring_037c.jpg', [(800, 'store-monitoring.jpg'), (600, 'store-monitoring-mobile.jpg')]),
    'baluns': ('07-baluns_396e.jpg', [(800, 'baluns.jpg'), (600, 'baluns-mobile.jpg')]),
}

for name, (source_file, sizes) in images.items():
    source_path = os.path.join(uploads_dir, source_file)
    if not os.path.exists(source_path):
        print(f"Warning: {source_path} not found")
        continue
    
    img = Image.open(source_path)
    
    # Convert RGBA to RGB if needed
    if img.mode == 'RGBA':
        img = img.convert('RGB')
    
    for width, output_name in sizes:
        # Calculate proportional height
        aspect_ratio = img.height / img.width
        height = int(width * aspect_ratio)
        
        # Resize
        resized = img.resize((width, height), Image.Resampling.LANCZOS)
        
        # Save with optimization
        output_path = os.path.join(output_dir, output_name)
        resized.save(output_path, 'JPEG', quality=85, optimize=True)
        print(f"Created {output_name} ({width}x{height})")

# Create a small Open Graph image from hero
hero_path = os.path.join(uploads_dir, '02-hero-bosch_e671.jpg')
if os.path.exists(hero_path):
    img = Image.open(hero_path)
    if img.mode == 'RGBA':
        img = img.convert('RGB')
    # 1200x630 for Open Graph
    og_img = img.resize((1200, 630), Image.Resampling.LANCZOS)
    og_img.save(os.path.join(output_dir, 'og-image.jpg'), 'JPEG', quality=85, optimize=True)
    print("Created og-image.jpg (1200x630)")

# Create favicon from logo PNG
logo_png = os.path.join(uploads_dir, '01-logo_5f7d.png')
if os.path.exists(logo_png):
    logo = Image.open(logo_png)
    # Create favicon sizes
    for size in [16, 32, 180, 192, 512]:
        favicon = logo.resize((size, size), Image.Resampling.LANCZOS)
        if size == 16 or size == 32:
            favicon.save(os.path.join(output_dir, f'favicon-{size}x{size}.png'), 'PNG', optimize=True)
        else:
            favicon.save(os.path.join(output_dir, f'icon-{size}x{size}.png'), 'PNG', optimize=True)
        print(f"Created favicon/icon {size}x{size}")

print("\nImage optimization complete!")
