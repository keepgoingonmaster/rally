# !/usr/bin/env python

#################################################################################################
#
# getitem.py -- Get info for a specific instance of a Rally type
#               identified either by an OID or a FormattedID value
#
USAGE = """
Usage: getitem.py <entity_name> <OID | FormattedID>    
"""
#################################################################################################

import sys
import re
import string
import datetime
import logging, os

from pyral import Rally, rallyWorkset

# import RallyUtil
from example import RallyUtil
import openpyxl
from parseExcelEnhancement import retrieveTestcaseResultFromSheet

logger = logging.getLogger('mylogger')
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

fh = logging.FileHandler(os.path.join(os.path.dirname(os.path.abspath("__file__")), 'testerror.log'))  # file log
ch = logging.StreamHandler()

fh.setFormatter(formatter)
ch.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)

#################################################################################################
#################################################################################################

if __name__ == '__main__' :
    apikey = "_y0jdQIdhTSmCZ1PuzwmeGW1mYWee5UMNsFwUmFuVsEA"
    server = "rally1.rallydev.com"
    username = "jinewang@microstrategy.com"
    password = ""
    workspace = "MicroStrategy Workspace"
    project = "SR-Intelligence-Kernel"

    rallyUtil = RallyUtil()

    excelname = 'testcase.xlsx'
    testcasesList = retrieveTestcaseResultFromSheet(excelname)

    for testcaseRow in testcasesList:
       for defectID, testcase_json in testcaseRow.items():
           print(defectID)
           # testcaseID = 'TC8818'
           # ident_query1 = 'FormattedID = "%s"' % testcaseID
           # ident_query_1 = 'FormattedID = "{}"'.format(testcaseID)
           # testcaseResponse = rallyUtil.rally.get('TestCase', fetch=True, query=ident_query1,
           #                                      workspace=workspace, project=project)
           # defectID='DE32108'
           ident_query = 'FormattedID = "%s"' % defectID
           ident_query_ = 'FormattedID = "{}"'.format(defectID)
           defectResponse = rallyUtil.rally.get('Defect', fetch=True, query=ident_query,
                                                 workspace=workspace, project=project)
           # defect_ = rallyUtil.rally.get('Defect', fetch=True,
           #                                        workspace=workspace, project=project)
           defect = defectResponse.next()
           if defect.TestCaseCount == 0:
               testcase = rallyUtil.create_testcaseFromDefect(defect, owner = None, **testcase_json)
        # logger.info(defectID, testcase.FormattedID)

    logger.info("done")
    # main(sys.argv[1 :])



