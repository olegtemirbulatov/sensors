# Import the dependencies.
import configparser
from datetime import datetime
from uuid import uuid4
from pathlib import Path
import os

# Import client library classes.
from influxdb_client import Authorization, InfluxDBClient, Permission, PermissionResource, Point, WriteOptions
from influxdb_client.client.authorizations_api import AuthorizationsApi
from influxdb_client.client.bucket_api import BucketsApi
from influxdb_client.client.query_api import QueryApi
from influxdb_client.client.write_api import SYNCHRONOUS

from sensor import Sensor

# Get the configuration key-value pairs.
path = Path(__file__)
ROOT_DIR = path.parent.absolute()
config_path = os.path.join(ROOT_DIR, "config.ini")

config = configparser.ConfigParser()
config.read(config_path)

def create_authorization(device_id) -> Authorization:
    influxdb_client = InfluxDBClient(url=config.get('APP', 'INFLUX_URL'),
                                     token=config.get('APP', 'INFLUX_TOKEN'),
                                     org=config.get('APP', 'INFLUX_ORG'))

    authorization_api = AuthorizationsApi(influxdb_client)
    # get bucket_id from bucket
    buckets_api = BucketsApi(influxdb_client)
    buckets = buckets_api.find_bucket_by_name(config.get('APP', 'INFLUX_BUCKET'))  # function returns only 1 bucket
    bucket_id = buckets.id
    org_id = buckets.org_id
    desc_prefix = f'IoTCenterDevice: {device_id}'
    org_resource = PermissionResource(org_id=org_id, id=bucket_id, type="buckets")
    print(org_resource)
    read = Permission(action="read", resource=org_resource)
    write = Permission(action="write", resource=org_resource)
    permissions = [write, read]
    print('org_id', org_id)
    print('permissions', permissions)
    print('desc_prefix', desc_prefix)
    authorization = Authorization(org_id=org_id, permissions=permissions, description=desc_prefix)
    print(authorization)
    request = authorization_api.create_authorization(authorization)
    return request


def create_device(device_id=None):
    config = configparser.ConfigParser()
    config.read('config.ini')
    influxdb_client = InfluxDBClient(url=config.get('APP', 'INFLUX_URL'),
                                     token=config.get('APP', 'INFLUX_TOKEN'),
                                     org=config.get('APP', 'INFLUX_ORG'))
    # influxdb_client = InfluxDBClient(url='http://localhost:8086/',
    #                                  token='YboNxQThPdJgecUYDcFM-aCiAUowJwfitF1F2TrzuNvstFxExhtl-AnWZOh8JCMGJHVHZmsDrYaRNMIY8G007w==',
    #                                  org='my_db')
    if device_id is None:
        device_id = str(uuid4())
    write_api = influxdb_client.write_api(write_options=SYNCHRONOUS)
    point = Point('deviceauth') \
        .tag("deviceId", device_id) \
        .field('key', f'fake_auth_id_{device_id}') \
        .field('token', f'fake_auth_token_{device_id}')
    client_response = write_api.write(bucket=config.get('APP', 'INFLUX_BUCKET_AUTH'), record=point)
    # write() returns None on success
    if client_response is None:
        return device_id
    # Return None on failure
    return None


def get_device(device_id=None) -> {}:
    influxdb_client = InfluxDBClient(url=config.get('APP', 'INFLUX_URL'),
                                     token=config.get('APP', 'INFLUX_TOKEN'),
                                     org=config.get('APP', 'INFLUX_ORG'))
    # Queries must be formatted with single and double quotes correctly
    query_api = QueryApi(influxdb_client)
    device_filter = ''
    if device_id:
        device_id = str(device_id)
        device_filter = f'r.deviceId == "{device_id}" and r._field != "token"'
    else:
        device_filter = f'r._field != "token"'

    flux_query = f'from(bucket: "{config.get("APP", "INFLUX_BUCKET_AUTH")}") ' \
                 f'|> range(start: 0) ' \
                 f'|> filter(fn: (r) => r._measurement == "deviceauth" and {device_filter}) ' \
                 f'|> last()'
    
    response = query_api.query(flux_query)
    result = []
    for table in response:
        for record in table.records:
            try:
                'updatedAt' in record
            except KeyError:
                record['updatedAt'] = record.get_time()
                record[record.get_field()] = record.get_value()
            result.append(record.values)
    return result


def write_measurements(device_id):
    influxdb_client = InfluxDBClient(url=config.get('APP', 'INFLUX_URL'),
                                     token=config.get('APP', 'INFLUX_TOKEN'),
                                     org=config.get('APP', 'INFLUX_ORG'))
    write_api = influxdb_client.write_api(write_options=SYNCHRONOUS)
    virtual_device = Sensor()
    coord = virtual_device.geo()
    point = Point("environment") \
        .tag("device", device_id) \
        .tag("TemperatureSensor", "virtual_bme280") \
        .tag("HumiditySensor", "virtual_bme280") \
        .tag("PressureSensor", "virtual_bme280") \
        .field("Temperature", virtual_device.generate_measurement()) \
        .field("Humidity", virtual_device.generate_measurement()) \
        .field("Pressure", virtual_device.generate_measurement()) \
        .field("Lat", coord['latitude']) \
        .field("Lon", coord['longitude']) \
        .time(datetime.utcnow())
    print(f"Writing: {point.to_line_protocol()}")
    client_response = write_api.write(bucket=config.get('APP', 'INFLUX_BUCKET'), record=point)
    # write() returns None on success
    if client_response is None:
        # TODO Maybe also return the data that was written
        return device_id
    # Return None on failure
    return None


def get_measurements(query):
    influxdb_client = InfluxDBClient(url=config.get('APP', 'INFLUX_URL'),
                                     token=config.get('APP', 'INFLUX_TOKEN'),
                                     org=config.get('APP', 'INFLUX_ORG'))
    query_api = QueryApi(influxdb_client)
    result = query_api.query_csv(query,
                                 dialect=Dialect(
                                       header=True,
                                       delimiter=",",
                                       comment_prefix="#",
                                       annotations=['group', 'datatype', 'default'],
                                       date_time_format="RFC3339"))
    response = ''
    for row in result:
        response += (',').join(row) + ('\n')
    return response


#@app.route('/api/devices/<string:device_id>', methods=['GET', 'POST'])
def api_get_device(device_id):
    if request.method == "OPTIONS": # CORS preflight
        return _build_cors_preflight_response()
    return _corsify_actual_response(jsonify(devices.get_device(device_id)))


create_authorization('1')
device_id_2 = create_device(device_id='testdevice')
write_measurements(device_id_2)
#write_measurements(device_id)
#write_measurements(device_id)
