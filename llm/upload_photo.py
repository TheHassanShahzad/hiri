import requests
import base64
import os

def upload_photo_to_imgbb(photo_path):

    """
    Upload a photo to ImgBB and return the URL
    
    Args:
        photo_path (str): Path to the photo file (relative to project root)
        api_key (str): Your ImgBB API key
    
    Returns:
        str: URL of the uploaded image, or None if upload fails
    """
    api_key = "af1e0a74a40bf3c5a4126ecdd8b91600"
    # Get the absolute path from project root
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    absolute_path = os.path.join(base_dir, photo_path)
    
    # API endpoint
    url = f"https://api.imgbb.com/1/upload"
    
    try:
        # Read and encode the image using absolute path
        with open(absolute_path, "rb") as file:
            image_data = base64.b64encode(file.read())
        
        # Prepare the payload
        payload = {
            'key': api_key,
            'image': image_data,
            'expiration': 600  # 10 minutes expiration
        }
        
        # Make the POST request
        response = requests.post(url, data=payload)
        
        # Check if request was successful
        if response.status_code == 200:
            json_data = response.json()
            if json_data.get('success'):
                return json_data['data']['url']
        
        return None
        
    except Exception as e:
        print(f"Error uploading image: {str(e)}")
        return None

# Example usage:
if __name__ == "__main__":
    api_key = "af1e0a74a40bf3c5a4126ecdd8b91600"
    image_url = upload_photo_to_imgbb("/Users/yinbaicheng/Downloads/hiri/llm/shopping.webp", api_key)
    if image_url:
        print(f"Uploaded image URL: {image_url}")
    else:
        print("Upload failed")
