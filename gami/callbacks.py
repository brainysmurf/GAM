"""
Defines all the actions
"""

#TODO: Move this into __init__
__author__ = u'Adam Morris <amorris@mistermorris.com>'
__version__ = u'0.5'
__website__ = 'http://github.com/brainysmurf/gam'
__license__ = u'Apache License 2.0 (http://www.apache.org/licenses/LICENSE-2.0)'

class UsefulCallbacks(object):
    """
    Just a class th
    """
    @staticmethod
    def creation_time_callback(creation_time):
        import datetime
        my_date = creation_time[:15]
        my_offset = creation_time[19:]
        return "{} {}".format(datetime.datetime.strptime(my_date, u"%Y%m%dT%H%M%S"), my_offset)






