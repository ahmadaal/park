import json
import datetime
from datetime import timedelta, date
import calendar

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
        self.left_addresses = (int(feature_properties['lf_fadd']), int(feature_properties['lf_toadd']))
        self.right_addresses = (int(feature_properties['rt_fadd']), int(feature_properties['rt_toadd']))
        
        self.weeks = [
            True if feature_properties['week1ofmon'] == 'Y' else False,
            True if feature_properties['week2ofmon'] == 'Y' else False,
            True if feature_properties['week3ofmon'] == 'Y' else False,
            True if feature_properties['week4ofmon'] == 'Y' else False,
            True if feature_properties['week5ofmon'] == 'Y' else False,
        ]
    
    def get_week(self, date):
        return (date.day-1)//7+1
    
    def cleaning_day_number(self):
        return {
            "Mon": 0,
            "Tues": 1,
            "Wed": 2,
            "Thu": 3,
            "Fri": 4,
            "Sat": 5,
            "Sun": 6
        }[self.day]
    
    def cleaning_week_ranges(self):
        week_ranges = []
        for idx, week in enumerate(self.weeks):
            if week:
                week_ranges.append([7 * idx + day for day in range(0, 7)])
        return week_ranges
        
    def is_cleaning_this_week(self, date):
        proposed_week = self.get_week(date)
        return self.weeks[proposed_week - 1]
        
    def is_cleaning_this_date(self, date):
        for cleaning_week in self.cleaning_week_ranges():
            # If this is a week we're interested in 
            # print "checking {} in {}".format(day.day, cleaning_week)
            if date.day in cleaning_week:
                # and it's a day we're interested in
                # print "checking {} is weekday {}".format(day.weekday(), self.cleaning_day_number())
                if date.weekday() == self.cleaning_day_number():
                    return True
        return False
    
    def cleaning_schedule(self, start_date, end_date):
        today = datetime.datetime.now()
        schedule_dates = []
        cal = calendar.Calendar()
        for day_out in range((end_date - start_date).days):
            date_to_check = start_date + timedelta(day_out)
            if self.is_cleaning_this_date(date_to_check):
                schedule_dates.append(date_to_check)

        return schedule_dates
                    
    def cleaning_schedule_this_month(self):
        schedule_dates = []
        today = datetime.datetime.now()
        for week in calendar.Calendar().monthdatescalendar(today.year, today.month):
            for day in week:
                if self.is_cleaning_this_date(day):
                    schedule_dates.append(day)
        return schedule_dates
        
    def __repr__(self):
        return '; '.join(
        ["block_side = {}".format(self.block_side),
        "t_from = {}".format(self.t_from),
        "t_to = {}".format(self.t_to),
        "street_name = {}".format(self.street_name),
        "day = {}".format(self.day),
        "left_addresses = {}".format(self.left_addresses),
        "right_addresses = {}".format(self.right_addresses),
        "weeks = {}".format(self.weeks)])
        
    __str__ = __repr__

class ParkDB(object):
    def __init__(self):
        self.streets = {}

    def add_block(self, block):
        if not block.block_side:
            print "Skipping {}, no block side".format(block.street_name)
        if not block.street_name in self.streets:
            self.streets[block.street_name] = []
        self.streets[block.street_name].append(block)

    def find_block(self, street, address, side):
        # get blocks
        all_blocks = self.streets[street]
        
        # look for all the blocks with that address
        relevant_blocks = [
            block for block in all_blocks 
            if (address in range(*block.left_addresses) or address in range(*block.right_addresses)) and block.block_side == side
        ]
        return relevant_blocks

def parse_file(filename):
    data = parse_json(filename)
    count = 0
    db = ParkDB()
    for location in data['features']:
        b = Block(location['properties'])
 #       if not b.is_cleaning_this_week(datetime.datetime.now()):
 #           print "PARK HERE! {}".format(b.street_name) 
        db.add_block(b)
        count = count + 1

    for street, blocks in db.streets.iteritems():
        if len(set([b.block_side for b in blocks])) == 1:
            print "All sides were same for {}".format(blocks[0].street_name)
    print "{}/{}".format(count, len(data['features']))
    return db
big_file = "./data.json"
little_file = "./data.short.json"
#trimfile(big_file, 500)
#parse_file(little_file)
db = parse_file(big_file)
import pdb; pdb.set_trace()
