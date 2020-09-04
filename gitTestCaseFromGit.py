from github import Github, UnknownObjectException
import re, base64, traceback, logging, time
import configparser, copy

##########################
### modify as you need ###
##########################


def get_file_from_git(branch, aba, user, pwd, GITHUB_URL):
    try:
        g = Github(base_url = GITHUB_URL, login_or_token = user, password = pwd)
        repo = g.get_repo('Tech/Yati')
        try:
            contents = repo.get_contents('Tests/Functionality/'+aba+'/scenario_class.yml', branch)
        except UnknownObjectException as e:
            if e.status == 404:
                logging.error(f"{aba} doesn't have file \"scenario_class.yml\"")
            return
        return(contents.content)
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

def get_aba_tc_list(branch, aba_list, levels, user, pwd, GITHUB_URL):
    abawithoutscenario = []
    listvar = []
    result = dict()
    for aba in aba_list:
        print('------ %s --- %s ------' % (branch, aba))
        result[aba] = parse_file(get_file_from_git(branch, aba, user, pwd, GITHUB_URL), levels)

        if result[aba] is None:
            abawithoutscenario.append(aba)
        else :
            for key in result[aba]:
                print("{:15}: {} {}".format(key, len(result[aba][key]), result[aba][key]))
                listvar = listvar + result[aba][key]

                # if listvar is None:
                #     listvar = copy.copy(set(result[aba][key]))
                # else:
                #     listvar = listvar.update(result[aba][key])
                # if key == 'Acceptance':
                #     sum += len(result[aba][key])
    print(set(listvar))
    print(len(set(listvar)))
    print(abawithoutscenario)
    # return result
    return set(listvar)


def parsestringtolist(str):

    str = re.sub('[\[\]\']', '', str)

    return str.split(',')

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s.%(msecs)03d - %(name)s  [%(levelname)s] [%(threadName)s] %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        filename='process.log',
                        filemode='w')

    config = configparser.ConfigParser()
    config.read('config.ini')
    branch = config['testInfOnGit']['branch']
    aba_list = parsestringtolist(config['testInfOnGit']['aba_list'])
    levels = parsestringtolist(config['testInfOnGit']['levels'])
    GIT_USER = config['testInfOnGit']['GIT_USER']
    GIT_PWD = config['testInfOnGit']['GIT_PWD']
    GITHUB_URL = config['testInfOnGit']['GITHUB_URL']



    result = get_aba_tc_list(branch, aba_list, levels, GIT_USER, GIT_PWD, GITHUB_URL)
    # logging.info(f"{len}")
