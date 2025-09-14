import os
import requests
from urllib.parse import urlparse, unquote
from pathlib import Path
import datetime

def download_image():
    """
    Downloads an image from a URL and saves it to Fetched_Images directory
    """
    print("=== Image Fetcher ===")
    print("Connect with the web community by fetching and organizing images")
    print("-" * 50)
    
    try:
        # Prompt user for URL
        url = input("Please enter the image URL: ").strip()
        
        if not url:
            print("❌ No URL provided. Please try again.")
            return
        
        # Validate URL format
        if not url.startswith(('http://', 'https://')):
            print("❌ Invalid URL format. Please include http:// or https://")
            return
        
        # Create directory if it doesn't exist
        os.makedirs("Fetched_Images", exist_ok=True)
        print("✓ Fetched_Images directory ready")
        
        # Fetch the image
        print(f"🌐 Connecting to {urlparse(url).netloc}...")
        response = requests.get(url, timeout=10)
        
        # Check for HTTP errors
        response.raise_for_status()
        
        # Check if content is actually an image
        content_type = response.headers.get('content-type', '')
        if not content_type.startswith('image/'):
            print("❌ The URL does not point to an image file")
            return
        
        # Extract or generate filename
        filename = extract_filename(url, content_type)
        filepath = os.path.join("Fetched_Images", filename)
        
        # Check if file already exists
        counter = 1
        base_name, extension = os.path.splitext(filename)
        while os.path.exists(filepath):
            filename = f"{base_name}_{counter}{extension}"
            filepath = os.path.join("Fetched_Images", filename)
            counter += 1
        
        # Save the image
        with open(filepath, 'wb') as file:
            file.write(response.content)
        
        print(f"✅ Successfully downloaded: {filename}")
        print(f"📁 Saved to: {os.path.abspath(filepath)}")
        print(f"📊 File size: {len(response.content):,} bytes")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP error: {e}")
    except requests.exceptions.Timeout:
        print("❌ Connection timed out. Please try again.")
    except requests.exceptions.TooManyRedirects:
        print("❌ Too many redirects. The URL might be broken.")
    except PermissionError:
        print("❌ Permission denied. Cannot write to directory.")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")

def extract_filename(url, content_type):
    """
    Extract filename from URL or generate one based on content type
    """
    # Try to get filename from URL path
    parsed_url = urlparse(url)
    path = unquote(parsed_url.path)
    
    if path and '/' in path:
        # Extract the last part of the path
        potential_filename = path.split('/')[-1]
        if potential_filename and '.' in potential_filename:
            return potential_filename
    
    # If no filename in URL, generate one based on content type
    extension = content_type.split('/')[-1]
    if extension == 'jpeg':
        extension = 'jpg'
    
    # Generate timestamp-based filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"image_{timestamp}.{extension}"

def main():
    """
    Main function to run the image downloader
    """
    try:
        download_image()
    except KeyboardInterrupt:
        print("\n\n👋 Operation cancelled by user. Stay connected!")
    finally:
        print("\n" + "=" * 50)
        print("Thank you for using Image Fetcher!")
        print("Share your organized images with the community!")
        print("=" * 50)

if __name__ == "__main__":
    main()