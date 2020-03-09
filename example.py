import sys, datetime, logging, os, configparser, json
from pyral import Rally, rallyWorkset

logger = logging.getLogger('mylogger')
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

fh = logging.FileHandler(os.path.join(os.path.dirname(os.path.abspath("__file__")), 'test.log'))  # file log
ch = logging.StreamHandler()

fh.setFormatter(formatter)
ch.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)


class RallyUtil(object):
    def __init__(self, RallyServer='rally1.rallydev.com', \
                 APIKep='_fONhEFO2RHW87EMPIc4II1yY1fx4PEmtgpW85jMq7eI', \
                 workspace='MicroStrategy Workspace', project='SR-Intelligence-Kernel', \
                 loggingfile='Rally.log'):
        self.rally = Rally(server=RallyServer, apikey=APIKep, workspace=workspace, project=project,
                           projectScopeDown=True)
        self.rally.enableLogging(loggingfile)

    def get_testcase_by_id(self, testcase_id):
        return self._get_entity_by_id(testcase_id)

    def get_testset_by_id(self, testset_id):
        return self._get_entity_by_id(testset_id)

    def set_testcase_name(self, testcase_id, testcase_name):
        self._set_entity(testcase_id, Name=testcase_name)

    def _get_entity_by_id(self, entity_id):
        entity_type = self._get_entity_type(entity_id)
        query = 'FormattedID = {}'.format(entity_id)
        return self.rally.get(entity_type, query=query, project=None, instance=True)

    def get_defect_by_id(self, defect_id):
        return self._get_entity_by_id(defect_id)

    def _set_entity(self, entity_id, **info):
        entity_type = self._get_entity_type(entity_id)
        info['FormattedID'] = entity_id
        logger.debug(info)
        self.rally.update(entity_type, info)

    def get_object_by_id(self, type, oid):
        response = self.rally.get(type, fetch=True, query='ObjectID = ',
                                  workspace=workspace, project=project)

    def get_alluserinfo(self):
        return self.rally.getAllUsers()

    def get_userstorys_by_product_release(self, *product_releases):

        query = 'c_ProductionRelease = "11.1.2 [2019-Jun-7]" OR c_ProductionRelease = "11.2 RC [2019-Sep-20]" OR c_ProductionRelease = "11.2 EA [2019-Jun-21]"'
        # query = 'c_ProductionRelease = "11.1.2 [2019-Jun-7]"'
        response = self.rally.get('UserStory', query=query,
                                  fetch=True, projectScopeDown=True)

        userstorys = []
        for entry in response:
            logger.debug(entry.FormattedID, entry.Name)
            userstorys.append(entry)

        return userstorys

    def create_testcase(self, testcase_name, testfolder_id, status, test_type, owner):
        # note, owner should be Email address, e.g. jiazhang@microstrategy.com

        testcase_json = {
            "Workspace": self.rally.getWorkspace().ref,
            "Project": self.rally.getProject().ref,
            "Name": testcase_name,
            "TestFolder": self.get_testfolder(testfolder_id)._ref,
            "Method": "Manual",
            "Type": test_type,
            "Priority": "Useful",
            "Risk": "Low",
            "c_TestCaseStatus": status,
            "c_UPCComponent": "017 Tool : Administration",
            "c_UPCModule": "017.000 Administration",
            "Owner": self.rally.getUserInfo(username=owner)[0].ref
        }
        testcase = self.rally.create('TestCase', testcase_json)
        logger.debug(testcase.details())
        return testcase

    def create_testset(self, testsetName, iterationName, stage, test_type, owner):
        # note, owner should be Email address, e.g. jiazhang@microstrategy.com

        query = 'Name = "%s"' % iterationName
        iteration = self.rally.get('Iteration', fetch=True, query=query,  projectScopeDown=True)
                                       # workspace=workspace, project=project)
        iteration = next(iteration, None)
        if not iteration:
            logging.error(f"{create_testset.__name__} get iteration fail")
            return

        testset_json = {
            "Workspace": self.rally.getWorkspace().ref,
            "Project": self.rally.getProject().ref,
            "Name": testsetName,
            "c_Result": "Unexecuted",
            "c_Stage": stage,
            "c_Type": test_type,
            "Iteration": iteration.ref,
            # "c_UPCComponent": "017 Tool : Administration",
            # "c_UPCModule": "017.000 Administration",
            "Owner": self.rally.getUserInfo(name=owner)[0].ref
        }
        testset = self.rally.create('TestSet', testset_json)
        logger.debug(testset.details())
        return testset.FormattedID


    def create_testcaseFromDefect(self, defect, owner = None, **testcase_json):
        # note, owner should be corp user name, such as "Jine Wang"
        # ident_query = 'FormattedID = "%s"' % defectID
        # workproduct = self.rally.get('Defect', fetch=True, query=ident_query, projectScopeDown=True)
        # # workproduct = self.rally.get('Defect', fetch=True, query=ident_query, workspace='current', project='current')
        # # self.rally.get.get(entity_name, fetch=True, query=ident_query, workspace=workspace, project=project)
        # defect = workproduct.next()

        testcase_json["Workspace"]   = self.rally.getWorkspace().ref
        testcase_json["Project"]     = self.rally.getProject().ref
        testcase_json["Name"]        = defect.FormattedID + " | " + defect.c_ProductionRelease.split()[0] + " | " + defect.Name
        testcase_json["Description"] = defect.Description
        testcase_json["Owner"]       = defect.Owner._ref
        testcase_json["WorkProduct"] = defect._ref
        testcase_json["Risk"]        = "Low"
        testcase_json["c_UPCModule"]  = defect.c_UPCModule
        testcase_json["c_UPCComponent"] = defect.c_UPCComponent
        testcase_json["c_TestCaseStatus"] = "Active"
        testcase_json["Type"] = "Regression"


        testcase = self.rally.create('TestCase', testcase_json)
        print(testcase.FormattedID, defect.FormattedID)
        return testcase


    def gettestcasesFromDefect(self, defect):
        result = []
        testcases = self.rally.getCollection(
            "https://rally1.rallydev.com/slm/webservice/v2.0/Defect/" + str(defect.oid) + "/TestCases")
        if testcases.errors :
            logging.error(f"{defect.FormattedID} Error in getting test cases")
        else :
            flag = True
            for testcase in testcases :
                flag = False
                result.append(testcase.FormattedID)
                logging.info(f'{defect.FormattedID} {testcase.FormattedID} {testcase.c_TestCaseStatus} {testcase.Method}')
        if flag:
            logging.info(f'         {defect.FormattedID} has no test case')
        return result

    def get_testcases_from_testfolder(self, testfolder_id):
        # query critial to get all active test cases
        query = 'TestFolder.FormattedID = "%s"' % testfolder_id
        response = self.rally.get('TestCase', query=query,
                                  fetch=True, projectScopeDown=True)

        test_cases = []
        for entry in response:
            logger.debug(entry.FormattedID, entry.Name)
            test_cases.append(entry)

        return test_cases

    def delete_all_testcases_in_testfolder(self, testfolder_id):
        for item in self.get_testcases_from_testfolder(testfolder_id=testfolder_id):
            logger.info('deleting testcase {} {}'.format(item.FormattedID, item.Name))
            self.rally.delete(entityName='TestCase', itemIdent=item.FormattedID, project='current', workspace='current')


    def get_defects_by_date(self, defect_id, start_date, end_date):
        query = 'Iteration.StartDate > "{}" AND Iteration.StartDate < "{}"'.format(start_date, end_date)
        response = self.rally.get('Defect', fetch=True, query=query, projectScopeDown=True)
        defects = []
        for item in response:
            logger.debug('{},{}'.format(item.FormattedID, item.Name))
            defects.append(item)

    def get_defects_with_query(self, query):
        response = self.rally.get('Defect', fetch=True, query=query, projectScopeDown=True)
        defects = []
        for item in response:
            logger.debug('{},{}'.format(item.FormattedID, item.Name))
            defects.append(item)

        return defects

    def set_defect(self, defect_id, **info):
        self._set_entity(defect_id, **info)


    def add_testresult(self, testcase_id, **info):
        # logger.info('adding test result to {}'.format(testcase_id))
        info['TestCase'] = self.get_testcase_by_id(testcase_id).ref
        if not 'date' in info:
            info['date'] = str(datetime.datetime.utcnow().isoformat())
        if not 'tester' in info:
            info['tester'] = self.get_testcase_by_id(testcase_id).Owner.ref
        if not 'Verdict' in info:
            info['Verdict'] = 'Unexecuted'
        if not 'c_ProductionRelease' in info:
            info['c_ProductionRelease'] = '11.1.2 [2019-Jun-7]'
        if not 'Build' in info:
            info['Build'] = '0.0.0.0'
        if not 'Notes' in info:
            info['Notes'] = 'this result was added by script automatically'

        # self.rally.create('TestCaseResult', info)
        try:
            self.rally.create('TestCaseResult', info)
            logger.info('test case result for test case {} is added'.format(testcase_id))
        except Exception as re:
            logger.error('Fail to update test case {}, {}'.format(testcase_id, re))

    def add_testcasetotestset(self, testset_id, testcase_id):
        entity = self._get_entity_by_id(testset_id)
        testcasesList = []
        testcase = self.get_testcase_by_id(testcase_id)
        testcasesList.append(testcase)

        try:
            self.rally.addCollectionItems(entity, testcasesList)
            logger.info('adding test case {} to test set {}'.format(testcase.FormattedID, testset_id))
        except Exception as re:
            logger.error('Fail to add test case {} to test set {}: {}'.format(testcase_id, testset_id, re))

    def add_testcasetotestfolder(self, testfolder_id, testcase_id):
        entity = self._get_entity_by_id(testfolder_id)
        testcasesList = []
        testcase = self.get_testcase_by_id(testcase_id)
        testcasesList.append(testcase)

        try:
            self.rally.addCollectionItems(entity, testcasesList)
            logger.info('adding test case {} to test set {}'.format(testcase.FormattedID, testfolder_id))
        except Exception as re:
            logger.error('Fail to add test case {} to test set {}: {}'.format(testcase_id, testfolder_id, re))


    def add_defectstouserstory(self, userstory_id, defect_id):
        entity = self._get_entity_by_id(userstory_id)
        defectsList = []
        defect = self.get_testcase_by_id(defect_id)
        defectsList.append(defect)

        try:
            self.rally.addCollectionItems(entity, testcasesList)
            logger.info('adding test case {} to test set {}'.format(defect_id.FormattedID, userstory_id))
        except Exception as re:
            logger.error('Fail to add test case {} to test set {}: {}'.format(defect_id, userstory_id, re))

    def copyTestSet(self, sourcetestset_id, c_ProductionRelease, c_Stage):
        entity = self._get_entity_by_id(sourcetestset_id)
        # ident_query = 'FormattedID = "%s"' % sourcetestset_id
        # testset = self.rally.get('TestSet', fetch=True, query=ident_query, instance=True)
        # testset = testset.next()

        # querytestcase = 'TestCase.FormattedID = "%s"' % testcase_id
        # testcaseDiscussion = self.rally.get('ConversationPost', query=querytestcase, instance=True)

        # info = {}
        # info['c_ProductionRelease'] = c_ProductionRelease
        # info['Tasks'] = entity.Tasks
        # info['Owner'] = entity.Owner
        # info['Description'] = entity.Description
        # info['Name'] = entity.Name
        # info['Project'] = entity.Project
        # info['TestCases'] = entity.TestCases
        # info['c_Stage'] = c_Stage

        # testset_json = {
        #     "Workspace" : self.rally.getWorkspace().ref,
        #     "Project" : self.rally.getProject().ref,
        #     "Name" : entity.Name,
        #     "Description" : entity.Description,
        #     "c_ProductionRelease" : c_ProductionRelease,
        #     "Tasks" : entity.Tasks['_ref'],
        #     "Owner" : entity.Owner['_ref'],
        #     "TestCases" : entity.TestCases['_ref'],
        #     "c_Stage" : c_Stage,
        #     # "c_UPCComponent" : "017 Tool : Administration",
        #     # "c_UPCModule" : "017.000 Administration",
        #     # "Owner" : self.rally.getUserInfo(username=owner)[0].ref
        # }

        # taskList = testset.__collection_ref_for_Tasks
        # testset.__getattr__(__collection_ref_for_Tasks)

        testset_json = {
            "Workspace" : self.rally.getWorkspace().ref,
            "Project" : self.rally.getProject().ref,
            "Name" : entity.Name,
            "Description" : entity.Description,
            "c_ProductionRelease" : c_ProductionRelease,
            # "Tasks" : testset.__collection_ref_for_Tasks,
            # "Owner" : testset.Owner['_ref'],
            # "TestCases" : __collection_ref_for_TestCases,
            "c_Stage" : c_Stage,
            # "c_UPCComponent" : "017 Tool : Administration",
            # "c_UPCModule" : "017.000 Administration",
            # "Owner" : self.rally.getUserInfo(username=owner)[0].ref
        }
        testset = self.rally.create('TestSet', testset_json)
        logger.info('create test set {}'.format(testset.FormattedID))

        ident_query = 'TestSet.FormattedID = "%s"' % sourcetestset_id
        testcaseResponse = self.rally.get('TestCase', fetch=True, query=ident_query, instance=True)

        # testcaseList = []
        for testcase in testcaseResponse:
            testcaseList = []
            testcaseList.append(testcase)
            try :
                responses = self.rally.addCollectionItems(testset, testcaseList)
                logger.info('adding test case {} to test set {}'.format(testcase.FormattedID, testset.FormattedID))
            except Exception as re :
                logger.error('Fail to add test case {} to test set {}: {}, {}'.format(testcase.FormattedID, testset.FormattedID, re, responses.errors))

        # ident_querytask = 'TestSet.FormattedID = "%s"' % sourcetestset_id
        # taskResponse = self.rally.get('Task', fetch=True, query=ident_querytask, instance=True)

        taskList= entity.Tasks
        responses = self.rally.addCollectionItems(testset, taskList)


        # for task in taskResponse :
        #     taskList = []
        #     taskList.append(task)
        #     try :
        #         responses = self.rally.addCollectionItems(testset, taskList)
        #         logger.info('adding test case {} to test set {}'.format(task.FormattedID, testset.FormattedID))
        #     except Exception as re :
        #         logger.error(
        #             'Fail to add test case {} to test set {}: {}, {}'.format(task.FormattedID, testset.FormattedID,
        #                                                                      re, responses.errors))

        print(testcase)
        logger.debug(testcase.details())
        # print(info)
        # ident_query = 'TestSet.FormattedID = "%s"' % sourcetestset_id

        # testcaseResponse = rallyUtil.rally.get('TestCase', fetch=True, query=ident_query, project='current', workspace='current')
        #
        # testcaseList = []
        # for testcase in testcaseResponse:
        #     testcaseList.append(testcase)
        #     try :
        #         self.rally.addCollectionItems(entity, testcasesList)
        #         logger.info('adding test case {} to test set {}'.format(testcase.FormattedID, testset_id))
        #     except Exception as re :
        #         logger.error('Fail to add test case {} to test set {}: {}'.format(testcase_id, testset_id, re))






    def remove_testcasesfromtestset(self, testset_id, testcase_id):
        # querytestcase = 'TestCase.FormattedID = "%s"' % testcase_id
        # testcase = self.rally.get('TestCase', query=querytestcase, instance=True)
        #
        #
        # testcasesList = []
        # testcasesList.append(testcase.next())
        # self.rally.dropCollectionItems(self._get_entity_by_id(testset_id), testcasesList)
        # logger.info('remove testcase {} from testset {}'.format(testcase.FormattedID, testset_id))
        entity = self._get_entity_by_id(testset_id)
        testcasesList = []
        testcase = self.get_testcase_by_id(testcase_id)
        testcasesList.append(testcase)

        try :
            self.rally.dropCollectionItems(entity, testcasesList)
            logger.info('remove testcase {} from testset {}'.format(testcase.FormattedID, testset_id))
        except Exception as re :
            logger.error('Fail to remove test case {} from test set {}: {}'.format(testcase.FormattedID, re))

    def remove_testset(self, testset_id, osList):
        # querytestcase = 'TestCase.FormattedID = "%s"' % testcase_id
        # testcase = self.rally.get('TestCase', query=querytestcase, instance=True)
        #
        #
        # testcasesList = []
        # testcasesList.append(testcase.next())
        # self.rally.dropCollectionItems(self._get_entity_by_id(testset_id), testcasesList)
        # logger.info('remove testcase {} from testset {}'.format(testcase.FormattedID, testset_id))
        entity = self._get_entity_by_id(testset_id)
        list = entity.Name.split('|')
        if list[1] not in osList:
            self.rally.delete("TestSet", entity.oid)
            logger.info('remove testset {}'.format(testset_id))
        # testcasesList = []
        # testcase = self.get_testcase_by_id(testcase_id)
        # testcasesList.append(testcase)
        #
        # try :
        #     self.rally.dropCollectionItems(entity, testcasesList)
        #     logger.info('remove testcase {} from testset {}'.format(testcase.FormattedID, testset_id))
        # except Exception as re :
        #     logger.error('Fail to remove test case {} from test set {}: {}'.format(testcase.FormattedID, re))


    # def add_testresult(self, testcase_id, **info):
    #     logger.info('adding test result to {}'.format(testcase_id))
    #     info['TestCase'] = self.get_testcase_by_id(testcase_id).ref
    #     if not info.has_key('date'):
    #         info['date'] = str(datetime.datetime.utcnow().isoformat())
    #     if not info.has_key('tester'):
    #         info['tester'] = self.get_testcase_by_id(testcase_id).Owner.ref
    #     if not info.has_key('Verdict'):
    #         info['Verdict'] = 'Unexecuted'
    #     if not info.has_key('c_ProductionRelease'):
    #         info['c_ProductionRelease'] = '11.1.2 [2019-Jun-7]'
    #     if not info.has_key('Build'):
    #         info['Build'] = '0.0.0.0'
    #     if not info.has_key('note'):
    #         info['Notes'] = 'this result was added by script automatically'
    #
    #     self.rally.create('TestCaseResult', info)

    def _get_all_tags(self):
        response = self.rally.get('Tag', fetch="true", order="Name", server_ping=False, isolated_workspace=True)
        return [tag for tag in response]

    def _get_tag_by_name(self, tag_name):
        query = 'Name = "{}"'.format(tag_name)
        response = self.rally.get('Tag', fetch="true", query=query, server_ping=False, isolated_workspace=True)
        if response.resultCount != 0:
            tag = response.next()
            logger.debug('find tag {}'.format(tag.Name))
            return tag
        else:
            logger.error('can not find Tag with name {}'.format(tag_name))

    def get_tags_by_names(self, *tag_names):
        tags = []
        for tag_name in tag_names:
            tags.append(self._get_tag_by_name(tag_name))

        return tags

    def get_all_tag_names(self):
        return [tag.Name for tag in self._get_all_tags()]

    def create_tag(self, tag_name):
        tag_json = {'Name': tag_name}
        tag = self.rally.create('Tag', tag_json)
        return tag

    # somehow is not working
    def del_tag_by_name(self, tag_name):

        tag = self.get_tag_by_name(tag_name)
        self.rally.delete('Tag', itemIdent=self._get_tag_by_name(tag_name).oid)

    def remove_tags_from_testcase(self, testcase_id, tags):
        self.rally.dropCollectionItems(self.get_testcase_by_id(testcase_id), self.get_tags_by_names(tags))

    # archive tag will hide the tag from drop down list on rally, it is working..
    def archive_tag(self, tag_name):
        tag = self.get_tag_by_name(tag_name)
        info = {"ObjectID": tag.oid, "Archived": True}
        self.rally.update('Tag', info)

    def add_tags_to_entity(self, entity_id, *tag_names):
        entity = self._get_entity_by_id(entity_id)

        tags = []
        for tag_name in tag_names:
            tags.append(self._get_tag_by_name(tag_name))

        logger.info('adding tags {} to {}'.format(tag_names, entity_id))
        self.rally.addCollectionItems(entity, tags)

    def _get_entity_type(self, entity_id):
        if entity_id.startswith('TC'):
            entity_type = 'TestCase'
        elif entity_id.startswith('US'):
            entity_type = 'UserStory'
        elif entity_id.startswith('DE'):
            entity_type = 'Defect'
        elif entity_id.startswith('TS'):
            entity_type = 'TestSet'
        elif entity_id.startswith('TF'):
            entity_type = 'TestFolder'

        return entity_type

    def _update_entity(self, entity_id, **info):
        entity_type = self._get_entity_type(entity_id)
        info['FormattedID'] = entity_id
        logger.debug('{},{}'.format(entity_type, info))
        self.rally.update(entity_type, info)

    # def update_defect(self, entity_id, **info):
    #     self._update_entity(entity_id = entity_id, info=info)

    def active_testcase(self, testcase_id):
        self._update_entity(testcase_id, c_TestCaseStatus='Active')

    def active_all_testcases_in_testfolder(self, testfolder_id):
        for item in self.get_testcases_from_testfolder(testfolder_id=testfolder_id):
            logger.info('activing test case {} {}'.format(item.FormattedID, item.Name))
            self.active_testcase(item.FormattedID)

    def set_testcase_type(self, testcase_id, testcase_type):
        self._update_entity(testcase_id, Type=testcase_type)

    def update_testcase_owner(self, testcase_id, owner):
        tc = self.get_testcase_by_id(testcase_id)
        self.testCasefields = {}
        self.testCasefields['ObjectID'] = tc.oid
        self.testCasefields['Owner'] = self.get_user_ref_by_owner(owner)
        try:
            response = self.rally.update('TestCase', self.testCasefields)
            logger.info('Owner for test case {} now become {}'.format(tc.FormattedID, response.Owner.Name))
        except Exception as re:
            logger.error('Fail to update test case {}, {}'.format(tc.FormattedID, re.message))

    def update_testcase_project(self, testcase_id):
        tc = self.get_testcase_by_id(testcase_id)
        self.testCasefields = {}
        self.testCasefields['ObjectID'] = tc.oid
        self.testCasefields['Project'] = self.rally.getProject().ref
        try:
            response = self.rally.update('TestCase', self.testCasefields)
            logger.info('Project for test case {} now become {}'.format(tc.FormattedID, response.Project.Name))
        except Exception as re:
            logger.error('Fail to update test case {}, {}'.format(tc.FormattedID, re.message))

    def update_testcase_status(self, testcase_id, testcase_status):
        tc = self.get_testcase_by_id(testcase_id)
        self.testCasefields = {}
        self.testCasefields['ObjectID'] = tc.oid
        self.testCasefields['c_TestCaseStatus'] = testcase_status
        try:
            response = self.rally.update('TestCase', self.testCasefields)
            logger.info('test case for test case {} now become {}'.format(tc.FormattedID, response.c_TestCaseStatus))
        except Exception as re:
            logger.error('Fail to update test case {}, {}'.format(tc.FormattedID, re.message))

    def update_testset_name(self, testset_id, oldrelease, newrelease):
        ts = self.get_testcase_by_id(testset_id)
        self.testSetfields = {}
        self.testSetfields['ObjectID'] = ts.oid

        self.testSetfields['Name'] = ts.Name.replace(oldrelease, newrelease)
        try:
            response = self.rally.update('TestSet', self.testSetfields)
            logger.info('test set for test set {} now become {}'.format(ts.FormattedID, response.Name))
        except Exception as re:
            logger.error('Fail to update test set {}, {}'.format(ts.FormattedID, re.message))

    def get_user_ref_by_owner(self, owner):
        owner = owner.split('@')[0] if '@' in owner else owner
        return self.rally.getUserInfo(
            username=('%s@microstrategy.com' % owner))[0].ref

    def get_discussion(self, entity_id):
        entity = elf._get_entity_by_id(entity_id)
        discussion_context = []
        if hasattr(entity, '__collection_ref_for_Discussion'):
            discussion_url = entity.__collection_ref_for_Discussion
            content = json.loads(ralutil.rally.session.get(discussion_url).content)
            for post in content['QueryResult']['Results']:
                discussion_context.append(post)
        else:
            logger.error('{} has no discussion'.format(entity_id))
            return

    def get_testsets(self):
        query = 'c_ProductionRelease = "11.2 EA [2019-Jun-21]"'
        testsets = self.rally.get('TestSet', query=query, instance=True)
        for testset in testsets:
            print(testset.Name)

    def add_teststeps_to_testcase(self, testcase_id, inputs, expect_results):
        testcase = self.get_testset_by_id(testcase_id)

        if len(inputs) != len(expect_results):
            logger.warning('your input# is not match your expect# {}/{}'.format(len(inputs), len(expect_results)))
        if len(inputs) <= len(expect_results):
            index = len(inputs)
        else:
            index = len(expect_results)
        for i in range(index):
            Step = {'StepIndex': i + 1}
            Step['Input'] = inputs[i]
            Step['ExpectedResult'] = expect_results[i]
            Step['TestCase'] = testcase.ref
            logger.debug(Step)
            self.rally.create('TestCaseStep', Step)

    def add_discussion_to_testcase(self, testcase_id, **info):
        querytestcase = 'TestCase.FormattedID = "%s"' % testcase_id
        testcaseDiscussion = self.rally.get('ConversationPost', query=querytestcase, instance=True)
        testcase = self.get_testcase_by_id(testcase_id)
        queryuser = 'DisplayName = "%s"' % info['User']
        user = self.rally.get('User', fetch=True, query=queryuser, instance=True)

        info["User"] = user.ref
        info['Artifact'] = testcase.ref
        # info['_type']     = "ConversationPost"

        self.rally.create('ConversationPost', info)




    def clean_teststeps_on_testcase(self, testcase_id):
        testcase = self.get_testset_by_id(testcase_id)

        for step in testcase.Steps:
            self.rally.delete('TestCaseStep', step.oid)


