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
from walib import configManager

defaultCFGpath = path.join(path.dirname(path.split(path.abspath(__file__))[0]),
                                         "services/default.cfg")
serviceconf = configManager.waServiceConfig(defaultCFGpath)


def notify(name, message, status=True):
    """
        Attributes:
            name        name of the notification
            message     message to notify
    """
    from walib import databaseManager as dbm
    from wnslib import notify

    dbConnection = dbm.PgDB(
            serviceconf.connectionWns['user'],
            serviceconf.connectionWns['password'],
            serviceconf.connectionWns['dbname'],
            serviceconf.connectionWns['host'],
            serviceconf.connectionWns['port'])

    sql = """SELECT r.user_id_fk, r.not_list
            FROM wns.registration r, wns.notification n
            WHERE r.not_id_fk = n.id AND n.name=%s"""
    params = (name,)

    usersList = dbConnection.select(sql, params)

    #print usersList

    notifier = notify.Notify(serviceconf)
    if status:
        notifier.post_twitter_status(message['twitter'], name)

    for user in usersList:
        sql = "SELECT * FROM wns.user WHERE id = %s"
        par = [user['user_id_fk']]
        contact = dict(dbConnection.select(sql, par)[0])

        #print user['not_list']
        #print contact

        for con in user['not_list']:
            if con == 'mail' or con == 'email':
                if 'mail' in message.keys():
                    notifier.email(message['mail'], contact['email'])
            elif con == 'twitter':
                if 'twitter' in message.keys():
                    notifier.twitter(message['twitter'], contact['twitter'], name)
            elif con == 'fax':
                notifier.fax(message, contact['fax'], name)
            elif con == 'sms':
                notifier.sms(message, contact['tel'], name)
