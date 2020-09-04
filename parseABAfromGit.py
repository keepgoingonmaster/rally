from github import Github, UnknownObjectException
import re, base64, traceback
import logging

##########################
### modify as you need ###
##########################
GITHUB_URL="https://github.microstrategy.com/api/v3"
GIT_USER = 'jinewang'
GIT_PWD = 'HUAhua@2020'
branch = 'm2021'
aba_list = ['T14.JobPriority',
            'T53.CubeServices_FT'
            ]
# levels = ['Regression']
levels = ['Acceptance', 'Regression']

def get_file_from_git(branch, aba, user, pwd):
    try:
        g = Github(base_url = GITHUB_URL, login_or_token = user, password = pwd)
        repo = g.get_repo('Tech/Yati')
        contents = None
        try:
            contents = repo.get_contents('Tests/Functionality/'+aba+'/scenario_class.yml', branch)
            return (contents.content)
        except UnknownObjectException as e:
            if e.status == 404:
                print("{}: {} doesn't have file {}".format(e.status, aba, "scenario_class.yml"))
            # print(str(e))
    except:
        print('ERROR when getting file from Github.\n'+traceback.format_exc())
        # return None

def parse_file(encoded_string, levels):
    if encoded_string != None:
        try:
            decoded = base64.b64decode(encoded_string).decode('utf-8')
            tc_list = dict()
            for level in levels:
                tc_list[level] = re.findall(r'%s:\s(TC\d+)'%level, decoded)
            return tc_list
        except:
            print('ERROR when parsing file content.\n'+traceback.format_exc())
    # return None

def get_aba_tc_list(branch, aba_list, levels, user, pwd):
    result = dict()
    for aba in aba_list:
        print('------ %s --- %s ------' % (branch, aba))
        result[aba] = parse_file(get_file_from_git(branch, aba, user, pwd), levels)
        print(result[aba])
    return result

if __name__ == '__main__':
    get_aba_tc_list(branch, aba_list, levels, GIT_USER, GIT_PWD)