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


def retrieveiteration(rally, iteration):
    itemResponse = rally.get('Iteration', fetch=True, query='Name = "%s"' % iteration)

    item = next(itemResponse, None)
    if item:
        return item._ref
    else:
        print('{} is invalid.'.format(iteration))
        # return None

def copytestset(rally, testsets, iterations, testseturl):
    for ts in testsets:
        response = rally.get('TestSet', fetch=True, query='FormattedID = "%s"' % ts)
        testset = next(response, None)
        if not response:
            print(ts + ' not found. Skipped.')
            continue

        ts_data = {
            "Project" : testset.Project.ref,
            "Owner" : testset.Owner.ref,
            "Name" : testset.Name,
            "Description" : testset.Description,
            "c_Result" : "Unexecuted",
            "ScheduleState" : "Defined",
            "c_ProductionRelease": c_ProductionRelease,
            "c_Stage": testset.c_Stage,
            "c_Type": testset.c_Type,
            "PlanEstimate": testset.PlanEstimate
        }

        # get iteration ref
        ### it will query iteration with the name specified in your project, but not the project of template test set ###
        for iteration in iterations:
            if retrieveiteration(rally, iteration):
                ts_data["Iteration"] = retrieveiteration(rally, iteration)

            try :
                tsn = rally.create('TestSet', ts_data)
            except Exception as details :
                logging.error(f'{details}')
            print(tsn.FormattedID + ' created.')

            # update test cases
            tcs = rally.getCollection(testseturl + str(testset.ObjectID) + "/TestCases")
            if tcs.errors :
                logging.error(f'Fail to copy test cases from {ts} to {tsn}')
            else :
                testcaselist = []
                for tc in tcs :
                    testcaselist.append(tc)
                rally.addCollectionItems(tsn, testcaselist)

            # create tasks
            tasks = rally.getCollection(testseturl + str(testset.ObjectID) + "/Tasks")
            if tasks.errors :
                logging.error(f'Fail to copy tasks from {ts} to {tsn}')
            else :
                for task in tasks :
                    task_data = {
                        "Name" : task.Name,
                        "Owner" : task.Owner.ref,
                        "Estimate" : task.Estimate,
                        "State" : "Defined", "WorkProduct" : tsn.ref
                    }
                    try :
                        taskn = rally.create('Task', task_data)
                    except Exception as details :
                        logging.error(f'{details}')
                        # print('ERROR: %s \n' % details)



def parsestringtolist(str):

    str = re.sub('[\[\]\']', '', str)

    return [re.sub(r'^\s+', '', item) for item in str.split(',')]


if __name__ == '__main__' :
    config = configparser.ConfigParser()
    config.read('config.ini')

    apikey = config['rally']['apikey']
    server = config['rally']['server']
    username = config['rally']['username']
    password = config['rally']['password']
    workspace = config['rally']['workspace']
    project = config['rally']['project']

    testsets = parsestringtolist(config['testsetcopy']['ts_list'])
    iterations = parsestringtolist(config['testsetcopy']['iterations'])
    c_ProductionRelease = config['testsetcopy']['c_ProductionRelease']
    testseturl = config['testsetcopy']['testseturl']

    rally = Rally(server, username, password, apikey=apikey, workspace=workspace, project=project)

    copytestset(rally, testsets, iterations, testseturl)

    # for iteration in iterations:
    #     retrieveiteration(rally, iteration)


