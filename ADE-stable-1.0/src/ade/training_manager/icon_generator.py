from PIL import Image, ImageDraw
import os

def generate_icon():
    # Create a new image with a white background
    size = (256, 256)
    image = Image.new('RGBA', size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    
    # Draw a rounded rectangle for the base
    draw.rounded_rectangle([(20, 20), (236, 236)], radius=30, fill=(65, 105, 225))
    
    # Draw "ADE" text-like shapes
    # Letter A
    draw.polygon([(78, 180), (108, 80), (138, 180)], fill=(255, 255, 255))
    draw.polygon([(93, 140), (123, 140)], fill=(65, 105, 225))
    
    # Letter D
    draw.rectangle([(148, 80), (158, 180)], fill=(255, 255, 255))
    draw.ellipse([(148, 80), (188, 180)], fill=(255, 255, 255))
    
    # Letter E
    draw.rectangle([(198, 80), (208, 180)], fill=(255, 255, 255))
    draw.rectangle([(198, 80), (228, 90)], fill=(255, 255, 255))
    draw.rectangle([(198, 125), (218, 135)], fill=(255, 255, 255))
    draw.rectangle([(198, 170), (228, 180)], fill=(255, 255, 255))
    
    # Ensure the assets directory exists
    os.makedirs('assets', exist_ok=True)
    
    # Save as ICO file
    image.save('assets/icon.ico', format='ICO', sizes=[(256, 256)])

if __name__ == "__main__":
    generate_icon() 