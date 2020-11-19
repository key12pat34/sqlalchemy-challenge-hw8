#dependencies
import numpy as np
import datetime as dt
import pandas as pd
import random

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

from flask import Flask, jsonify


# #################################################
# # Database Setup
# #################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)
Base.classes.keys()

# # # Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)


# #################################################
# # Flask Setup
# #################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f'Hawaii Climate Analysis<br>'
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br>"
        f"/api/v1.0/start<br>"
        f"/api/v1.0/start/end"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    #getting the last date in the datebase
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date = last_date[0]


    # Calculating the date 1 year ago from the last data point in the database
    one_year_ago = dt.datetime.strptime(last_date, "%Y-%m-%d") - dt.timedelta(days=365)
    one_year_ago = one_year_ago.strftime("%Y-%m-%d")

    # Convert the query results to a dictionary using date as the key and prcp as the value.
    perciptation_results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).all()
   
    session.close()

    date_prcp_list=[]
    for date,prcp in perciptation_results:
        prcp_dict = {}
        prcp_dict[date] = prcp
        date_prcp_list.append(prcp_dict)
    
    # Return the JSON representation of your dictionary.
    return jsonify(date_prcp_list)


@app.route("/api/v1.0/stations")
def stations():    
    # Return a JSON list of stations from the dataset.
    station_list = session.query(Station.station).all()
    station_dict = list(np.ravel(station_list))
    session.close()
    
    return jsonify(stations = station_dict)


@app.route("/api/v1.0/tobs")
def tobs():
    # Query the dates and temperature observations of the most active station for the last year of data.
    # Return a JSON list of temperature observations (TOBS) for the previous year.

    #getting the last date in the datebase
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date = last_date[0]

    # Calculating the date 1 year ago from the last data point in the database
    one_year_ago = dt.datetime.strptime(last_date, "%Y-%m-%d") - dt.timedelta(days=365)
    one_year_ago = one_year_ago.strftime("%Y-%m-%d")

    # most active station
    active_stations = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).all()

    most_active_station = active_stations[0][0]

    temp_results = session.query(Measurement.station, Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station).\
        filter(Measurement.date >= one_year_ago).all()

    session.close()

    temp_list=[]
    for station, date, tobs in temp_results:
        temp_dict = {}
        temp_dict['station'] = station
        temp_dict['date'] = date
        temp_dict['temp'] = tobs
        temp_list.append(temp_dict)

    return jsonify(temp_list)




@app.route("/api/v1.0/<start>")
def start(start):
    # Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
    # When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
    
    # Random Start date
    start_date = session.query(Measurement.date).order_by(func.random()).first()    
    start_date = start_date[0]


    sel=[Measurement.date,
        func.min(Measurement.tobs),
        func.max(Measurement.tobs),
        func.avg(Measurement.tobs),]

    min_max_avg_qry = session.query(*sel).\
        filter(Measurement.date >= start_date).all()
    
    session.close()

    min_max_avg_list=[]
    for date, Tmin, Tmax, Tavg in min_max_avg_qry:
        min_max_avg_dict = {}
        min_max_avg_dict['date'] = date
        min_max_avg_dict['Tmin'] = Tmin
        min_max_avg_dict['Tmax'] = Tmax
        min_max_avg_dict['Tavg'] = Tavg
        min_max_avg_list.append(min_max_avg_dict)

    return jsonify(min_max_avg_list)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start,end):
    # Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
    # When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
    
    # Random Start date
    start_date = session.query(Measurement.date).order_by(func.random()).first()    
    start_date = start_date[0]

    #getting the last date in the datebase
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date = last_date[0]

    # Calculating the date 10 days before last_date
    ten_ago = dt.datetime.strptime(last_date, "%Y-%m-%d") - dt.timedelta(days=10)
    ten_ago = ten_ago.strftime("%Y-%m-%d")



    sel=[Measurement.date,
        func.min(Measurement.tobs),
        func.max(Measurement.tobs),
        func.avg(Measurement.tobs),]

    min_max_avg_qry = session.query(*sel).\
        filter(Measurement.date >= start_date).\
        filter(Measurement.date <= ten_ago).all()

    session.close()

    min_max_avg_list=[]
    for date, Tmin, Tmax, Tavg in min_max_avg_qry:
        min_max_avg_dict = {}
        min_max_avg_dict[' start date'] = date
        min_max_avg_dict['Tmin'] = Tmin
        min_max_avg_dict['Tmax'] = Tmax
        min_max_avg_dict['Tavg'] = Tavg
        min_max_avg_list.append(min_max_avg_dict)

    return jsonify(min_max_avg_list)




if __name__ == '__main__':
    app.run()