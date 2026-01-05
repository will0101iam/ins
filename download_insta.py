import os
from instagrapi import Client
from urllib.parse import urlparse

def download_instagram_media(post_url):
    cl = Client()
    
    # Try to configure client to be more stealthy
    # cl.set_user_agent("Instagram 200.0.0.31.120 Android (29/10; 420dpi; 1080x2028; samsung; SM-G960F; starlte; samsungexynos9810; en_US; 314665256)")

    try:
        print(f"Analyzing URL: {post_url}")
        # Extract media PK
        media_pk = cl.media_pk_from_url(post_url)
        print(f"Media PK: {media_pk}")
        
        # Get media info
        media_info = cl.media_info(media_pk)
        
        output_dir = "downloads"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        print(f"Media Type: {media_info.media_type}")
        
        downloaded_files = []

        if media_info.media_type == 1: # Photo
            print("Found Photo")
            path = cl.photo_download(media_pk, folder=output_dir)
            downloaded_files.append(str(path))
            
        elif media_info.media_type == 2 and media_info.product_type == 'feed': # Video
            print("Found Video")
            path = cl.video_download(media_pk, folder=output_dir)
            downloaded_files.append(str(path))
            
        elif media_info.media_type == 8: # Album
            print("Found Album")
            # For albums, we need to iterate resources
            # instagrapi has album_download helper
            paths = cl.album_download(media_pk, folder=output_dir)
            downloaded_files.extend([str(p) for p in paths])
            
        elif media_info.media_type == 2 and media_info.product_type == 'clips': # Reels
             print("Found Reel")
             path = cl.video_download(media_pk, folder=output_dir)
             downloaded_files.append(str(path))

        print("\nDownload complete!")
        for f in downloaded_files:
            print(f"Saved to: {f}")

    except Exception as e:
        print(f"Error: {e}")
        # If login is required, we might see a specific error here
        if "login_required" in str(e).lower():
             print("This post requires login to view.")

if __name__ == "__main__":
    url = "https://www.instagram.com/p/DSsMcLMlK2h/?img_index=1&igsh=MTVxbXc4NWFodXByYg=="
    download_instagram_media(url)
