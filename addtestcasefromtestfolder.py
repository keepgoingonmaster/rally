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

    testplanID = config['testplan']['testplanID']


    rallyUtil = RallyUtil()


    testcases = rallyUtil.get_testcases_from_testfolder(testplanID)

    for testcase in testcases:
        if testcase.c_TestCaseStatus != 'Active' or testcase.Method != 'Manual':
            continue

        rallyUtil.add_testcasetotestset(testsetID, testcase.FormattedID)









