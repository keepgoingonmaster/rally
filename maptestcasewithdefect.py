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
from datetime import datetime
import coloredlogs, logging, os
import json

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
    logging.basicConfig(level=logging.INFO,
                        # format='%(asctime)s.%(msecs)03d - %(name)s  [%(levelname)s] [%(threadName)s] %(message)s',
                        format='',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        filename='process.log',
                        filemode='w')

    coloredlogs.install()
    logging.addLevelName(logging.WARNING, "\033[1;31m%s\033[1;0m" % logging.getLevelName(logging.WARNING))
    logging.addLevelName(logging.ERROR, "\033[1;41m%s\033[1;0m" % logging.getLevelName(logging.ERROR))
    apikey = "_y0jdQIdhTSmCZ1PuzwmeGW1mYWee5UMNsFwUmFuVsEA"
    server = "rally1.rallydev.com"
    username = "jinewang@microstrategy.com"
    password = ""
    workspace = "MicroStrategy Workspace"
    project = "SR-Intelligence"

    rallyUtil = RallyUtil()

    excelname = 'testcase.xlsx'
    testcasesList = retrieveTestcaseResultFromSheet(excelname)

    start_time = datetime.now()

    result = {}
    highlevelresult = {}
    for testcaseRow in testcasesList:
       for defectID, testcase_json in testcaseRow.items():
           # eachdefect = dict()
           result.setdefault(defectID, [])
           highlevelresult.setdefault(defectID, [])
           print(defectID)

           ident_query = 'FormattedID = "%s"' % defectID
           ident_query_ = 'FormattedID = "{}"'.format(defectID)
           defectResponse = rallyUtil.rally.get('Defect', fetch=True, query=ident_query,
                                                 workspace=workspace)
                                                 # workspace=workspace, project=project)
           # defect_ = rallyUtil.rally.get('Defect', fetch=True,
           #                                        workspace=workspace, project=project)

           # defect = defectResponse.next()
           defect = next(defectResponse, None)
           if not defect:
               logging.error(f'{defectID} is not found')
               # result.append(eachdefect)
               continue
           # result.setdefault(defectID, [])
           if defect.TestCaseCount != 0:
               testcaseFommattedID = rallyUtil.gettestcasesFromDefect(defect)
               result[defectID].append(testcaseFommattedID)
               tempnewlist = highlevelresult[defectID] + testcaseFommattedID
               highlevelresult[defectID] = tempnewlist


           duplicatedDefects = rallyUtil.rally.getCollection(
               "https://rally1.rallydev.com/slm/webservice/v2.0/Defect/" + str(defect.oid) + "/Duplicates")

           if duplicatedDefects.errors:
               logging.error(f"{defect.FormattedID} Error in getting duplicated defects")
           else:
               logging.info(f'{defectID} ***duplicated defect begins***')
               for defect in duplicatedDefects:
                   testcaseFommattedID = testcaseFommattedID = rallyUtil.gettestcasesFromDefect(defect)
                   tmpdict = {defect.FormattedID: testcaseFommattedID}
                   result[defectID].append(tmpdict)
                   tempnewlist = highlevelresult[defectID] + testcaseFommattedID
                   highlevelresult[defectID] = tempnewlist
               logging.info(f'{defectID} ***duplicated defect ends  ***')
           # result.append(eachdefect)
    end_time = datetime.now()
    print('Duration: {}'.format(end_time - start_time))
    duration = end_time - start_time
    logging.info(f'Duration: {duration}')

    with open('result.log', 'w') as filehander:
        json.dump(result, filehander, indent=2)

    with open('highlevelresult.json', 'w') as filehander:
        json.dump(highlevelresult, filehander, indent=2)


    logging.info("Test is done")
    # main(sys.argv[1 :])



