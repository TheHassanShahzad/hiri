from user_command_to_structured_output import create_structured_output
from upload_photo import upload_photo_to_imgbb
from image_to_mac import get_device_mac
from typing import Dict, Any
import requests

def convert_command(
    user_command: str,
    user_image_path: str,
    devices_server_ip: str = "127.0.0.1:5000",
) -> Dict[str, Any]:
    # step 1: upload photo to imgbb
    # step 2: get device mac address
    # step 3: get device schema using mac address
    # step 4: convert user command to structured output
    # step 5: return structured output

    # step 1
    image_url = upload_photo_to_imgbb(user_image_path)

    # step 2
    device_list = str(requests.get(f"http://{devices_server_ip}/devices").json())
    response = get_device_mac(image_url, user_command, device_list)
    device_name = response.get("name")
    device_mac = response.get("mac")
    device_info = response.get("info")

    # step 3
    device_schema = requests.get(f"http://{devices_server_ip}/devices/{device_mac}/parameters").json()
    # print(device_schema.get("parameters"))

    # step 4
    structured_output = create_structured_output(user_command, device_name, device_info, image_url, device_schema.get("parameters"))
    # print(structured_output)

    return {
        "mac_address": device_mac,
        "parameters": structured_output
    }

if __name__ == "__main__":
    print(convert_command("heat my food to 110 degrees for 3 minutes", "/Users/yinbaicheng/Downloads/hiri/llm/microwave.jpeg")) 