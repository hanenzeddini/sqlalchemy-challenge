# Import necessary libraries and modules.
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

# Database Setup: Establish connection with the SQLite database.
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect the existing database into a new model.
Base = automap_base()
# Reflect the tables in the database.
Base.prepare(autoload_with=engine)

# Save references to each table for easier access.
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create a session (link) from Python to the database.
session = Session(engine)

# Flask Setup: Initialize the Flask app.
app = Flask(__name__)

# Define the routes for the Flask app.
@app.route("/")
def home():
    """Home route: Lists all available API routes."""
    return (
        f"/api/v1.0/precipitation:<br/>"
        f"/api/v1.0/stations:<br/>"
        f"/api/v1.0/tobs:<br/>"
        f"/api/v1.0/<start>:<br/>"
        f"/api/v1.0/<start>/<end>:<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """API route for precipitation data."""
    # Query for the latest date and calculate the date one year ago.
    start = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    start = dt.datetime.strptime(start, '%Y-%m-%d')
    last = start - dt.timedelta(days=365.25)

    # Retrieve data and precipitation scores for the last year.
    data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= last).filter(Measurement.prcp != None).all()
    
    # Convert query results to a list of dictionaries.
    data_dic = [{"date": val[0], "prcp": val[1]} for val in data]

    session.close()
    return jsonify(data_dic)

@app.route("/api/v1.0/stations")
def stations():
    """API route for station data."""
    # Query for station data and their activity count.
    station_activity = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).all()
    data_dic = [{"station": val[0], "count": val[1]} for val in station_activity]

    session.close()
    return jsonify(data_dic)

@app.route("/api/v1.0/tobs")
def tobs():
    """API route for temperature observations (tobs)."""
    # Query for the most active station's temperature observations in the last year.
    station_activity = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).all()

    start = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    start = dt.datetime.strptime(start, '%Y-%m-%d')
    last = start - dt.timedelta(days=365.25)

    data_temp = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= last).filter(Measurement.station == station_activity[0][0]).all()

    data_dic = [{"date": val[0], "temp": val[1]} for val in data_temp]

    session.close()
    return jsonify(data_dic)

@app.route("/api/v1.0/<start>")
def start_temp(start):
    """API route for temperature statistics from a given start date."""
    # Query for min, max, and avg temperatures from the start date.
    data_temp = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
    filter(Measurement.date >= start).all()[0]

    data_dic = {"TMIN": data_temp[0], "TAVG": data_temp[2], "TMAX": data_temp[1]}

    session.close()
    return jsonify(data_dic)

@app.route("/api/v1.0/<start>/<end>")
def start_end_temp(start,end):
   """API route for temperature statistics between a start and end date."""
   # Query for min, max, and avg temperatures in the date range.
   data_temp = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
    filter(Measurement.date >= start).filter(Measurement.date <= end).all() [0] 
   
   data_dic = {"TMIN": data_temp[0],"TAVG": data_temp[2],"TMAX": data_temp[1]}
   
   session.close()
   return jsonify(data_dic)



if __name__ == '__main__':
    app.run(debug=True)