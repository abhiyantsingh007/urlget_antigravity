import os
from PIL import Image
import sys

def view_screenshots():
    """View the captured screenshots"""
    
    # Check for screenshot files
    screenshots = []
    for file in os.listdir('.'):
        if file.endswith('.png') and ('login' in file.lower() or 'dashboard' in file.lower()):
            screenshots.append(file)
    
    if not screenshots:
        print("No screenshots found!")
        return
    
    print("Available screenshots:")
    for i, screenshot in enumerate(screenshots, 1):
        print(f"{i}. {screenshot}")
    
    # Try to display each screenshot
    for screenshot in screenshots:
        try:
            print(f"\nDisplaying {screenshot}...")
            # Get image info
            img = Image.open(screenshot)
            print(f"  Size: {img.size[0]}x{img.size[1]} pixels")
            print(f"  Format: {img.format}")
            print(f"  Mode: {img.mode}")
            print(f"  File size: {os.path.getsize(screenshot)} bytes")
            
            # Try to show the image (this might not work in all environments)
            try:
                img.show()
                print(f"  Image viewer opened for {screenshot}")
            except:
                print(f"  Could not open image viewer for {screenshot}")
                print(f"  You can manually open {screenshot} with an image viewer")
                
        except Exception as e:
            print(f"Error viewing {screenshot}: {str(e)}")

if __name__ == "__main__":
    view_screenshots()