if __name__ == '__main__':
    # config = ConfigParser.ConfigParser()
    config = configparser.ConfigParser()
    config.read('config.ini')

    ralutil = RallyUtil(RallyServer=config.get('rally', 'server'), \
                        APIKep=config.get('rally', 'token'), \
                        workspace=config.get('rally', 'workspace'), \
                        loggingfile=config.get('rally', 'log'))

    defects = ralutil.get_defects_with_query('')
    for defect in defects:
        if not defect.Release:
            continue
        # print(defect.Release.__dict__)
        if defect.Release.Name == 'MicroStrategy Q2 Release 2019':
            # if not defect.c_MSTRProduct:
            #     print('{} {} {}'.format(defect.FormattedID, defect.Release.Name, defect.Name))
            #     ralutil.set_defect(defect.FormattedID, c_MSTRProduct='Intelligence Server')
            if not defect.c_UCProduct:
                print('{} {} {}'.format(defect.FormattedID, defect.Release.Name, defect.Name))
                ralutil.set_defect(defect.FormattedID, c_UCProduct='U 221 Intelligence')

    print("enter")

# if __name__=='__main__':
#     config = ConfigParser.ConfigParser()
#     config.read('config.ini')
#
#     ralutil = RallyUtil(RallyServer=config.get('rally','server'),\
#                         APIKep=config.get('rally','token'),\
#                         workspace= config.get('rally','workspace'),\
#                         loggingfile=config.get('rally','log'))
#
#
#     # print ralutil.rally.session.get('https://rally1.rallydev.com/slm/webservice/v2.0/Defect/29464641098/Discussion').content
#     #
#     # import requests
#     # headers = {'ZSESSIONID':config.get('rally','token')}
#     # print requests.get('https://rally1.rallydev.com/slm/webservice/v2.0/Defect/29464641098/Discussion', headers=headers).content
#
#     import re
#     pattern = '[0-9]+.[0-9]+.[0-9]+.[0-9]+'
#     defects = ralutil.get_defects_with_query('Resolution = "None" AND c_NumberofTSCases > 0')
#     logger.info('found {} defects '.format(len(defects)))
#
#     for defect in defects:
#         if hasattr(defect, '__collection_ref_for_Discussion'):
#             discussion_url = defect.__collection_ref_for_Discussion
#         else:
#             logger.warning('{} has no discussion'.format(defect.FormattedID))
#             continue
#         content = json.loads(ralutil.rally.session.get(discussion_url).content)
#         # for post in content['QueryResult']['Results']:
#         #     if 'fc in ' in post['Text'].lower() or 'fc on ' in post['Text'].lower() \
#         #         or 'fc with ' in post['Text'].lower() or 'fixed confirm ' in post['Text'].lower()\
#         #             or 'fix confirm' in post['Text'].lower() :
#         #
#         #         reg= re.compile(pattern)
#         #         res = reg.findall(post['Text'])
#         #         build = ''
#         #         if len(res):
#         #             build = res[0]
#         #             ralutil.set_defect(defect.FormattedID, FixedInBuild=build, Resolution='Fixed')
#         #
#         #         logger.info('{} | {} |{}'.format(defect.FormattedID,build, post['Text']))
#         #
#         #         continue
#
#         for post in content['QueryResult']['Results']:
#             #if 'not reproduc' in post['Text'].lower():
#             if 'changes made into build' in post['Text'].lower():
#
#                     #ralutil.set_defect(defect.FormattedID, FixedInBuild=build, Resolution='Fixed')
#
#                 logger.info('{} |{}'.format(defect.FormattedID, post['Text']))
#                 reg= re.compile(pattern)
#                 res = reg.findall(post['Text'])
#                 build = ''
#                 if len(res):
#                     build = res[0]
#                     ralutil.set_defect(defect.FormattedID, FixedInBuild=build, Resolution='Fixed')
#                 break
#
#
#
#         #print '{}|{}|{}|{}'.format(defect.FixedInBuild, defect.Resolution, defect.FormattedID, defect.Name)
#
#
#     #ralutil.clean_teststeps_on_testcase('TC35406')
#     # inputs=[]
#     # rest=[]
#     # for i in range(10):
#     #     inputs.append('<b>input {}</b>'.format(i))
#     #     rest.append('<h1>res {}</h1>'.format(i))
#     # ralutil.add_teststeps_to_testcase('TC35406', inputs, rest)
#
#
#
#
#
#
#
#     #print ralutil.get_defect_by_id('DE124394').__dict__
#     # query = 'Resolution = None AND c_ProductionRelease = "11.2 EA [2019-Jun-21]" AND State = "Closed"'
#     # for defect in ralutil.get_defects_with_query(query=query):
#     #     ralutil.update_entity(entity_id=defect.FormattedID, Resolution='Fixed')
#
#
#         #print '{} | {} | {}'.format(defect.FormattedID, defect.Name, defect.Project.Name)
#     # for testcase in ralutil.get_testcases_from_testfolder('TF6293'):
#     #
#     #
#     #     testcase_name = testcase.Name.encode('utf-8')
#     #     logger.info('checking {} | {}'.format(testcase.FormattedID, testcase_name))
#     #     if '[REG]' in testcase_name:
#     #         testcase_name = testcase_name.replace('[REG]','')
#     #         ralutil.set_testcase_name(testcase.FormattedID, testcase_name)
#         #ralutil.add_tags_to_entity(testcase.FormattedID, 'RC')
#         # if 'GUI' in testcase_name:
#         #     ralutil.set_testcase_type(testcase.FormattedID, 'Acceptance')
#         # elif 'Functionality' in testcase_name:
#         #     ralutil.set_testcase_type(testcase.FormattedID, 'End to End Test')
#     #ralutil.add_testresult('TC35172')
#     # testset= ralutil.get_testset_by_id('TS26212')
#     # for task in testset.Tasks:
#     #     print task
#     # for testcase in testset.TestCases:
#     #     print testcase
#     #ralutil.get_testsets()
#
#
#
#     # for item in ralutil.get_testcases_from_testfolder('TF6032'):
#     #     ralutil.add_tags_to_entity(item.FormattedID, 'Command Manager')
#     #ralutil.active_all_testcases_in_testfolder('TF6032')





