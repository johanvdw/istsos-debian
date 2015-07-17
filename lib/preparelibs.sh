#  -*- coding: utf-8 -*-
# istsos WebAdmin - Istituto Scienze della Terra
# Copyright (C) 2012 Massimiliano Cannata, Milan Antonovic
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

# APSScheduler - Correcting imports in python files
find lib/apscheduler/ -name '*.py' -print0 | xargs -0 -n 1 sed -i -e 's/from apscheduler/from lib.apscheduler/g'
find lib/pytz/ -name '*.py' -print0 | xargs -0 -n 1 sed -i -e 's/from pytz/from lib.pytz/g'
find lib/pytz/ -name '*.py' -print0 | xargs -0 -n 1 sed -i -e 's/import pytz/import lib.pytz/g'
