
# Flask Application Documentation

This documentation describes the Flask application for managing `Device`, `Agent`, and associated `Parameter` and `Image` data in a database. The application provides a RESTful API for interacting with the database.

---

## **Dependencies**

- Flask
- Flask-SQLAlchemy
- re (regular expressions)
- PIL (Python Imaging Library)
- io (for BytesIO)
- base64

### **Database Models**

1. **Agent**
   - `id` (Integer, Primary Key)
   - `mac_address` (String, Unique, Required)
   - `name` (String, Required)
   - `info` (String, Required)
   - `map_serial` (Binary, Optional)
   - `map_info` (JSON, Optional)

2. **Device**
   - `id` (Integer, Primary Key)
   - `mac_address` (String, Unique, Required)
   - `name` (String, Required)
   - `info` (String, Required)
   - `location` (JSON, Optional)
   - Relationships:
     - `parameters` (One-to-Many with `Parameter`)
     - `images` (One-to-Many with `Image`)

3. **Parameter**
   - `id` (Integer, Primary Key)
   - `param_name` (String, Required)
   - `info` (String, Required)
   - `data_type` (JSON, Required)
   - `device_id` (Foreign Key to `Device.id`, Required)

4. **Image**
   - `id` (Integer, Primary Key)
   - `image` (Binary, Required)
   - `device_id` (Foreign Key to `Device.id`, Required)

---

### **API Endpoints**

#### **Device Endpoints**

- **GET `/devices`**  
  Retrieve all devices.

- **POST `/devices`**  
  Add a new device.  
  **Request Body:**
  ```json
  {
      "mac_address": "AA:BB:CC:DD:EE:FF",
      "name": "Device Name",
      "info": "Device Information",
      "location": {"x": 0, "y": 0, "z": 0}
  }
  ```

- **DELETE `/devices/<mac_address>`**  
  Delete a specific device by MAC address.

---

#### **Agent Endpoints**

- **GET `/agents`**  
  Retrieve all agents.

- **POST `/agents`**  
  Add a new agent.  
  **Request Body:**
  ```json
  {
      "mac_address": "AA:BB:CC:DD:EE:FF",
      "name": "Agent Name",
      "info": "Agent Information",
      "map_serial": "<binary data>",
      "map_info": {"key": "value"}
  }
  ```

- **DELETE `/agents/<mac_address>`**  
  Delete a specific agent by MAC address.

---

#### **Parameter Endpoints**

- **GET `/devices/<mac_address>/parameters`**  
  Retrieve all parameters for a specific device.

- **POST `/devices/<mac_address>/parameters`**  
  Add a parameter to a device.  
  **Request Body:**
  ```json
  {
      "param_name": "Parameter Name",
      "info": "Parameter Information",
      "data_type": {"type": "string"}
  }
  ```

- **DELETE `/devices/<mac_address>/parameters/<param_name>`**  
  Delete a specific parameter from a device.

- **DELETE `/devices/<mac_address>/parameters`**  
  Delete all parameters from a device.

---

#### **Image Endpoints**

- **GET `/devices/<mac_address>/images`**  
  Retrieve all images for a specific device.

- **POST `/devices/<mac_address>/images`**  
  Upload a compressed image for a device.  
  **Request Body:**  
  Form-Data containing an image file (JPEG only).

- **DELETE `/devices/<mac_address>/images`**  
  Delete all images associated with a device.

---

### **Utilities**

- `allowed_file(filename)`  
  Validate if a file has an allowed extension.

- `compress_image(file)`  
  Compress an image to fit within 800x800 pixels and save it as JPEG.

---

### **Validation Rules**

- **MAC Address:**  
  Must follow the format `XX:XX:XX:XX:XX:XX` where `X` is a hexadecimal character.

- **File Types:**  
  Only JPEG images are allowed for upload.

---

### **Error Responses**

- `400 Bad Request`  
  Invalid or missing data in the request.

- `404 Not Found`  
  Requested resource does not exist.

- `409 Conflict`  
  Resource with a unique constraint (e.g., MAC address) already exists.

- `500 Internal Server Error`  
  Database or server error.

---

### **Run the Application**

Start the Flask server with:
```bash
python app.py
```