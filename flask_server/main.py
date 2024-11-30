from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import re
from PIL import Image as PILImage
from io import BytesIO
import base64

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///main_database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

ALLOWED_EXTENSIONS = {'jpeg','jpg'}

class Agent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mac_address = db.Column(db.String(17), nullable=False, unique=True)
    name = db.Column(db.String(80), nullable=False)
    info = db.Column(db.String(200), nullable=False)
    map_serial = db.Column(db.LargeBinary, nullable=True)
    map_info = db.Column(db.JSON, nullable=True)

class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mac_address = db.Column(db.String(17), nullable=False, unique=True)
    name = db.Column(db.String(80), nullable=False)
    info = db.Column(db.String(200), nullable=False)
    location = db.Column(db.JSON, nullable=True) #{"x": 2.5, "y": 5, "z": 0}

    # Relationship with Parameter
    parameters = db.relationship('Parameter', backref='device', cascade="all, delete-orphan")

    # Relationship with Image
    images = db.relationship('Image', backref='device', cascade="all, delete-orphan")

class Parameter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    param_name = db.Column(db.String(80), nullable=False)
    info = db.Column(db.String(200), nullable=False)
    data_type = db.Column(db.JSON, nullable=False)
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'), nullable=False)

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.LargeBinary, nullable=False)
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'), nullable=False)


# Create the database
with app.app_context():
    db.create_all()


##############################################################################################################################################################
##############################################################################################################################################################

@app.route('/devices', methods=['POST'])
def add_device():
    # Get data from the request
    data = request.get_json()

    # Validate input data
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # Extract fields
    mac_address = data.get('mac_address')
    name = data.get('name')
    info = data.get('info')
    location = data.get('location')

    # Check if all required fields are provided
    if not mac_address or not name or not info:
        return jsonify({'error': 'mac_address, name, and info are required fields'}), 400

    # Validate MAC address format
    mac_regex = r'^([0-9A-Fa-f]{2}:){5}([0-9A-Fa-f]{2})$'
    if not re.match(mac_regex, mac_address):
        return jsonify({'error': 'Invalid MAC address format'}), 400

    # Check for duplicate MAC address
    existing_device = Device.query.filter_by(mac_address=mac_address).first()
    if existing_device:
        return jsonify({'error': 'Device with this MAC address already exists'}), 409

    # Add new device to the database
    new_device = Device(
        mac_address=mac_address,
        name=name,
        info=info,
        location=location  # This should be a JSON object or `None`
    )
    db.session.add(new_device)
    db.session.commit()

    return jsonify({'message': 'Device added successfully', 'device': {
        'id': new_device.id,
        'mac_address': new_device.mac_address,
        'name': new_device.name,
        'info': new_device.info,
        'location': new_device.location
    }}), 201

@app.route('/agents', methods=['POST'])
def add_agent():
    # Get data from the request
    data = request.get_json()

    # Validate input data
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # Extract fields
    mac_address = data.get('mac_address')
    name = data.get('name')
    info = data.get('info')
    map_serial = data.get('map_serial')  # Optional
    map_info = data.get('map_info')      # Optional

    # Check if all required fields are provided
    if not mac_address or not name or not info:
        return jsonify({'error': 'mac_address, name, and info are required fields'}), 400

    # Validate MAC address format
    mac_regex = r'^([0-9A-Fa-f]{2}:){5}([0-9A-Fa-f]{2})$'
    if not re.match(mac_regex, mac_address):
        return jsonify({'error': 'Invalid MAC address format'}), 400

    # Check for duplicate MAC address
    existing_agent = Agent.query.filter_by(mac_address=mac_address).first()
    if existing_agent:
        return jsonify({'error': 'Agent with this MAC address already exists'}), 409

    # Add new agent to the database
    new_agent = Agent(
        mac_address=mac_address,
        name=name,
        info=info,
        map_serial=map_serial,  # Optional binary data
        map_info=map_info       # Optional JSON
    )
    try:
        db.session.add(new_agent)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Database error', 'details': str(e)}), 500

    return jsonify({'message': 'Agent added successfully', 'agent': {
        'id': new_agent.id,
        'mac_address': new_agent.mac_address,
        'name': new_agent.name,
        'info': new_agent.info,
        'map_serial': new_agent.map_serial,  # Typically binary data isn't returned
        'map_info': new_agent.map_info
    }}), 201

