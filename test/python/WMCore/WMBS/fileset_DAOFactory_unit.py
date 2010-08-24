#!/usr/bin/env python
"""
_FilesetExistsTestCase_

Unit tests for Fileset creation and exists, including checks to see that calls 
are database dialect neutral.

"""

__revision__ = "$Id: fileset_DAOFactory_unit.py,v 1.1 2008/06/12 10:04:09 metson Exp $"
__version__ = "$Revision: 1.1 $"

import unittest, logging, os, commands

from WMCore.Database.DBCore import DBInterface
from WMCore.Database.DBFactory import DBFactory
from WMCore.DAOFactory import DAOFactory
#pylint --rcfile=../../../../standards/.pylintrc  ../../../../src/python/WMCore/WMBS/Fileset.py

class BaseFilesetTestCase(unittest.TestCase):
    def setUp(self):
        "make a logger instance"
        #level=logging.ERROR
        logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename='%s.log' % __file__,
                    filemode='w')
        
        self.mysqllogger = logging.getLogger('wmbs_mysql')
        self.sqlitelogger = logging.getLogger('wmbs_sqlite')
        self.testlogger = logging.getLogger('unit_test')
        
        self.tearDown()
        
        self.dbf1 = DBFactory(self.mysqllogger, 'mysql://metson@localhost/wmbs')
        self.dbf2 = DBFactory(self.sqlitelogger, 'sqlite:///filesettest.lite')
        
        self.daofactory1 = DAOFactory(package='WMCore.WMBS', logger=self.mysqllogger, dbinterface=self.dbf1.connect())
        self.daofactory2 = DAOFactory(package='WMCore.WMBS', logger=self.sqlitelogger, dbinterface=self.dbf2.connect())
        
        theMySQLCreator = self.daofactory1(classname='CreateWMBS')
        createworked = theMySQLCreator.execute()
        
        if createworked:
            self.testlogger.debug("WMBS MySQL database created")
        else:
            self.testlogger.debug("WMBS MySQL database could not be created, already exists?")
            
        theSQLiteCreator = self.daofactory2(classname='CreateWMBS')
        createworked = theSQLiteCreator.execute()
        
        if createworked:
            self.testlogger.debug("WMBS SQLite database created")
        else:
            self.testlogger.debug("WMBS SQLite database could not be created, already exists?")
        
                       
    def tearDown(self):
        """
        Delete the databases
        """
        self.testlogger.debug(commands.getstatusoutput('echo yes | mysqladmin -u root drop wmbs'))
        self.testlogger.debug(commands.getstatusoutput('mysqladmin -u root create wmbs'))
        self.testlogger.debug("WMBS MySQL database deleted")
        try:
            self.testlogger.debug(os.remove('filesettest.lite'))
        except OSError:
            #Don't care if the file doesn't exist
            pass
        self.testlogger.debug("WMBS SQLite database deleted")

class FilesetExistsTestCase(BaseFilesetTestCase):
    def setUp(self):
        BaseFilesetTestCase.setUp(self)
        i = 0
        self.action1 = []
        self.action2 = []
        self.action3 = []
        self.action4 = []
        for daofactory in self.daofactory1, self.daofactory2:
            self.action1.append(daofactory(classname='Fileset.Exists'))
            self.action2.append(daofactory(classname='Fileset.New'))
            self.action3.append(daofactory(classname='Fileset.Delete')) 
            self.action4.append(daofactory(classname='Fileset.List'))
        
                
    def testCreateExists(self):
        for i in 0,1:
            assert self.action1[i].execute(name='fs001') == False, \
                               'fileset exists before it has been created'

            assert self.action2[i].execute(name='fs001') == True, \
                               'fileset cannot be created'

            assert self.action1[i].execute(name='fs001') == True, \
                               'fileset does not exist after it has been created'   
                               
            assert self.action3[i].execute(name='fs001') == True, \
                               'fileset cannot be deleted'
                               
            assert self.action1[i].execute(name='fs001') == False, \
                               'fileset exists after it has been deleted'
                               
        print " Create/Exist actions work as expected for MySQL and SQLite"

    def insertFilesets(self, size=5, conn=None):
        for i in range(size):
            try:
                self.action2[conn].execute(name='fs00%s' % i)
            except Exception, e:
                print e
    
    def testListDialectNeutral(self):
        s = 5
        self.insertFilesets(conn=0, size=s)  
        self.insertFilesets(conn=1, size=s)  
        
        themysqllist = self.action4[0].execute()
        thesqllitelist = self.action4[1].execute()
        
        self.testlogger.debug(themysqllist)
        self.testlogger.debug(thesqllitelist)        
                
        for i in themysqllist, thesqllitelist:
            assert len(i) == s, \
                'lists is wrong size %s not %s\n \t %s' % (len(i), s, i)
            assert type(i) == type([]), \
                'lists is not type list \n \t %s' % (type(i))
        
        assert themysqllist == thesqllitelist, \
            'lists do not match \n \t %s \n \t %s' % (themysqllist, thesqllitelist)
            
        print " List action is dialect neutral" 

    #def testAddAndList(self):
    #    for conn in self.dbf1.connect(), self.dbf2.connect():
    #        result = self.action5.execute(fileset='fs001', dbinterface=conn)
    #        assert type(result) == type([]), 'AddAndListFilesetAction did not return a list'
    #        assert len(result) == 1,\
    #            'List from AddAndListFilesetAction is of unexpected length (%s not 1) \n\t %s' % (len(result), result)
    #            
    #    print " AddAndListFilesetAction works as expected"
if __name__ == "__main__":
    unittest.main()