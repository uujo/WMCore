#!/usr/bin/env python
"""
_FilesTestCase_

Unit tests for File creation, location and exists, including checks to see that calls 
are database dialect neutral.

"""

__revision__ = "$Id: files_DAOFactory_unit.py,v 1.1 2008/06/12 10:04:09 metson Exp $"
__version__ = "$Revision: 1.1 $"

import unittest, logging, os, commands

from WMCore.Database.DBCore import DBInterface
from WMCore.Database.DBFactory import DBFactory
from WMCore.DAOFactory import DAOFactory
#pylint --rcfile=../../../../standards/.pylintrc  ../../../../src/python/WMCore/WMBS/Fileset.py

class BaseFilesTestCase(unittest.TestCase):
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
        
class CreateListDeleteTestCase(BaseFilesTestCase):
    def setUp(self):
        BaseFilesTestCase.setUp(self)
        
        newFS = self.daofactory1(classname='Fileset.New')
        assert newFS.execute(name='fs001')
        
        newFS = self.daofactory2(classname='Fileset.New')
        assert newFS.execute(name='fs001')
        
        self.action1 = self.daofactory1(classname='Files.Add')
        self.action2 = self.daofactory1(classname='Files.AddToFileset')
        self.action3 = self.daofactory1(classname='Files.InFileset')
        self.action4 = self.daofactory1(classname='Files.SetLocation')
        
        self.action1a = self.daofactory2(classname='Files.Add')
        self.action2a = self.daofactory2(classname='Files.AddToFileset')
        self.action3a = self.daofactory2(classname='Files.InFileset')
        self.action4a = self.daofactory2(classname='Files.SetLocation')
        
    def testCreate(self, notest=False):
        file = "/store/data/Electrons/1234/5678/hkh123ghk12khj3hk123ljhkj1231.root"
        
        self.action1.execute(files=file, size=1000, events=2000, run=10, lumi=12312)
        self.action1a.execute(files=file, size=1000, events=2000, run=10, lumi=12312)
        
        self.action2.execute(file=file, fileset='fs001')
        self.action2a.execute(file=file, fileset='fs001')
        
        list = self.action3.execute(fileset='fs001')
        assert len(list) == 1, \
            "list has wrong length (%s not 1) \n \t %s" %(len(list), list)
        
        list = self.action3a.execute(fileset='fs001')
        assert len(list) == 1, \
            "list has wrong length (%s not 1) \n \t %s" %(len(list), list)
        
    def testListCreate(self, notest=False):
        filelist = []
        filelist.append(("/store/data/Electrons/1234/5678/hkh123ghk12khj3hk123ljhkj1232.root", 1000, 2000, 10, 12312))
        filelist.append(("/store/data/Electrons/1234/5678/hkh123ghk12khj3hk123ljhkj1233.root", 1000, 2000, 10, 12312))
        filelist.append(("/store/data/Electrons/1234/5678/hkh123ghk12khj3hk123ljhkj1234.root", 1000, 2000, 10, 12312))
        
        self.action1.execute(files=filelist)
        self.action1a.execute(files=filelist)

        def strim(tuple): return tuple[0]
        filelist = map(strim, filelist)
        
        self.action2.execute(file=filelist, fileset='fs001')
        self.action2a.execute(file=filelist, fileset='fs001')
        
        list = self.action3.execute(fileset='fs001')
        assert len(list) == 3 or notest, \
            "list has wrong length (%s not 3) \n \t %s" %(len(list), list)
            
        list = self.action3a.execute(fileset='fs001')
        assert len(list) == 3 or notest, \
            "list has wrong length (%s not 3) \n \t %s" %(len(list), list)
    
    def testListDialectNeutral(self):
        self.testListCreate(notest=True)
        mysqllist = self.action3.execute(fileset='fs001')
        sqllitelist = self.action3a.execute(fileset='fs001')
        
        assert mysqllist == sqllitelist, \
            "Lists are not dialect neutral \n \t %s \n \t %s" % (mysqllist, sqllitelist)
        
    def testLocateFiles(self):
        self.testListCreate(notest=True)
        
        se1 = 'lcgse01.phy.bris.ac.uk'
        se2 = 'lcgse02.phy.bris.ac.uk'
        selist = ['se01.fnal.gov', 'se02.fnal.gov']
        
        list = self.action3.execute(fileset='fs001')
        lista = self.action3a.execute(fileset='fs001')
        
        def strim(tuple): return tuple[1]
        
        list = map(strim, list)
        lista = map(strim, lista)
        
        self.action4.execute(file=list, sename=se1)
        self.action4a.execute(file=lista, sename=se1)
        
        for i in list:
            self.action4.execute(file=i, sename=se2)
            
        for i in lista:    
            self.action4a.execute(file=i, sename=se2)
            
        self.action4.execute(file=list, sename=selist)
        self.action4a.execute(file=list, sename=selist)
          
            
if __name__ == "__main__":
    unittest.main()