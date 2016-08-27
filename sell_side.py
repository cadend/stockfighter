#!/usr/local/bin/python

from SFCore import SFCore

core = SFCore("TESTEX", "")

heartbeat = core.heartbeat()
print heartbeat

venue_heartbeat = core.venue_heartbeat()
print venue_heartbeat