@app.route('/devices/<mac_address>/parameters', methods=['POST'])
def add_parameter_to_device(mac_address):
    # Validate MAC address format
    mac_regex = r'^([0-9A-Fa-f]{2}:){5}([0-9A-Fa-f]{2})$'
    if not re.match(mac_regex, mac_address):
        return jsonify({'error': 'Invalid MAC address format'}), 400

    # Check if the device exists
    device = Device.query.filter_by(mac_address=mac_address).first()
    if not device:
        return jsonify({'error': f'Device with MAC address {mac_address} not found'}), 404

    # Get data from the request
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # Extract and validate fields
    param_name = data.get('param_name')
    info = data.get('info')
    data_type = data.get('data_type')  # Assuming this is JSON

    if not param_name or not info or not data_type:
        return jsonify({'error': 'param_name, info, and data_type are required fields'}), 400

    existing_parameter = Parameter.query.filter_by(device_id=device.id, param_name=param_name).first()
    if existing_parameter:
        return jsonify({'error': f'Parameter with name "{param_name}" already exists for this device'}), 409


    try:
        # Add the parameter to the database
        new_parameter = Parameter(
            param_name=param_name,
            info=info,
            data_type=data_type,
            device_id=device.id  # Set the device_id
        )
        db.session.add(new_parameter)
        db.session.commit()

        return jsonify({
            'message': 'Parameter added successfully',
            'parameter': {
                'id': new_parameter.id,
                'param_name': new_parameter.param_name,
                'info': new_parameter.info,
                'data_type': new_parameter.data_type
            },
            'device': {
                'mac_address': device.mac_address,
                'name': device.name
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Database error', 'details': str(e)}), 500


def allowed_file(filename):
    """Check if the file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def compress_image(file):
    """Compress the image and return its binary data."""
    img = PILImage.open(file)
    img = img.convert("RGB")  # Ensure the image is in RGB mode for JPEG
    img.thumbnail((800, 800))  # Resize to fit within 800x800 pixels

    buffer = BytesIO()
    img.save(buffer, format="JPEG", quality=85)  # Compress and save as JPEG
    buffer.seek(0)  # Reset buffer pointer to the beginning
    return buffer.read()  # Return binary data

@app.route('/devices/<mac_address>/images', methods=['POST'])
def upload_compressed_image(mac_address):
    # Validate MAC address format
    mac_regex = r'^([0-9A-Fa-f]{2}:){5}([0-9A-Fa-f]{2})$'
    if not re.match(mac_regex, mac_address):
        return jsonify({'error': 'Invalid MAC address format'}), 400

    # Check if the device exists
    device = Device.query.filter_by(mac_address=mac_address).first()
    if not device:
        return jsonify({'error': f'Device with MAC address {mac_address} not found'}), 404

    # Check if a file is included in the request
    if 'image' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['image']

    # Check if the file is empty
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Check if the file has a valid extension
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Only JPEG images are allowed.'}), 400

    try:
        # Compress the image
        compressed_image_data = compress_image(file)

        # Save the compressed image to the database
        new_image = Image(
            image=compressed_image_data,
            device_id=device.id
        )
        db.session.add(new_image)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Database error', 'details': str(e)}), 500

    return jsonify({
        'message': 'Image uploaded successfully',
        'image': {
            'id': new_image.id,
            'device_id': new_image.device_id
        }
    }), 201

##############################################################################################################################################################
##############################################################################################################################################################


@app.route('/devices', methods=['GET'])
def get_all_devices():
    try:
        # Query all devices
        devices = Device.query.all()

        # Create a list of devices as dictionaries
        devices_list = [{
            'id': device.id,
            'mac_address': device.mac_address,
            'name': device.name,
            'info': device.info,
            'location': device.location  # Assuming location is a JSON
        } for device in devices]

        # Return the list as a JSON response
        return jsonify({'devices': devices_list}), 200
    except Exception as e:
        return jsonify({'error': 'Database error', 'details': str(e)}), 500


@app.route('/agents', methods=['GET'])
def get_all_agents():
    try:
        # Query all agents
        agents = Agent.query.all()

        # Create a list of agents as dictionaries
        agents_list = [{
            'id': agent.id,
            'mac_address': agent.mac_address,
            'name': agent.name,
            'info': agent.info,
            'map_serial': agent.map_serial is not None,  # Indicate if map_serial exists
            'map_info': agent.map_info  # Assuming map_info is JSON
        } for agent in agents]

        # Return the list as a JSON response
        return jsonify({'agents': agents_list}), 200
    except Exception as e:
        return jsonify({'error': 'Database error', 'details': str(e)}), 500


@app.route('/devices/<mac_address>/parameters', methods=['GET'])
def list_device_parameters(mac_address):
    # Validate MAC address format
    mac_regex = r'^([0-9A-Fa-f]{2}:){5}([0-9A-Fa-f]{2})$'
    if not re.match(mac_regex, mac_address):
        return jsonify({'error': 'Invalid MAC address format'}), 400

    # Check if the device exists
    device = Device.query.filter_by(mac_address=mac_address).first()
    if not device:
        return jsonify({'error': f'Device with MAC address {mac_address} not found'}), 404

    try:
        # Query parameters associated with the device
        parameters = Parameter.query.filter_by(device_id=device.id).all()

        # Format the parameters as a list of dictionaries
        parameters_list = [{
            'id': parameter.id,
            'param_name': parameter.param_name,
            'info': parameter.info,
            'data_type': parameter.data_type  # Assuming data_type is stored as JSON
        } for parameter in parameters]

        # Return the list of parameters
        return jsonify({
            'device': {
                'mac_address': device.mac_address,
                'name': device.name
            },
            'parameters': parameters_list
        }), 200
    except Exception as e:
        return jsonify({'error': 'Database error', 'details': str(e)}), 500

import base64

@app.route('/devices/<mac_address>/images', methods=['GET'])
def get_device_images(mac_address):
    # Validate MAC address format
    mac_regex = r'^([0-9A-Fa-f]{2}:){5}([0-9A-Fa-f]{2})$'
    if not re.match(mac_regex, mac_address):
        return jsonify({'error': 'Invalid MAC address format'}), 400

    # Check if the device exists
    device = Device.query.filter_by(mac_address=mac_address).first()
    if not device:
        return jsonify({'error': f'Device with MAC address {mac_address} not found'}), 404

    try:
        # Query images associated with the device
        images = Image.query.filter_by(device_id=device.id).all()

        # Create a list of image metadata with encoded image data
        images_list = [{
            'id': image.id,
            'device_id': image.device_id,
            'image_data': base64.b64encode(image.image).decode('utf-8')  # Encode binary to Base64
        } for image in images]

        # Return the list of images
        return jsonify({
            'device': {
                'mac_address': device.mac_address,
                'name': device.name
            },
            'images': images_list
        }), 200
    except Exception as e:
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    

##############################################################################################################################################################
##############################################################################################################################################################

@app.route('/devices/<mac_address>', methods=['DELETE'])
def delete_device(mac_address):
    # Validate MAC address format
    mac_regex = r'^([0-9A-Fa-f]{2}:){5}([0-9A-Fa-f]{2})$'
    if not re.match(mac_regex, mac_address):
        return jsonify({'error': 'Invalid MAC address format'}), 400

    # Check if the device exists
    device = Device.query.filter_by(mac_address=mac_address).first()
    if not device:
        return jsonify({'error': f'Device with MAC address {mac_address} not found'}), 404

    try:
        # Delete the device (associated parameters and images will be deleted automatically if cascade is set)
        db.session.delete(device)
        db.session.commit()

        return jsonify({'message': f'Device with MAC address {mac_address} deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Database error', 'details': str(e)}), 500


@app.route('/agents/<mac_address>', methods=['DELETE'])
def delete_agent(mac_address):
    # Validate MAC address format
    mac_regex = r'^([0-9A-Fa-f]{2}:){5}([0-9A-Fa-f]{2})$'
    if not re.match(mac_regex, mac_address):
        return jsonify({'error': 'Invalid MAC address format'}), 400

    # Check if the agent exists
    agent = Agent.query.filter_by(mac_address=mac_address).first()
    if not agent:
        return jsonify({'error': f'Agent with MAC address {mac_address} not found'}), 404

    try:
        # Delete the agent
        db.session.delete(agent)
        db.session.commit()

        return jsonify({'message': f'Agent with MAC address {mac_address} deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Database error', 'details': str(e)}), 500

@app.route('/devices/<mac_address>/images', methods=['DELETE'])
def delete_device_images(mac_address):
    # Validate MAC address format
    mac_regex = r'^([0-9A-Fa-f]{2}:){5}([0-9A-Fa-f]{2})$'
    if not re.match(mac_regex, mac_address):
        return jsonify({'error': 'Invalid MAC address format'}), 400

    # Check if the device exists
    device = Device.query.filter_by(mac_address=mac_address).first()
    if not device:
        return jsonify({'error': f'Device with MAC address {mac_address} not found'}), 404

    try:
        # Delete all images associated with the device
        Image.query.filter_by(device_id=device.id).delete()
        db.session.commit()

        return jsonify({'message': f'All images for device with MAC address {mac_address} deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Database error', 'details': str(e)}), 500

@app.route('/devices/<mac_address>/parameters/<param_name>', methods=['DELETE'])
def delete_device_parameter(mac_address, param_name):
    # Validate MAC address format
    mac_regex = r'^([0-9A-Fa-f]{2}:){5}([0-9A-Fa-f]{2})$'
    if not re.match(mac_regex, mac_address):
        return jsonify({'error': 'Invalid MAC address format'}), 400

    # Check if the device exists
    device = Device.query.filter_by(mac_address=mac_address).first()
    if not device:
        return jsonify({'error': f'Device with MAC address {mac_address} not found'}), 404

    try:
        # Check if the parameter exists for the given device
        parameter = Parameter.query.filter_by(device_id=device.id, param_name=param_name).first()
        if not parameter:
            return jsonify({'error': f'Parameter with name "{param_name}" not found for device with MAC address {mac_address}'}), 404

        # Delete the parameter
        db.session.delete(parameter)
        db.session.commit()

        return jsonify({'message': f'Parameter "{param_name}" deleted successfully for device with MAC address {mac_address}'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Database error', 'details': str(e)}), 500

@app.route('/devices/<mac_address>/parameters', methods=['DELETE'])
def delete_all_device_parameters(mac_address):
    # Validate MAC address format
    mac_regex = r'^([0-9A-Fa-f]{2}:){5}([0-9A-Fa-f]{2})$'
    if not re.match(mac_regex, mac_address):
        return jsonify({'error': 'Invalid MAC address format'}), 400

    # Check if the device exists
    device = Device.query.filter_by(mac_address=mac_address).first()
    if not device:
        return jsonify({'error': f'Device with MAC address {mac_address} not found'}), 404

    try:
        # Delete all parameters associated with the device
        Parameter.query.filter_by(device_id=device.id).delete()
        db.session.commit()

        return jsonify({'message': f'All parameters for device with MAC address {mac_address} deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Database error', 'details': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
