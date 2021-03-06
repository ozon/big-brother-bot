#
# BigBrotherBot(B3) (www.bigbrotherbot.net)
# Copyright (C) 2011 Courgette
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
import os
from b3.storage.database import DatabaseStorage
from tests import B3TestCase
from tests.storage.common import StorageAPITest
import nose
import unittest2 as unittest


"""
    NOTE: you can customize the MySQL host, database and credential using the following
    environment variables :
        MYSQL_TEST_HOST
        MYSQL_TEST_USER
        MYSQL_TEST_PASSWORD
        MYSQL_TEST_DB
"""
MYSQL_TEST_HOST = os.environ.get('MYSQL_TEST_HOST', 'localhost')
MYSQL_TEST_USER = os.environ.get('MYSQL_TEST_USER', 'b3test')
MYSQL_TEST_PASSWORD = os.environ.get('MYSQL_TEST_PASSWORD', 'test')
MYSQL_TEST_DB = os.environ.get('MYSQL_TEST_DB', 'b3_test')

#===============================================================================
# 
# Test if we can run the MySQL tests
#
#===============================================================================

is_mysql_ready = True
no_mysql_reason = ''

try:
    import pymysql
except ImportError:
    # debian wheezy has python-mysql.connector instead of pymysql
    try:
        import mysql.connector as pymysql
    except ImportError:
        pymysql = None
        is_mysql_ready = False
        no_mysql_reason = "no pymysql or mysql.connector module available"
if is_mysql_ready:
    try:
        pymysql.connect(host=MYSQL_TEST_HOST, user=MYSQL_TEST_USER, passwd=MYSQL_TEST_PASSWORD)
    except pymysql.Error, err:
        is_mysql_ready = False
        no_mysql_reason = "%s" % err[1]
    except Exception, err:
        is_mysql_ready = False
        no_mysql_reason = "%s" % err


#===============================================================================
# 
# Load the tests
# 
#===============================================================================
@unittest.skipIf(not is_mysql_ready, no_mysql_reason)
class Test_MySQL(B3TestCase, StorageAPITest):

    def setUp(self):
        """this method is called before each test"""
        B3TestCase.setUp(self)
        try:
            db = pymysql.connect(host=MYSQL_TEST_HOST, user=MYSQL_TEST_USER, password=MYSQL_TEST_PASSWORD)
        except pymysql.OperationalError, message:
            self.fail("Error %d:\n%s" % (message[0], message[1]))
        db.query("DROP DATABASE IF EXISTS `%s`" % MYSQL_TEST_DB)
        db.query("CREATE DATABASE `%s` CHARACTER SET utf8;" % MYSQL_TEST_DB)
        self.storage = self.console.storage = DatabaseStorage("mysql://%s:%s@%s/%s" % (MYSQL_TEST_USER, MYSQL_TEST_PASSWORD, MYSQL_TEST_HOST, MYSQL_TEST_DB), self.console)
        self.storage.connect()
        # Fenix: we dont need this anymore since B3 already pupulate the database if no table is found
        #self.storage.queryFromFile("@b3/sql/b3.sql")

    def tearDown(self):
        """this method is called after each test"""
        B3TestCase.tearDown(self)
        self.storage.query("DROP DATABASE `%s`" % MYSQL_TEST_DB)
        self.storage.shutdown()

    def test_getTables(self):
        self.assertSetEqual(set(
            ['aliases',
             'ipaliases',
             'clients',
             'groups',
             'penalties',
             'data',
             'xlr_bodyparts',
             'xlr_mapstats',
             'xlr_opponents',
             'xlr_playerbody',
             'xlr_playermaps',
             'xlr_playerstats',
             'xlr_weaponstats',
             'xlr_weaponusage',
             'xlr_actionstats',
             'xlr_playeractions',
             'xlr_history_monthly',
             'xlr_history_weekly',
             'ctime'
            ]), set(self.storage.getTables()))

if __name__ == '__main__':
    nose.main()
    
    
