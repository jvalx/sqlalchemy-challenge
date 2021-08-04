import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    #"""List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/<start><br/>"
        f"/api/v1.0/temp/<start>/<end><br>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
     # Create our session (link) from Python to the DB
    session = Session(engine)

# Convert the query results to a dictionary using date as the key and prcp as the value.
    results = session.query(Measurement.date, Measurement.prcp).all()
    prcp_values = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["Date"] = date
        prcp_dict["Precipitation"] = prcp
        prcp_values.append(prcp_dict)
# Return the JSON representation of your dictionary.
    return jsonify(prcp_values)



@app.route("/api/v1.0/stations")
def station():
     # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of stations from the dataset."""
    # Query all station
    results = session.query(Station.station).all()
    # Unravel results into a 1D array and convert to a list
    stations = list(np.ravel(results))
    return jsonify(stations)


@app.route("/api/v1.0/tobs")
def tobs():
     # Create our session (link) from Python to the DB
    session = Session(engine)

    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    active_station = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc())

    for row in active_station:
        print(row)
    # Query the dates and temperature observations of the most active station for the last year of data.
    results1 = session.query(Measurement.tobs, Measurement.date).filter(Measurement.date >= prev_year).filter(Measurement.station == active_station[0][0]).all()

    # Return a JSON list of temperature observations (TOBS) for the previous year.
    tobs_values = []
    for tobs, date in results1:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Temperature"] = tobs
        tobs_values.append(tobs_dict)
    
    return jsonify(tobs_values)



@app.route("/api/v1.0/temp/<start_date>")
def start(start_date):  
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    start_date = dt.datetime.strptime(start_date, "%m%d%Y")
    # When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= start_date).all()

    tobs_values = []
    for min_tobs, max_tobs, avg_tobs in results:
        tobs_dict = {}
        tobs_dict["Min"] = min_tobs
        tobs_dict["Max"] = max_tobs
        tobs_dict["Avg"] = avg_tobs
        tobs_values.append(tobs_dict)
    
    return jsonify(tobs_values)
    

@app.route("/api/v1.0/temp/<start_date>/<end_date>")
def start_end(start_date, end_date):

    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    start_date = dt.datetime.strptime(start_date, "%m%d%Y")
    end_date = dt.datetime.strptime(end_date, "%m%d%Y")
    # Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
     # When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.

    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    tobs_values = []
    for min_tobs, max_tobs, avg_tobs in results:
        tobs_dict = {}
        tobs_dict["Min"] = min_tobs
        tobs_dict["Max"] = max_tobs
        tobs_dict["Avg"] = avg_tobs
        tobs_values.append(tobs_dict)
    
    return jsonify(tobs_values)


if __name__ == '__main__':
    app.run(debug=True)