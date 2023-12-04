# Import the dependencies.
import numpy as np
import datetime as dt
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify



#################################################
# Database Setup
#################################################
# DATA SETUP
###########################################
engine = create_engine("sqlite:///Starter_Code/Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)


# Create variables for each class
Measurement = Base.classes.measurement
Station = Base.classes.station

#create session fron python to DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    return(
        f"Welcome to the David's VACATION TEMPERATURE APP!<br/>"
        f"<br/>"
        f"<br/>"
        f"Available Routes:<br/>"
        f"<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"Precipitation data from the last 12 months.<br/>"
        f"<br/>"
        f"/api/v1.0/stations<br/>"
        f"All observatory stations listed."
        f"<br/>"
        f"<br/>"
        f"/api/v1.0/tobs<br/>"
        f"The temperature observations from the previous year.<br/>"
        f"<br/>"
        F"/api/v1.0/temp/start/end<br/>"
        f"Average, maximum and minimum temperature for the last 12 months of the station ""USC00519281"".<br/>"
        f"<br/>"
        f"Thanks for visiting the app!"
    )
# create API for precipitation using date as key and prcp as value
@app.route("/api/v1.0/precipitation")

def precipitation():
    last_date = dt.date(2017,8,23) - dt.timedelta(days = 365)
    last12 = session.query(Measurement.date,Measurement.prcp).\
    filter(func.strftime(Measurement.date) >= last_date).\
    order_by(Measurement.date).all()

    precipitation_data = {date:prcp for date, prcp in last12}
    return jsonify(precipitation_data)

# Create a list of all available observation stations
@app.route("/api/v1.0/stations")

def station():
    results = session.query(Station.station).group_by(Station.station).all()
    list_stations = list(np.ravel(results))

    # Return a JSON list of stations from the database
    return jsonify(list_stations)


# Query the dates and temps of the most active station for the previous year
@app.route("/api/v1.0/tobs")

def month_temp():
    last_year = dt.date(2017,8,18) - dt.timedelta(days=365)
    results2 = session.query(Measurement.tobs).\
        filter(Station.station == 'USC00519281').\
        filter(Measurement.date >= last_year).all()
    temperature = list(np.ravel(results2))

    # Return list of most active station dates and temps for previous list in JSON format
    return jsonify(temperature)


# Query the temperature min, max and average for specific start and end ranges of dates.
@app.route("/api/v1.0/temp/<start>/<end>")

def stats(start, end):
    start_date = dt.datetime.strptime(start, '%Y%m%d')
    end_date = dt.datetime.strptime(end, '%Y%m%d')
    temps = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    all_tobs = []
    for tobs in temps:
        tobs_dict = {}
        tobs_dict["MIN"] = tobs[0]
        tobs_dict["AVG"] = tobs[1]
        tobs_dict["MAX"] = tobs[2]
        
    all_tobs.append(tobs_dict)

#Return a JSON list of above data findings.
    return jsonify(all_tobs)


if __name__ == "__main__":
    app.run(debug=True)