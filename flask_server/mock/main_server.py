from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# SQLite database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///custom_structure.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Devices table
class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    json_data = db.Column(db.Text, nullable=False)  # Store device JSON as TEXT

# Agents table
class Agent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    json_data = db.Column(db.Text, nullable=False)  # Store agent JSON as TEXT

# Network table
class Network(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)
    value = db.Column(db.Integer, nullable=False)


# Create the tables
with app.app_context():
    db.create_all()

@app.route('/store_device', methods=['POST'])
def store_device():
    content = request.json
    json_string = str(content)  # Convert JSON to string
    new_device = Device(json_data=json_string)
    db.session.add(new_device)
    db.session.commit()
    return jsonify({'message': 'Device stored successfully!'}), 201

@app.route('/store_agent', methods=['POST'])
def store_agent():
    content = request.json
    json_string = str(content)  # Convert JSON to string
    new_agent = Agent(json_data=json_string)
    db.session.add(new_agent)
    db.session.commit()
    return jsonify({'message': 'Agent stored successfully!'}), 201

@app.route('/store_network', methods=['POST'])
def store_network():
    content = request.json
    entry_type = content.get('type')
    value = content.get('value')
    new_network_entry = Network(type=entry_type, value=value)
    db.session.add(new_network_entry)
    db.session.commit()
    return jsonify({'message': 'Network entry stored successfully!'}), 201

@app.route('/retrieve_all', methods=['GET'])
def retrieve_all():
    # Fetch all devices
    devices = Device.query.all()
    devices_list = [eval(d.json_data) for d in devices]

    # Fetch all agents
    agents = Agent.query.all()
    agents_list = [eval(a.json_data) for a in agents]

    # Fetch all network entries
    network_entries = Network.query.all()
    network_list = [{'type': n.type, 'value': n.value} for n in network_entries]

    # Combine into the desired structure
    result = {
        "devices": devices_list,
        "agents": agents_list,
        "network": network_list
    }

    return jsonify(result)

@app.route('/clear_database', methods=['POST'])
def clear_database():
    try:
        # Clear all rows from the tables
        db.session.query(Device).delete()
        db.session.query(Agent).delete()
        db.session.query(Network).delete()
        db.session.commit()

        return jsonify({'message': 'Database cleared successfully!'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)