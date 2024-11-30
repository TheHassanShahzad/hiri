# Language Model Callings and helpers

## main.py

This script orchestrates the entire process of converting user commands into structured device instructions.

Usage:
Set up the environment variables:
```
export OPENAI_API_KEY=<your_api_key>
```

```python
from llm.main import convert_command

result = convert_command("<user_command>", "<path_to_photo>")
print(result)
```

## upload_photo.py

This function uploads a photo to ImgBB and returns the URL of the uploaded photo.

Usage:
```
image_url = upload_photo("<path_to_photo>")
```


## image_to_mac.py

This script uses a language model to analyze an image and extract information about a device. It takes an image URL as input and returns a dictionary containing the device name and MAC address.

Usage:
```
export OPENAI_API_KEY=<your_api_key>
```


## user_command_to_structured_output.py

This function uses a language model to convert a user command into a structured output. 
The structured output follows a schema which should be defined as a list of parameters following format:
```
[   
    {
        "name": <parameter_name>,
        "type": <parameter_type>,
        "description": <parameter_description>
    },
]
```
The function will output a dictionary with the parameter names as keys and the user command as values.

e.g.
```
{
    "parameter_name1": "parameter_value1",
    "parameter_name2": "parameter_value2"
}
```



Usage:
```
export OPENAI_API_KEY=<your_api_key>
```