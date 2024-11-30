import os
from openai import OpenAI
from typing import List, Dict, Any

def create_structured_output(
    user_command: str,
    device_name: str,
    device_info: str,
    image_url: str,
    schema: List[Dict[str, str]],
) -> Dict[str, Any]:
    """
    Convert a user command into structured output based on the provided schema.
    
    Args:
        user_command: The user's command/input text
        device_name: The name of the device to analyze
        device_info: The info of the device to analyze
        image_url: url to an image file to analyze
        output_schema: List of dictionaries defining the expected parameters
            Each dict should have: {"name": str, "type": str, "description": str}
            type can be "string", "number", "boolean"
    
    Returns:
        Dictionary with parameter names as keys and extracted values
    """
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # Create the JSON schema for the response format
    for param in schema:
        assert param["data_type"] in ["string", "number", "boolean"], "Invalid parameter type"
    properties = {}
    for param in schema:
        properties[param["param_name"]] = {
            "type": param["data_type"],
            "description": param["info"]
        }
    
    response_format = {
        "type": "json_schema",
        "json_schema": {
            "name": "device_instructions",
            "description": f"Instructions for {device_name}",
            "schema": {
                "type": "object",
                "properties": properties,
                "required": [param["param_name"] for param in schema],
                "additionalProperties": False
            },
            "strict": True
        }
    }
    
    # Create the system prompt
    system_prompt = (
        "You're in a home environment.\n"
        "Your job is to understand the user's command and extract the required information "
        "according to the schema. "
        "You should only return the extracted information, nothing else."
    )

    user_prompt = [
        {
            "type": "text",
            "text": (
                f"Device name: {device_name}\n"
                f"Device info: {device_info}\n"
                f"User command: {user_command}\n"
                f"Schema: {schema}"
            )
        },
        {
            "type": "image_url",
            "image_url": {
                "url": image_url
            }
        }
    ]

    
    
    # Prepare the API call
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]


    
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # Changed to vision model to handle images
        messages=messages,
        response_format=response_format,
        temperature=0.1,
        max_tokens=4096  # Added max_tokens for vision model
    )
    
    return response.choices[0].message.content

# Example usage
if __name__ == "__main__":
    # Example schema
    schema = [
        {
            "param_name": "temperature",
            "data_type": "number",
            "info": "The temperature of the microwave"
        },
        {
            "param_name": "time",
            "data_type": "number",
            "info": "The time to cook the food in seconds"
        }
    ]
    
    # Example command with image
    command = "heat my food to 110 degrees for 3 minutes"
    image_url = "https://store.panasonic.co.uk/media/.renditions/catalog/category/SKA/NN-DF38PBBPQ_2-HIGH_RES_1.jpg"
    
    result = create_structured_output(command, "microwave", image_url, schema)
    print(result)
