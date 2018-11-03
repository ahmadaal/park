import json
import datetime
from pprint import pprint

def trimfile(filename, length):
    with open(filename) as f:
        data = json.loads(f.read())
        assert data['type'] == 'FeatureCollection'
        out = data['features'][:length]
        print json.dumps({'type': 'FeatureCollection', 'features': out})
    exit()

def parse_json(filename):
    with open(filename) as f:
        data = json.loads(f.read())
        assert data['type'] == 'FeatureCollection'
        return data

class Block(object):
    def __init__(self, feature_properties):
        self.block_side = feature_properties['blockside']
        self.t_from = feature_properties['fromhour']
        self.t_to = feature_properties['tohour']
        self.street_name = feature_properties['streetname']
        self.day = feature_properties['weekday']
        self.weeks = [
            True if feature_properties['week1ofmon'] == 'Y' else False,
            True if feature_properties['week2ofmon'] == 'Y' else False,
            True if feature_properties['week3ofmon'] == 'Y' else False,
            True if feature_properties['week4ofmon'] == 'Y' else False,
            True if feature_properties['week5ofmon'] == 'Y' else False,
        ]

    def get_week(self, date):
        return (date.day-1)//7+1

    def is_cleaning_this_week(self, date):
        proposed_week = self.get_week(date)
        return self.weeks[proposed_week - 1]

def parse_file(filename):
    data = parse_json(filename)
    for location in data['features']:
        b = Block(location['properties'])
        if not b.is_cleaning_this_week(datetime.datetime.now()):
            print "PARK HERE! {}".format(b.street_name) 

big_file = "/Users/aa/Downloads/Historical Street Sweeper Scheduled Routes.geojson"
little_file = "./data.short.json"
#trimfile(big_file, 500)
parse_file(little_file)

