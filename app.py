# Import the dependencies.

import datetime as dt
import datetime
import numpy as np
import pandas as pd

from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station


# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
# define homepage route
@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )

# define precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the precipitation data for the last 12 months."""
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Calculate the date one year from the last date in data set
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    one_year_ago = dt.datetime.strptime(recent_date, "%Y-%m-%d") - dt.timedelta(days=365)
    
    # Query for the last 12 months of precipitation data
    results = session.query(Measurement.date, Measurement.prcp).\
                filter(Measurement.date >= one_year_ago).\
                order_by(Measurement.date).all()
    
    # Create dictionary from the query results
    precipitation_dict = {}
    for date, prcp in results:
        precipitation_dict[date] = prcp
    
    # Return the JSON representation of the dictionary
    return jsonify(precipitation_dict)

    session.close()


    # define stations route
@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations from the dataset."""
    # Create our session (link) from Python to the DB
    session = Session(engine)
      
    # Query for the stations
    results = session.query(Station.station).all()
    
    # Convert the query results to a list
    station_list = list(np.ravel(results))
    
    # Return the JSON representation of the list
    return jsonify(station_list)
    
    session.close()
    
    
# define tobs route
@app.route("/api/v1.0/tobs")
def tobs():
    """Return the temperature observations for the previous year at the most active station."""
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Calculate the date one year from the last date in data set
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    one_year_ago = dt.datetime.strptime(recent_date, "%Y-%m-%d") - dt.timedelta(days=365)
    
    # Query for the most active station
    station_query = session.query(Measurement.station, func.count(Measurement.station)).\
                    group_by(Measurement.station).\
                    order_by(func.count(Measurement.station).desc()).first()
    most_active_station = station_query[0]
    
    # Query for the temperature observations
    results = session.query(Measurement.date, Measurement.tobs).\
                filter(Measurement.date >= one_year_ago).\
                filter(Measurement.station == most_active_station).\
                all()
    
    session.close()
    
    # Convert the results to a list of dictionaries
    tobs_data = []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict['date'] = date
        tobs_dict['tobs'] = tobs
        tobs_data.append(tobs_dict)
    
    # Return the JSON representation of the tobs data
    return jsonify(tobs_data)
    
@app.route("/api/v1.0/<start>")
def temp_stats_start(start):
    """Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start date"""
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Perform a query to retrieve the temperature stats for dates greater than or equal to the start date
    temp_stats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()

    # Convert the query results to a dictionary
    temp_stats_dict = {"TMIN": temp_stats[0][0], "TAVG": temp_stats[0][1], "TMAX": temp_stats[0][2]}

    # Return the JSON representation of the dictionary
    return jsonify(temp_stats_dict)
    
    session.close()
    
    
@app.route("/api/v1.0/<start>/<end>")
def temp_stats_start_end(start, end):
    """Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start-end date range"""
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Perform a query to retrieve the temperature stats for dates between the start and end date, inclusive
    temp_stats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    # Convert the query results to a dictionary
    temp_stats_dict = {"TMIN": temp_stats[0][0], "TAVG": temp_stats[0][1], "TMAX": temp_stats[0][2]}

    # Return the JSON representation of the dictionary
    return jsonify(temp_stats_dict)

    session.close()
    
# 4. Define main behavior
if __name__ == "__main__":
    app.run(debug=True)