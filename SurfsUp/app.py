# Import the dependencies.
import datetime as dt
import numpy as np

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################

# reflect an existing database into a new model
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect the tables
Base = automap_base()
Base.prepare(engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
# Pass the app name
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
# Setup route for index page 
@app.route("/")
def welcome():
    return(
        f"Welcome to the Hawaii Climate Analysis API<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start<br/>"
        f"/api/v1.0/temp/start/end<br/>"
        f"<p>'start' and 'end' date should be in the format MMDDYYYY.</p>"
    )

# Setup route for Precipitation data 
@app.route("/api/v1.0/precipitation")
def precipitation():
    max_date = session.query(func.max(Measurement.date)).scalar()
    prev_year = session.query(func.date(max_date,'-12 months')).scalar()

# Query for filtering last year of data
    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= prev_year).all()
# Close session and show results
    session.close()
    precip = { date: prcp for date, prcp in precipitation}

    return jsonify(precip)

# Setup route for listing stations
@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.station).all()

# Close session and show results
    session.close()
    stations = list(np.ravel(results))

    return jsonify(stations=stations)

# Setup route for temperature at Station USC00519281 for last year
@app.route("/api/v1.0/tobs")
def temp_monthly():
    max_date = session.query(func.max(Measurement.date)).scalar()
    prev_year = session.query(func.date(max_date,'-12 months')).scalar()

    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= prev_year).all()

# Close session and show results
    session.close()
    temps = list(np.ravel(results))

    return jsonify(temps=temps)

# Setup route for allowing user to add date filter
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
# Setup func for Min, Max, Average
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
# Query using filter input from user
    if not end:
        start = dt.datetime.strptime(start,"%m%d%Y")
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()
# Close session and show results
        session.close()
        temps = list(np.ravel(results))

        return jsonify(temps)
# Setup for query with start and end date inputs from user
    start = dt.datetime.strptime(start, "%m%d%Y")
    end = dt.datetime.strptime(end, "%m%d%Y")

    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
# Close session and show results
    session.close()
    temps = list(np.ravel(results))

    return jsonify(temps=temps)
# Turn debug on when name is main
if __name__ == "__main__":
    app.run(debug=True)
    