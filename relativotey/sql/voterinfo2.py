# Copyright 2013, 2018 Beartronics Inc. All Rights Reserved.
#

"""
Sample App Engine application demonstrating how to connect to Google Cloud SQL
using App Engine's native unix socket or using TCP when running locally.

"""

# [START gae_python_mysql_app]
import os
import math

import MySQLdb
import webapp2
import json

import logging


# These environment variables are configured in app.yaml.
CLOUDSQL_CONNECTION_NAME = os.environ.get('CLOUDSQL_CONNECTION_NAME')
CLOUDSQL_USER = os.environ.get('CLOUDSQL_USER')
CLOUDSQL_PASSWORD = os.environ.get('CLOUDSQL_PASSWORD')

def connect_to_cloudsql():
    # When deployed to App Engine, the `SERVER_SOFTWARE` environment variable
    # will be set to 'Google App Engine/version'.
    if os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine/'):
        # Connect using the unix socket located at
        # /cloudsql/cloudsql-connection-name.
        cloudsql_unix_socket = os.path.join(
            '/cloudsql', CLOUDSQL_CONNECTION_NAME)

        db = MySQLdb.connect(
            unix_socket=cloudsql_unix_socket,
            user=CLOUDSQL_USER,
            passwd=CLOUDSQL_PASSWORD, db='voter')

    # If the unix socket is unavailable, then try to connect using TCP. This
    # will work if you're running a local MySQL server or using the Cloud SQL
    # proxy, for example:
    #
    #   $ cloud_sql_proxy -instances=your-connection-name=tcp:3306
    #
    else:
        db = MySQLdb.connect(
            host='127.0.0.1', user=CLOUDSQL_USER, passwd=CLOUDSQL_PASSWORD, db='voter')

    return db

class MainPage(webapp2.RequestHandler):
    def get(self):
        """Makes a SQL query to voter db, returns result as JSON"""
        self.response.headers['Content-Type'] = 'text/plain'

        db = connect_to_cloudsql()
        cursor = db.cursor()
        town = self.request.get('town')
        # python tuple syntax sux, that's why you need "(town,)" to make a single element tuple
        cursor.execute('SELECT sum(Registered_Voters) as vcount, count(*) as total FROM voters WHERE town=%s', (town,))

        r = cursor.fetchone()
        # you get back a "Decimal" object from sql, need to convert to int in order to serialize to JSON
        dataFound = False
        logging.info("r[0]  = ", r[0])
        logging.info("r[1]  = ", r[1])
        if (r is None) or (r[0] is None):
            vcount = 0
        else:
            vcount = int(r[0])
            dataFound = True
            
        results = { "data_found": dataFound,
                    "registered": vcount,
                    "voted": math.floor(vcount * 0.4),
                    "town": town,
                    "year": 2016 }

        logging.info("results = ",results)

        self.response.write(json.dumps(results))

app = webapp2.WSGIApplication([
    ('.*', MainPage),
], debug=True)

# [END gae_python_mysql_app]