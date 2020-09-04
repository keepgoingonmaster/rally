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

    excelname = 'testcaseResult.xlsx'
    testcasesList = retrieveTestcaseResultFromSheet(excelname)

    sourcetestset_id = 'TS31391'
    c_ProductionRelease = "11.2 GA [2019-Dec-06]"
    c_Stage = "GA Build Validation"

    # rallyUtil.copyTestSet(sourcetestset_id, c_ProductionRelease, c_Stage)
    # ident_query = 'TestSet.FormattedID = "%s"' % testsetID
    # testcaseResponse = rallyUtil.rally.get('TestCase', fetch=True, query=ident_query,
    #                                        workspace=workspace, project=project)

    # ident_querytask = 'FormattedID = "%s"' % 'TA1132781'
    # ident_querytask = 'TestSet.FormattedID = "%s"' % 'TS35612'
    # # taskResponse = rallyUtil.rally.get('Task', fetch=True, query=ident_querytask, instance=True)
    # query = 'WorkProduct.Type = "TestSet"'
    querytestset = 'FormattedID = "%s"' % 'TS35612'
    taskResponse = rallyUtil.rally.get('TestSet', fetch=True, query=querytestset, workspace=workspace, project=project)
    #
    entry = taskResponse.next()
    #
    tasks = entry.Tasks
    testcase = entry.TestCases
    #
    # print(tasks)



    # for testcaseRow in testcasesList:
    #     for testcase, info in testcaseRow.items():
    #         if 'tester' in info:
    #             testerResponse = rallyUtil.rally.get('User', fetch=True, query='DisplayName = "%s"' % info['tester'],
    #                                                  workspace=workspace, project=project)
    #             if testerResponse.errors or testerResponse.data['TotalResultCount'] == 0:
    #                 logger.error('fail to add test result to {} for the given user {} does not exist'.format(testcase, info['tester']))
    #                 continue
    #             info['tester'] = testerResponse.next()._ref
    #
    #         entity_name, identity = ("TestCase", testcase)
    #         ident_query = 'FormattedID = "%s"' % identity
    #         testcaseResponse = rallyUtil.rally.get(entity_name, fetch=True, query=ident_query,
    #                              workspace=workspace, project=project)
    #         if testcaseResponse.errors or testcaseResponse.data['TotalResultCount'] == 0:
    #             logger.error('fail to add test result to {} for the given testcase {} does not exist'.format(testcase, testcase))
    #             continue
    #
    #         info['TestCase'] = testcaseResponse.next()._ref;
    #         rallyUtil.add_testresult(testcase, **info)

    print("done")
    # main(sys.argv[1 :])
