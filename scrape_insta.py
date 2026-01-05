import os
import time
import requests
import sys
from playwright.sync_api import sync_playwright

def download_file(url, folder, prefix="media"):
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    # Extract filename from URL or generate one
    filename = url.split('/')[-1].split('?')[0]
    if not filename:
        filename = f"{prefix}_{int(time.time())}.jpg"
    
    filepath = os.path.join(folder, filename)
    
    print(f"Downloading {url} to {filepath}")
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            print("Download success")
            return filepath
        else:
            print(f"Failed to download: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error downloading: {e}")
        return None

def scrape_instagram(post_url, download=True):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True) # Set to False to see what's happening
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        media_urls = set()

        # Handler for network responses
        def handle_response(response):
            url = response.url
            # Check for image and video extensions or patterns
            if ".jpg" in url or ".png" in url or ".mp4" in url:
                # Filter out small icons or irrelevant assets if possible
                # Instagram media usually comes from cdninstagram.com or fbcdn.net
                if "cdninstagram.com" in url or "fbcdn.net" in url:
                     # Check if it's a significant size to be a post media? 
                     # For now, just collect them and we can filter duplicates or thumbnails later.
                     # Better yet, looking for specific patterns.
                     # Feed images usually have p1080x1080 or similar, but not always.
                     media_urls.add(url)
        
        page.on("response", handle_response)

        print(f"Navigating to {post_url}...")
        try:
            page.goto(post_url, timeout=60000)
            page.wait_for_load_state("networkidle")
            
            # Try to handle carousel using keyboard
            try:
                print("Attempting carousel navigation via keyboard...")
                # Click somewhere on the page to ensure focus
                page.mouse.click(100, 100)
                
                for _ in range(5): # Max 5 slides for demo
                    page.keyboard.press("ArrowRight")
                    time.sleep(1.5) # Wait for slide transition and load
            except Exception as e:
                print(f"Carousel navigation error: {e}")

            # Additional wait to ensure dynamic content loads
            time.sleep(5)
            
            # Also try to extract from DOM in case network interception missed (or cached)
            # Video
            videos = page.locator("video").all()
            for v in videos:
                src = v.get_attribute("src")
                if src:
                    media_urls.add(src)
                poster = v.get_attribute("poster")
                if poster:
                    media_urls.add(poster)
                    
            # Try to find all image elements in the feed container
            # The class names are obfuscated, but usually inside 'article' or role='presentation'
            images = page.locator("article img").all()
            for img in images:
                src = img.get_attribute("src")
                srcset = img.get_attribute("srcset")
                if src:
                    media_urls.add(src)
                if srcset:
                    # parse srcset to get the largest image
                    # format: url widthw, url widthw
                    parts = srcset.split(',')
                    if parts:
                        last_part = parts[-1].strip()
                        url_part = last_part.split(' ')[0]
                        media_urls.add(url_part)

        except Exception as e:
            print(f"Error during navigation: {e}")
        
        finally:
            browser.close()

        print(f"Found {len(media_urls)} potential media URLs.")
        
        # Filter URLs
        # We want to filter out profile pics (usually small) or other UI elements if possible.
        # But for now let's just download unique ones.
        
        valid_urls = []
        for url in media_urls:
            # Basic filtering
            if "s150x150" in url: continue # Thumbnail
            valid_urls.append(url)
        
        if download:
            print(f"Downloading {len(valid_urls)} valid media files...")
            downloaded_files = []
            for i, url in enumerate(valid_urls):
                 path = download_file(url, "downloads", prefix=f"insta_{i}")
                 if path:
                     downloaded_files.append(path)
            return downloaded_files
        else:
            return valid_urls

if __name__ == "__main__":
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = "https://www.instagram.com/p/DSsMcLMlK2h/?img_index=1&igsh=MTVxbXc4NWFodXByYg=="
        print(f"No URL provided, using default: {url}")
    
    scrape_instagram(url)
