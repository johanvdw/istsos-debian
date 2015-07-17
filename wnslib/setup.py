# -*- coding: utf-8 -*-
# ===============================================================================
#
# Authors: Massimiliano Cannata, Milan Antonovic
#
# Copyright (c) 2015 IST-SUPSI (www.supsi.ch/ist)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
#
# ===============================================================================
from os import path
from wnslib.operation import wnsOperation
from walib import databaseManager


class wnsSetup(wnsOperation):

    def __init__(self, wnsEnviron):
        wnsOperation.__init__(self, wnsEnviron)

    def executePost(self):

        directory = path.dirname(path.split(path.abspath(__file__))[0])
        services_dir = path.join(directory, "services")
        wns_dir = path.join(directory, "wnslib")
        sql_dir = path.join(wns_dir, "dbSetup.sql")
        aps_dir = path.join(services_dir, "notifications.aps")

        import datetime
        now = datetime.datetime.now()
        startDate = now.strftime('%Y-%m-%d %H:%M:%S')

        aps = open(aps_dir, 'w')
        aps.write("### CREATED ON " + str(startDate) + " ###")
        aps.close()

        db = open(sql_dir, 'r')
        sqlFile = db.read()
        db.close()

        sqlCommands = sqlFile.split(';')
        sqlCommands.pop()
        dbConnection = databaseManager.PgDB(
            self.serviceconf.connectionWns['user'],
            self.serviceconf.connectionWns['password'],
            self.serviceconf.connectionWns['dbname'],
            self.serviceconf.connectionWns['host'],
            self.serviceconf.connectionWns['port'])

        dbConnection.execute(sqlFile)
        msg = "Notification.aps file created in %s " % services_dir
        msg += "\nDatabase schema WNS correctly created"

        self.setMessage(msg)
