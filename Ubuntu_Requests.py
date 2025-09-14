import requests
import os
import hashlib
from urllib.parse import urlparse
import mimetypes

def get_filename_from_url(url, content_type=None):
    """Extract filename from URL or generate one based on content type"""
    parsed_url = urlparse(url)
    filename = os.path.basename(parsed_url.path)
    
    if not filename or '.' not in filename:
        # Generate filename based on content type or default to .jpg
        extension = ".jpg"
        if content_type:
            extension = mimetypes.guess_extension(content_type) or ".jpg"
        filename = f"downloaded_image{extension}"
    
    return filename

def calculate_file_hash(content):
    """Calculate MD5 hash of file content for duplicate detection"""
    return hashlib.md5(content).hexdigest()

def is_duplicate_image(directory, content):
    """Check if image with same content already exists"""
    content_hash = calculate_file_hash(content)
    
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath):
            with open(filepath, 'rb') as f:
                existing_hash = calculate_file_hash(f.read())
                if existing_hash == content_hash:
                    return True, filename
    
    return False, None

def download_image(url, directory="Fetched_Images"):
    """Download a single image from URL"""
    try:
        # Set headers to mimic a browser request
        headers = {
            'User-Agent': 'UbuntuImageFetcher/1.0 (https://example.com/image-fetcher)'
        }
        
        # Fetch the image with timeout and headers
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()  # Raise exception for bad status codes
        
        # Check content type to ensure it's an image
        content_type = response.headers.get('Content-Type', '')
        if not content_type.startswith('image/'):
            return False, f"URL does not point to an image (Content-Type: {content_type})"
        
        # Check content length to avoid excessively large files
        content_length = response.headers.get('Content-Length')
        if content_length and int(content_length) > 10 * 1024 * 1024:  # 10MB limit
            return False, f"File too large ({int(content_length)/1024/1024:.2f} MB)"
        
        # Extract filename from URL or generate one
        filename = get_filename_from_url(url, content_type)
        filepath = os.path.join(directory, filename)
        
        # Check for duplicates
        is_duplicate, existing_filename = is_duplicate_image(directory, response.content)
        if is_duplicate:
            return False, f"Duplicate image already exists as {existing_filename}"
        
        # Save the image
        with open(filepath, 'wb') as f:
            f.write(response.content)
            
        return True, f"Successfully fetched: {filename}"
        
    except requests.exceptions.RequestException as e:
        return False, f"Connection error: {e}"
    except Exception as e:
        return False, f"An error occurred: {e}"

def main():
    print("Welcome to the Ubuntu Image Fetcher")
    print("A tool for mindfully collecting images from the web\n")
    
    # Create directory if it doesn't exist
    os.makedirs("Fetched_Images", exist_ok=True)
    
    # Get URLs from user
    urls_input = input("Please enter image URL(s), separated by commas: ")
    urls = [url.strip() for url in urls_input.split(',') if url.strip()]
    
    if not urls:
        print("No URLs provided.")
        return
    
    successful_downloads = 0
    
    for url in urls:
        print(f"\nProcessing: {url}")
        success, message = download_image(url)
        
        if success:
            print(f"✓ {message}")
            successful_downloads += 1
        else:
            print(f"✗ {message}")
    
    print(f"\nDownloaded {successful_downloads} of {len(urls)} images.")
    
    if successful_downloads > 0:
        print("Connection strengthened. Community enriched.")

if __name__ == "__main__":
    main()
