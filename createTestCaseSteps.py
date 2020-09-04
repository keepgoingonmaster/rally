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

from pyral import Rally, rallyWorkset

# import RallyUtil
from example import RallyUtil

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

    entity_name, ident = ("TestCase", "TF7360")
    ident_query = 'TestFolder.FormattedID = "%s"' % ident
    response = rallyUtil.rally.get(entity_name, fetch=True, query=ident_query,
                         workspace=workspace, project=project)

    excelname = 'testcaseSteps.xlsx'
    scenarios = retrieveTestcaseResultFromSheet(excelname)


    for testcase in response:
        testcaseID = testcase.FormattedID
        if testcaseID == "TC49577" :
            inputs = ["step11", "step21"]
            expect_results = ["", "step21-result2"]
            rallyUtil.add_teststeps_to_testcase(testcaseID, inputs, expect_results)

            # query = 'FormattedID = %s' % testcaseID
            # response = rallyUtil.rally.get("TestCase", fetch=True, query=query,
            #                      workspace=workspace, project=project)
            # testcase = response.next()
            # info = {
            #     'TestCase' : testcase._ref,
            #     'tester' : testcase.Owner._ref
            # }
            # rallyUtil.add_testresult(testcaseID, **info)

    print("done")
    # main(sys.argv[1 :])
