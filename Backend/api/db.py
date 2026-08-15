import pymysql
from flask import current_app
import os
import tempfile


# In every file that is going to change the database these lines are needed

# Import
# from . import db

# Establish connection
# conn = db.get_db()

# # Create cursor
# cursor = conn.cursor()

# Make changes to db.....

# Save actions to db
# conn.commit()

# #Close the cursor and conn
# cursor.close()
# conn.close()

def _ssl_options():
    ca_path = current_app.config.get('MYSQL_SSL_CA')
    ca_content = current_app.config.get('MYSQL_SSL_CA_CONTENT')

    if ca_content:
        ca_path = os.path.join(tempfile.gettempdir(), 'aiven-ca.pem')
        if not os.path.exists(ca_path):
            with open(ca_path, 'w', encoding='utf-8') as ca_file:
                ca_file.write(ca_content.replace('\\n', '\n'))

    return {'ca': ca_path} if ca_path else None


def get_db():

    try:
        connect_kwargs = dict(
            host = current_app.config['MYSQL_HOST'],
            port = current_app.config.get('MYSQL_PORT', 3306),
            user = current_app.config['MYSQL_USER'],
            password = current_app.config['MYSQL_PASSWORD'],
            db = current_app.config['MYSQL_DB'],
            cursorclass=pymysql.cursors.DictCursor
        )

        ssl = _ssl_options()
        if ssl:
            connect_kwargs['ssl'] = ssl

        connection = pymysql.connect(**connect_kwargs)
        return connection
    except Exception as e:
        print("Error connecting to DB:", e)
        raise
