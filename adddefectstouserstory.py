#!/usr/bin/env python

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

    excelname = 'testcasesattachtotestset.xlsx'
    testfoldersList = retrieveTestcaseResultFromSheet(excelname)

    for testsetRow in testfoldersList :
        for testcase, info in testsetRow.items() :
            # ident_query = 'WorkProduct.FormattedID = "%s"' % testsetID
            # ident_query = 'WorkProduct.FormattedID = "%s"' % testsetID
            # testcaseResponse = rallyUtil.rally.get('TestCase', fetch=True, query=ident_query,
            #                                        workspace=workspace, project=project)

            # testsetID = 'TS35586'


            # testsetID = 'TS34763'
            #
            # ident_query = 'FormattedID = %s' % testcase
            # testcaseResponse = rallyUtil.rally.get('TestCase', fetch=True, query=ident_query,
            #                                        workspace=workspace, project=project)
            # if testcaseResponse.errors:
            #     logger.error('fail to find test case {}'.format(testcase))
            #     continue
            # testcase = testcaseResponse.next()
            #
            #
            # rallyUtil.add_testcasetotestset(testsetID, testcase)
            userstoryID = 'US260622'
            # rallyUtil.add_testcasetotestfolder(testsetID, testcase)
            rallyUtil.add_defectstouserstory(userstoryID, testcase)



