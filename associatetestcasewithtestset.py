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
from gitTestCaseFromGit import get_aba_tc_list
from gitTestCaseFromGit import parsestringtolist
import configparser

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
    config = configparser.ConfigParser()
    config.read('config.ini')

    apikey = config['rally']['apikey']
    server = config['rally']['server']
    username = config['rally']['username']
    password = config['rally']['password']
    workspace = config['rally']['workspace']
    project = config['rally']['project']


    branch = config['testInfOnGit']['branch']
    aba_list = config['testInfOnGit']['aba_list']
    aba_list = parsestringtolist(aba_list)
    levels = parsestringtolist(config['testInfOnGit']['levels'])
    GIT_USER = config['testInfOnGit']['GIT_USER']
    GIT_PWD = config['testInfOnGit']['GIT_PWD']
    GITHUB_URL = config['testInfOnGit']['GITHUB_URL']

    testsetID = config['testset']['testsetID']


    rallyUtil = RallyUtil()
    ident_query = 'FormattedID = "{}"'.format(testsetID)
    testset = rallyUtil.rally.get('TestSet', fetch=True, query=ident_query,
                                 workspace=workspace, project=project)


    testset = next(testset, None)
    testcases = rallyUtil.get_testcases_from_testset(testsetID)

    for testcase in testcases:
        print("handle case", testcase.FormattedID)
        if not testcase.LastResult:
            continue
        ident_query = 'oid = "{}"'.format(testcase.LastResult.oid)
        result = rallyUtil.rally.get('TestCaseResult', fetch=True, query=ident_query,
                   workspace=workspace, project=project)

        testcaseresult = next(result, None)

        if testcaseresult is None:
            continue

        testcaseresult.TestTest = testset._ref
        updataDate = {"ObjectID" : testcaseresult.ObjectID, "TestSet": testset._ref}
        updated_re = rallyUtil.rally.update('TestCaseResult', updataDate)
        print(testcase.FormattedID)

        # if not testcaseresult.TestSet:
        #     testcaseresult.TestTest = testset._ref
        #     updataDate = {"ObjectID" : testcaseresult.ObjectID, "TestSet": testset._ref}
        #     updated_re = rallyUtil.rally.update('TestCaseResult', updataDate)
        #     print(testcase.FormattedID)










