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
    project = "SR-Intelligence-Metadata"

    rallyUtil = RallyUtil()

    excelname = 'deletelatesttestcaseresult.xlsx'
    testcasesList = retrieveTestcaseResultFromSheet(excelname)

    for testcaseRow in testcasesList:
        for testcase, info in testcaseRow.items():
            entity_name, identity = ("TestCaseResult", testcase)
            ident_query = 'TestCase.FormattedID = "%s"' % identity
            testcaseResponse = rallyUtil.rally.get(entity_name, fetch=True, query=ident_query,
                                 workspace=workspace, project=project)
            if testcaseResponse.errors or testcaseResponse.data['TotalResultCount'] == 0:
                logger.error('fail to get test result for the given testcase {}'.format(testcase))
                continue

            index = testcaseResponse.resultCount

            testcaseresult = testcaseResponse.data['Results'][index-1]['ObjectID']
            rallyUtil.rally.delete('TestCaseResult', testcaseresult)


    print("done")
    # main(sys.argv[1 :])
