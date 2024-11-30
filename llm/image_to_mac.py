import os
import requests
import json

def get_device_mac(device_image_url: str, command: str, all_devices: str) -> dict:
    """
    Call the Wordware API to get device MAC address from image.
    
    Args:
        device_image_url (str): URL of the device image
        command (str): Command parameter
        all_devices (str): All devices parameter
    
    Returns:
        dict: API response
        
    Raises:
        requests.exceptions.RequestException: If the API call fails
    """
    
    # API endpoint
    url = "https://app.wordware.ai/api/released-app/45a76eaf-b47f-4ada-9438-ec20dc74fd46/run"
    
    # Get API key from environment variable
    api_key = os.getenv("WORDWARE_API_KEY")
    if not api_key:
        raise ValueError("WORDWARE_API_KEY environment variable not set")
    
    # Prepare headers
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    
    # Prepare request body
    payload = {
        "inputs": {
            "device_image": {
                "type": "image",
                "image_url": device_image_url
            },
            "command": command,
            "all_devices": all_devices
        },
        "version": "^1.2"
    }
    
    # Make API call
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()

    # Parse the streaming response
    lines = response.text.split('\n')
    for line in lines:
        if not line:
            continue
        try:
            chunk = json.loads(line)
            # print(chunk)
            # Look for the structured generation result
            if (chunk.get('type') == 'chunk' and 
                chunk.get('value', {}).get('type') == 'outputs'):
                # Extract the result
                result = chunk['value'].get('values').get("new_structured_generation")
                return result
        except json.JSONDecodeError:
            continue
    
    raise ValueError("Could not find device information in response")


if __name__ == "__main__":
    image_url = "https://store.panasonic.co.uk/media/.renditions/catalog/category/SKA/NN-DF38PBBPQ_2-HIGH_RES_1.jpg"
    response = get_device_mac(image_url, "heat it up", """
    "devices": [
        {
            "id": 1,
            "info": "55-inch Smart TV with HDMI connectivity",
            "location": {
                "x": 3.5,
                "y": 0.8,
                "z": 1.2
            },
            "mac_address": "AA:BB:CC:11:22:33",
            "name": "Living Room TV"
        },
        {
            "id": 2,
            "info": "1000W countertop microwave with smart features",
            "location": {
                "x": 1.2,
                "y": 1.5,
                "z": 0.9
            },
            "mac_address": "AA:BB:CC:44:55:66",
            "name": "Kitchen Microwave"
        },
        {
            "id": 3,
            "info": "Dimmable RGB smart lamp with voice control",
            "location": {
                "x": 2.8,
                "y": 0.6,
                "z": 1.1
            },
            "mac_address": "AA:BB:CC:77:88:99",
            "name": "Bedroom Lamp"
        },
        {
            "id": 4,
            "info": "Electric smart stove with 4 burners and temperature monitoring",
            "location": {
                "x": 1.0,
                "y": 0.9,
                "z": 0.0
            },
            "mac_address": "AA:BB:CC:AA:BB:CC",
            "name": "Kitchen Stove"
        }
    ]
}
""")
    print(response)