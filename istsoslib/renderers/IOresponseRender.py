# -*- coding: utf-8 -*-
# istsos Istituto Scienze della Terra Sensor Observation Service
# Copyright (C) 2010 Massimiliano Cannata
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

def render(IO,sosConfig):
    r =  "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
    r += "  <sos:InsertObservationResponse xmlns:sos=\"http://www.opengis.net/sos/1.0\">"
    if IO.assignedId == "":
        r += "    <sos:AssignedObservationId/>"
    else:
        r += "    <sos:AssignedObservationId>" + str(IO.assignedId) + "</sos:AssignedObservationId>"
    r += "  </sos:InsertObservationResponse>"
    
    return r
