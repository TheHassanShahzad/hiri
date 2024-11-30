from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# SQLite database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///local_data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the database model
class Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(100), nullable=False)

# Initialize the database
with app.app_context():
    db.create_all()

# Route to store data
@app.route('/store', methods=['POST'])
def store_data():
    content = request.json
    data_value = content.get('value')
    if data_value:
        new_data = Data(value=data_value)
        db.session.add(new_data)
        db.session.commit()
        return jsonify({'message': 'Data stored successfully!'}), 201
    else:
        return jsonify({'error': 'Invalid data'}), 400

# Route to retrieve all data
@app.route('/retrieve', methods=['GET'])
def retrieve_data():
    data = Data.query.all()
    result = [{'id': d.id, 'value': d.value} for d in data]
    return jsonify({'data': result})

@app.route('/clear', methods=['POST'])
def clear_data():
    try:
        db.session.query(Data).delete()  # Deletes all rows from the `Data` table
        db.session.commit()
        return jsonify({'message': 'All data cleared successfully!'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
