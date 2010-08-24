"""
_CreateWMBS_

Implementation of CreateWMBS for MySQL.

Inherit from CreateWMBSBase, and add MySQL specific substituions (e.g. add 
INNODB) and specific creaetes (e.g. for time stamp and enum fields).
"""

__revision__ = "$Id: CreateWMBS.py,v 1.19 2008/10/22 18:00:50 metson Exp $"
__version__ = "$Reivison: $"

from WMCore.WMBS.CreateWMBSBase import CreateWMBSBase

class CreateWMBS(CreateWMBSBase):
    """
    Class to set up the WMBS schema in a MySQL database
    """
    def __init__(self, logger, dbInterface):
        """
        _init_

        Call the base class's constructor and create all necessary tables,
        constraints and inserts.
        """        
        CreateWMBSBase.__init__(self, logger, dbInterface)

        self.create["03wmbs_fileset_files"] = \
          """CREATE TABLE wmbs_fileset_files (
             file        INT(11)   NOT NULL,
             fileset     INT(11)   NOT NULL,
             insert_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
               ON UPDATE CURRENT_TIMESTAMP,
             FOREIGN KEY(fileset) REFERENCES wmbs_fileset(id)
               ON DELETE CASCADE,
             FOREIGN KEY(file)    REFERENCES wmbs_file_details(id)
               ON DELETE CASCADE)"""
                     
        self.create["09wmbs_subscription"] = \
          """CREATE TABLE wmbs_subscription (
             id          INT(11)      NOT NULL AUTO_INCREMENT,
             fileset     INT(11)      NOT NULL,
             workflow    INT(11)      NOT NULL,
             split_algo  VARCHAR(255) NOT NULL DEFAULT 'File',
             type        ENUM('merge', 'processing'),
             last_update TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
             ON UPDATE CURRENT_TIMESTAMP,
             UNIQUE(fileset, workflow, type),   
             PRIMARY KEY(id),
             FOREIGN KEY(fileset) REFERENCES wmbs_fileset(id)
               ON DELETE CASCADE,
             FOREIGN KEY(workflow) REFERENCES wmbs_workflow(id)
               ON DELETE CASCADE)"""
          
        self.create["13wmbs_jobgroup"] = \
          """CREATE TABLE wmbs_jobgroup (
             id           INT(11)    NOT NULL AUTO_INCREMENT,
             subscription INT(11)    NOT NULL,
             uid          VARCHAR(255),    
             output       INT(11),
             last_update  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
             ON UPDATE CURRENT_TIMESTAMP,
             PRIMARY KEY (id),
             FOREIGN KEY (subscription) REFERENCES wmbs_subscription(id)
               ON DELETE CASCADE,
             FOREIGN KEY (output) REFERENCES wmbs_fileset(id)
                    ON DELETE CASCADE)"""
        
        self.create["14wmbs_job"] = \
          """CREATE TABLE wmbs_job (
             id          INT(11)   NOT NULL AUTO_INCREMENT,
             jobgroup    INT(11)   NOT NULL,
             name        VARCHAR(255),
             last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                 ON UPDATE CURRENT_TIMESTAMP,
             UNIQUE(name),
             PRIMARY KEY (id),
             FOREIGN KEY (jobgroup) REFERENCES wmbs_jobgroup(id)
               ON DELETE CASCADE)"""
        
        self.constraints["uniquewfname"] = \
          "CREATE UNIQUE INDEX uniq_wf_name on wmbs_workflow (name)"
        
        self.constraints["uniquewfspecowner"] = \
          """CREATE UNIQUE INDEX uniq_wf_spec_owner on
             wmbs_workflow (spec, owner)"""
        
        self.constraints["uniquelfn"] = \
          "CREATE UNIQUE INDEX uniq_lfn on wmbs_file_details (lfn)"

        self.constraints["uniquefilerunlumi"] = \
          """CREATE UNIQUE INDEX uniq_wmbs_file_run_lumi on
             wmbs_file_runlumi_map (file, run, lumi)"""
    def execute(self):
        for i in self.create.keys():
            self.create[i] = self.create[i] + " ENGINE=InnoDB"
            self.create[i] = self.create[i].replace('AUTOINCREMENT', 'AUTO_INCREMENT')
            self.create[i] = self.create[i].replace('INTEGER', 'INT(11)')
        return CreateWMBSBase.execute(self)    
        