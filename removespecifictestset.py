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
os = {
    "Microsoft Windows Server": {
        2019,
        2016
    },
    "Amazon Linux": {
        2
    },
    "Red Hat Enterprise Linux": {
        8.1,
        7.7,
        7.6
    }
}
osList = ["Microsoft Windows Server","Amazon Linux","Red Hat Enterprise Linux"]
#################################################################################################

if __name__ == '__main__' :
    apikey = "_y0jdQIdhTSmCZ1PuzwmeGW1mYWee5UMNsFwUmFuVsEA"
    server = "rally1.rallydev.com"
    username = "jinewang@microstrategy.com"
    password = ""
    workspace = "MicroStrategy Workspace"
    project = "SR-Intelligence-Kernel"

    rallyUtil = RallyUtil()

    excelname = 'xlsx_updateTestCaseDiscussion.xlsx'
    testcasesList = retrieveTestcaseResultFromSheet(excelname)
    oldrelease = 'GA'
    newrelease = ''

    for testcaseRow in testcasesList:
        for testset_id, info in testcaseRow.items():
            rallyUtil.remove_testset(testset_id, osList)
            # rallyUtil.update_testset_name(testset_id, oldrelease, newrelease)


    print("done")
    # main(sys.argv[1 :])
