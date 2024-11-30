import json
import os
from openai import OpenAI
import requests
from typing import Dict, Any

def get_device_mac(device_image_url: str, command: str, all_devices: str) -> Dict[str, Any]:
    """
    Call OpenAI API to get device MAC address from image.
    """
    client = OpenAI()
    
    # Define the response schema
    response_format = {
        "type": "json_schema",
        "json_schema": {
            "name": "device_identification",
            "description": "Device identification from image and command",
            "schema": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The name of the device"
                    },
                    "mac": {
                        "type": "string",
                        "description": "The MAC address of the device"
                    },
                    "info": {
                        "type": "string",
                        "description": "The device description/information"
                    }
                },
                "required": ["name", "mac", "info"],
                "additionalProperties": False
            },
            "strict": True
        }
    }

    # Prepare the messages
    messages = [
        {
            "role": "system",
            "content": "You're in a home environment. Your job is to identify which device user is referring to. You only response with the name and mac address and device description of the device with nothing else."
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": f"Here's a list of devices: {all_devices}\nUser sent an image of the device and said {command}"
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": device_image_url
                    }
                }
            ]
        }
    ]
    
    # Make API call
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        response_format=response_format,
        temperature=0,
        max_tokens=300
    )
    
    return json.loads(response.choices[0].message.content)


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