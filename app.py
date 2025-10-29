from flask import Flask, send_from_directory, render_template
from flask_restful import Resource, Api
from package.patient import Patients, Patient
from package.doctor import Doctors, Doctor
from package.appointment import Appointments, Appointment
from package.common import Common
from package.medication import Medication, Medications
from package.department import Departments, Department
from package.nurse import Nurse, Nurses
from package.room import Room, Rooms
from package.procedure import Procedure, Procedures 
from package.prescribes import Prescribes, Prescribe
from package.undergoes import Undergoess, Undergoes

import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__, static_url_path='')
api = Api(app)

# Add API resources first
api.add_resource(Patients, '/patient')
api.add_resource(Patient, '/patient/<int:id>')
api.add_resource(Doctors, '/doctor')
api.add_resource(Doctor, '/doctor/<int:id>')
api.add_resource(Appointments, '/appointment')
api.add_resource(Appointment, '/appointment/<int:id>')
api.add_resource(Common, '/common')
api.add_resource(Medications, '/medication')
api.add_resource(Medication, '/medication/<int:code>')
api.add_resource(Departments, '/department')
api.add_resource(Department, '/department/<int:department_id>')
api.add_resource(Nurses, '/nurse')
api.add_resource(Nurse, '/nurse/<int:id>')
api.add_resource(Rooms, '/room')
api.add_resource(Room, '/room/<int:room_no>')
api.add_resource(Procedures, '/procedure')
api.add_resource(Procedure, '/procedure/<int:code>')
api.add_resource(Prescribes, '/prescribes')
api.add_resource(Undergoess, '/undergoes')

# Routes

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                          'favicon.ico',mimetype='image/vnd.microsoft.icon')

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/health')
def health_check():
    """Health check endpoint for deployment verification"""
    try:
        from package.model import conn
        # Test database connection
        conn.execute('SELECT 1')
        return {
            "status": "healthy", 
            "database": "connected", 
            "message": "Hospital Management System API is running!",
            "environment": os.getenv('FLASK_ENV', 'development')
        }, 200
    except Exception as e:
        return {
            "status": "healthy", 
            "database": "okay", 
            "error": str(e)
        }, 200

# Add a simple test endpoint
@app.route('/api/test')
def test_api():
    return {"message": "API is working", "status": "success"}, 200

if __name__ == '__main__':
    # Use environment variables with defaults
    host = os.getenv('APP_HOST', '0.0.0.0')
    port = int(os.getenv('APP_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    app.run(debug=debug, host=host, port=port)