import configparser
import os
import random
import re
import datetime

cfg = configparser.ConfigParser()
cfg.read('./config/config.ini')
llvmDisPath = cfg.get('llvm-main', 'LLVM_DIS_15')
seedPoolPath = cfg.get('llvm-main', 'SEED_POOL_PATH')
llvmBugsPath = cfg.get('llvm-main', 'llvm_bugs_path')
helpIRsPath = cfg.get('llvm-main', 'HELP_IRS_PATH')
irCovsPath = cfg.get('llvm-main', 'IR_COVS_PATH')
tempSeedsPoolPath = cfg.get('llvm-main', 'TEMP_SEEDS_POOL_PATH')
llvmVersionsPathPre = cfg.get('llvm-main', 'LLVM_VERSIONS_PATH_PRE')
numLLVMPre = f'{llvmVersionsPathPre}/llvm-versions'


class Scope:
    def __init__(self, f1=0, f2=0, b1=0, b2=0, i1=0, i2=0):
        self.f1 = int(f1)
        self.f2 = int(f2)
        self.b1 = int(b1)
        self.b2 = int(b2)
        self.i1 = int(i1)
        self.i2 = int(i2)

    def __eq__(self, o):
        return self.i1 == o.i1 and self.i2 == o.i2 and self.b1 == o.b1 and self.b2 == o.b2 and self.f1 == o.f1 and self.f2 == o.f2

    def __hash__(self):
        return hash((self.i1, self.i2, self.b1, self.b2, self.f1, self.f2))

    def __str__(self):
        return f"f[{self.f1}, {self.f2}] b[{self.b1}, {self.b2}] i[{self.i1}, {self.i2}]"


class StrategyScope:
    def __init__(self, s, num):
        self.NAMES = {1: "insert", 3: "modify"}
        self.s = s
        self.num = num

    def __eq__(self, o):
        return self.s == o.s and self.num == o.num

    def __hash__(self):
        return hash((self.s, self.num))

    def __str__(self):
        try:
            return f"operator {self.num}: -scope {str(self.s)}"
        except KeyError:
            print(f"StrategyScope __str__ ERROR: num-type-> {type(self.num)}")
            return f"operator {self.num}"


class StrategyScopePool:
    def __init__(self):
        self.sumWeight = 0.0
        self.ss = []  
        self.weights = []  
        

    def printAll(self, label):  
        print(f'label => {label}')
        print('-------------------------------------------------------------------------')
        for i in range(len(self.ss)):
            print(f'|-- num: {self.ss[i].num}, {self.ss[i].s}, {self.weights[i]} --|')
        print('-------------------------------------------------------------------------')


    def addStrategy(self, num, s, weight):
        self.ss.append(StrategyScope(s, num))  
        self.weights.append(weight)
        self.sumWeight += weight
        return len(self.ss) - 1

    def getStrategy(self, index):
        return self.ss[index]

    def getWeight(self, index):
        return self.weights[index]
    
    def randStrategy(self):
        op = random.uniform(0, self.sumWeight)
        l = len(self.weights)
        t = 0
        for i in range(l):
            t += self.weights[i]
            if op <= t:
                return (self.ss[i], i)  

    def getMinWeight(self):
        return min(self.weights)

    def addWeight(self, index, weight):
        self.weights[index] += weight
        self.sumWeight += weight

    def existSameStrategyScope(self, nss):
        for i in range(len(self.ss)):
            if self.ss[i] == nss:
                return i
        return False


def execIR(irPath: str, opt: str, exeName: str, branch: str):  
    pwd = os.getcwd()
    branchPre = f'{numLLVMPre}/{branch}'
    binPath = f'{numLLVMPre}/{branch}/bin'
    if exeName == 'llc':
        os.system(f"{llvmDisPath} {irPath} -o {irPath}.ll")
        os.system(f"{binPath}/llc {opt} {irPath}.ll -o {irPath}.s")  
        os.system(f"{binPath}/clang -no-pie {irPath}.s -o {irPath}.exe")  
        wfp = f"{pwd}/judgeExecRes"
        exeExitCode = os.system(f"timeout 6s {irPath}.exe > {wfp}")
        wf = open(wfp, 'r')
        ret = wf.read()
        wf.close()
        os.system(f"rm -f {irPath}.ll")
        os.system(f"rm -f {irPath}.s")
        os.system(f"rm -f {irPath}.exe")
        os.system(f"rm -f {wfp}")
    elif exeName == 'opt':
        os.system(f"{llvmDisPath} {irPath} -o {irPath}.ll")
        optRet = os.system(f"{binPath}/opt {opt} -S {irPath}.ll -o {irPath}.opt.ll 2> /dev/null")
        if optRet != 0:  
            os.system(f"rm -f {irPath}.ll")
            if os.path.exists(f'{irPath}.opt.ll'):
                os.system(f"{irPath}.opt.ll")
            return False
        wfp = f"{pwd}/judgeExecRes"
        exeExitCode = os.system(f"timeout 6s {binPath}/lli {irPath}.opt.ll > {wfp} 2> /dev/null")
        wf = open(wfp, 'r')
        ret = wf.read()
        wf.close()
        os.system(f"rm -f {irPath}.ll")
        os.system(f"rm -f {irPath}.opt.ll")
        os.system(f"rm -f {wfp}")
    if exeExitCode != 0:  
        return (False, exeExitCode)  
    else:
        return (True, str(ret).strip())  


def judgeExecRes(branch, irPath: str, failOpt: str, compOpt: str, failType, exeName, isMinimizing=False) -> str:  
    failOut = execIR(irPath, failOpt, exeName, branch)
    compOut = execIR(irPath, compOpt, exeName, branch)
    if compOut == False or failOut == False:
        print(f"judgeExecRes False !!!")
        return False
    for i in range(5):  
        if compOut != execIR(irPath, compOpt, exeName, branch):
            return False
    ret = 'pass'
    if isMinimizing:
        failRandValueJudge = False
        if compOut == (failType[0], failType[1]) and (failOut == (failType[2], failType[3]) or failRandValueJudge):
            return 'fail'
        elif compOut == failOut and compOut == (failType[0], failType[1]):
            return 'pass'
        else:
            return False
    loopCnt = 0
    beginCheckTime = 0
    while True:
        loopCnt += 1
        if loopCnt == 2:
            failOut = execIR(irPath, failOpt, exeName, branch)
            compOut = execIR(irPath, compOpt, exeName, branch)
        
        if failType[0] == True and failType[2] == True:
            if failOut[0] == True and compOut[0] == True and failOut[1] == compOut[1] \
                and (str(failOut[1]).strip() != ''):  
                ret = 'pass'
            elif failOut[0] == True and compOut[0] == True and failOut[1] != compOut[1] \
                and (str(compOut[1]).strip() != '' and ((str(failType[3]).strip() != '') == (str(failOut[1]).strip() != ''))):  
                ret = 'fail'
            else:
                ret = False
        elif failType[0] == True and failType[2] == False:
            if failOut[0] == True and compOut[0] == True and failOut[1] == compOut[1]:
                ret = 'pass'
            elif compOut[0] == True and failOut[0] == False and failOut[1] == failType[3]:
                ret = 'fail'
            else:
                ret = False
        else:
            print(f"failType => {failType}")
            print('judgeExecRes ERROR !!!')
            exit(114)
        if loopCnt == 2 or (loopCnt == 1 and ret != 'fail'):  
            break
        else:
            return False
    if loopCnt == 2 and ret == 'pass':
        ret = False
    return ret


def judgeIREqual(irPath1: str, irPath2: str) -> bool:
    os.system(f"{llvmDisPath} {irPath1} -o {irPath1}.ll")
    os.system(f"{llvmDisPath} {irPath2} -o {irPath2}.ll")
    os.system(f"diff {irPath1}.ll {irPath2}.ll > {irPath1}.diff")
    f = open(f'{irPath1}.diff', 'r')
    lines = f.readlines()
    f.close()
    os.system(f"rm -f {irPath1}.ll {irPath2}.ll {irPath1}.diff")
    if len(lines) == 0:
        return True
    if len(lines) <= 4 and str(lines[1]).find('ModuleID') != -1 and str(lines[2]).find('---') != -1 and str(lines[3]).find("ModuleID") != -1:
        return True
    return False


def haveSameIR(nsp: str):
    seedsPath = [f"{str(seedPoolPath)}/{x}" for x in os.listdir(seedPoolPath)]
    seedsPath += [f"{str(helpIRsPath)}/{x}" for x in os.listdir(helpIRsPath)]
    seedsPath += [f"{str(tempSeedsPoolPath)}/{x}" for x in os.listdir(tempSeedsPoolPath) if f"{str(tempSeedsPoolPath)}/{x}" != str(nsp)]
    for s in seedsPath:
        if judgeIREqual(nsp, str(s)):
            return True
    return False


def parseRealMutateScopeFile(path: str) -> dict:  
    f = open(path, 'r')
    lines = f.readlines()
    f.close()
    dic = {}
    for l in lines:
        if 'writeRealMutateLoc: ' not in l:
            continue
        l = l.strip().split(' ')[1]
        if l.strip() != '':
            arg = l.split(':')
            dic[arg[0].strip()] = int(arg[1].strip())
    return dic  

def collect_one_cov_dir_big(workdir, stmtfilename, covdir, gcov_path, testObj_path, options, ir_path, collectfiles={}):
    gcov_11_path = '/usr/bin/gcov'
    gcov_13_path = 'gcov'
    oridir = os.getcwd()
    os.chdir(workdir)  
    stmtfile = open(stmtfilename, 'w')  
    os.system("find . -name \"*.gcda\" -exec rm -f {} \\;")
    os.system(f"{llvmDisPath} {ir_path} -o {ir_path}.ll")
    os.system(f'{testObj_path} {options} {ir_path}.ll > exec.log 2>&1')
    testObj = testObj_path.strip().split('/')[-1]
    if testObj == 'llc':
        os.system(f'rm -f {ir_path}.s')  
    os.system(f'rm -f {ir_path}.ll')  
    if os.path.exists('gcdalist'):
        os.system('rm gcdalist')
    os.system(f'find {covdir} -name \"*.gcda\" > gcdalist')  
    f = open('gcdalist')
    lines = f.readlines()
    f.close()
    for i in range(len(lines)):  
        gcdafile = lines[i].strip()  
        cov_file_name_ori = gcdafile.split('.gcda')[0]  
        dir_names = cov_file_name_ori.split('/')
        cov_file_name = ''
        for i in range(0, len(dir_names)):  
            if dir_names[i] != 'CMakeFiles' and not '.dir' in dir_names[i] and dir_names[i] != '':
                cov_file_name += dir_names[i]
                cov_file_name += '/'
        cov_file_name = cov_file_name[:-1]  
        if '/clang/test/' in gcdafile:
            continue
        
        if collectfiles != {}:  
            if cov_file_name not in collectfiles:
                continue
        os.system('rm *.gcov')  
        os.system(f'{gcov_path} {gcdafile} > gcovfile 2>&1')
        gcovfile_name = gcdafile.strip().split('/')[-1].split('.gcda')[0] + '.gcov'  
        if not os.path.exists(gcovfile_name):  
            continue
        f = open(gcovfile_name)
        stmtlines = f.readlines()
        f.close()
        tmp = []
        for j in range(len(stmtlines)):
            if stmtlines[j] == '------------------\n':
                continue
            covcnt = stmtlines[j].strip().split(':')[0].strip()  
            linenum = stmtlines[j].strip().split(':')[1].strip()  
            if covcnt != '-' and covcnt != '#####' and linenum != '':
                tmp.append(linenum)  
        s = set()
        for lineno in tmp:
            toWrite = cov_file_name + ':' + lineno + '\n'
            if toWrite not in s:
                s.add(toWrite)
                stmtfile.write(toWrite)  
    stmtfile.close()
    os.system('rm *.gcov')  
    os.chdir(oridir)  


def ochiai(t):  
    ef = t[0]
    nf = t[1]
    ep = t[2]
    np = t[3]
    t1 = 0
    if ((ef + nf) * (ef + ep)) != 0:  
        t1 = ef / (((ef + nf) * (ef + ep))**0.5)
    return t1


def getClusterDiv(covFilePathList: list, ORIPath: str):  
    clusters = {}  
    mid = {}  
    passCnt = 0  
    ORI = set()
    ORIFile = open(ORIPath, 'r')
    for ol in ORIFile.readlines():
        ORI.add(ol.strip())
    ORIFile.close()
    for cf in covFilePathList:
        delta = 0
        if str(cf).strip().split('/')[-1].find('pass') != -1:
            delta = 1  
            passCnt += 1
        f = open(cf, 'r')
        lines = f.readlines()  
        f.close()
        for line in lines:
            l = line.strip()
            if l not in ORI:  
                continue
            if l not in mid:
                mid[l] = (1 - delta, 0, delta, 0)
            else:
                mid[l] = (mid[l][0] + 1 - delta, 0, mid[l][2] + delta, 0)
    for k in mid:
        t = mid[k]
        if t not in clusters:
            clusters[t] = [k]
        else:
            clusters[t].append(k)
    allTestCnt = len(covFilePathList)
    retClusters = {}
    for k in clusters:
        nt = (k[0], allTestCnt - passCnt - k[0], k[2], passCnt - k[2])
        retClusters[nt] = clusters[k].copy()
    return retClusters  


def calSeedScore(seedPath: str, clusters: dict):  
    seedCovName = seedPath.strip().split('/')[-1] + '.ir_cov'
    covPath = tempSeedsPoolPath + '/' + seedCovName
    ncf = open(covPath, 'r')
    ncfLines = ncf.readlines()
    ncf.close()
    clustersDiv = {}  
    for k in clusters:  
        if k not in clustersDiv:
            clustersDiv[k] = 0
        for nl in ncfLines:
            l = nl.strip()  
            if l in clusters[k]:  
                clustersDiv[k] += 1
    score = 0.0
    for k in clustersDiv:
        covCnt = clustersDiv[k]
        unCovCnt = len(clusters[k]) - covCnt
        div = min(covCnt, unCovCnt)
        weight = ochiai(k)
        score += (div * weight)
    return score


def calFailSeedCnt():  
    cnt = 0
    for f in os.listdir(irCovsPath):
        if str(f).find('fail') != -1:
            cnt += 1
    return cnt


def get1FailType(branch: str, testObj: str, failOpt: str, compOpt: str, failPath=f"{seedPoolPath}/1.fail"):
    binPath = f'{numLLVMPre}/{branch}/bin'
    if testObj == 'llc':
        os.system(f"{llvmDisPath} {failPath} -o {failPath}.ll")
        os.system(f"{binPath}/llc {compOpt} {failPath}.ll -o {failPath}.comp.s")  
        os.system(f"{binPath}/llc {failOpt} {failPath}.ll -o {failPath}.fail.s")
        os.system(f"{binPath}/clang -no-pie {failPath}.comp.s -o {failPath}.comp.exe")  
        os.system(f"{binPath}/clang -no-pie {failPath}.fail.s -o {failPath}.fail.exe")  
        compCode = os.system(f"timeout 4s {failPath}.comp.exe > {failPath}.comp.out 2> /dev/null")
        failCode = os.system(f"timeout 4s {failPath}.fail.exe > {failPath}.fail.out 2> /dev/null")
        ret = (True, 0, True, 0)
        if compCode != 0:
            ret = (False, compCode, ret[2], ret[3])
        else:
            compF = open(f"{failPath}.comp.out", 'r')
            ret = (ret[0], str(compF.read()).strip(), ret[2], ret[3])
            compF.close()
        if failCode != 0:
            ret = (ret[0], ret[1], False, failCode)
        else:
            failF = open(f"{failPath}.fail.out", 'r')
            ret = (ret[0], ret[1], ret[2], str(failF.read()).strip())
            failF.close()
        os.system(f"rm -f {failPath}.ll")
        os.system(f"rm -f {failPath}.comp.s")
        os.system(f"rm -f {failPath}.fail.s")
        os.system(f"rm -f {failPath}.comp.exe")
        os.system(f"rm -f {failPath}.fail.exe")
        os.system(f"rm -f {failPath}.comp.out")
        os.system(f"rm -f {failPath}.fail.out")
        return ret
    elif testObj == 'opt':
        os.system(f"{llvmDisPath} {failPath} -o {failPath}.ll")
        os.system(f"{binPath}/opt {compOpt} -S {failPath}.ll -o {failPath}.ll.comp 2> /dev/null")
        os.system(f"{binPath}/opt {failOpt} -S {failPath}.ll -o {failPath}.ll.fail 2> /dev/null")
        compCode = os.system(f"timeout 10s {binPath}/lli {failPath}.ll.comp > {failPath}.comp.out 2> /dev/null")
        failCode = os.system(f"timeout 10s {binPath}/lli {failPath}.ll.fail > {failPath}.fail.out 2> /dev/null")
        ret = (True, 0, True, 0)
        if compCode != 0:
            ret = (False, compCode, ret[2], ret[3])
        else:
            compF = open(f"{failPath}.comp.out", 'r')
            ret = (ret[0], str(compF.read()).strip(), ret[2], ret[3])
            compF.close()
        if failCode != 0:
            ret = (ret[0], ret[1], False, failCode)
        else:
            failF = open(f"{failPath}.fail.out", 'r')
            ret = (ret[0], ret[1], ret[2], str(failF.read()).strip())
            failF.close()
        os.system(f"rm -f {failPath}.ll")
        os.system(f"rm -f {failPath}.ll.comp")
        os.system(f"rm -f {failPath}.ll.fail")
        os.system(f"rm -f {failPath}.comp.out")
        os.system(f"rm -f {failPath}.fail.out")
        return ret


def calFileSuspicion(statementScore: list):  
    statementScore.sort(reverse=True)  
    n = len(statementScore)
    avg = 0.0
    k = 2.0
    oriWS = [1 / ((i + 1) ** k) for i in range(n)]
    x = sum(oriWS)
    ws = [w / x for w in oriWS]
    for i in range(n):
        w = ws[i]
        s = statementScore[i]
        avg += w * s
    return avg
    

def getSameList(LL: list) -> list:
    s = set(LL[0])
    for l in LL[1:]:
        s.intersection_update(l)
    return list(s)


def clearPassLine(pl: str) -> str:
        if pl.strip() == 'False':
            return 'False'
        pl = ''.join([f" {x}" for x in pl.split(' ')[4: ]]).strip()
        while pl != re.sub(r'\([^()]*\)', '', pl):  
            pl = str(re.sub(r'\([^()]*\)', '', pl)).strip()
        prepositions = [' at ', ' on ', ' in ']
        minIndex = len(pl)
        for p in prepositions:
            index = pl.find(p)
            if index != -1:
                minIndex = min(minIndex, index)
        pl = pl[0: minIndex].strip()
        pl = re.sub(r'Pass( |$)', ' ', pl)
        return re.sub(r'\s+', ' ', pl).strip()


def clearFilename(fn: str) -> str:
    filename = fn.strip().split('/')[-1]
    return re.sub(r'\.[^\.]*$', '', filename)


def calFilesRank(suspicionRankPath: str, allCovPath: list, oriCovPath0: str):
    ONLY_INTERSECTION = True  
    failFilePaths = [f for f in allCovPath if str(f).find('.fail') != -1]
    fileCnt = len(allCovPath)
    failFileCnt = len(failFilePaths)
    if os.path.exists(suspicionRankPath):
        os.system(f'rm -f {suspicionRankPath}')
    os.system(f'touch {suspicionRankPath}')
    oriCov = []
    if ONLY_INTERSECTION:
        failCovs = [] 
        for f in failFilePaths:
            with open(f, 'r') as F:
                failCovs.append(F.readlines())
        oriCov = getSameList(failCovs)
    else:
        oriCovPath = f"{irCovsPath}/1.fail.ir_cov"
        if oriCovPath0 != '':
            oriCovPath = oriCovPath0
        f = open(oriCovPath, 'r')
        oriCov = f.readlines()  
        f.close()
    dicOriCov = {}
    if ONLY_INTERSECTION:
        for o in oriCov:
            dicOriCov[o] = (failFileCnt, 0, 0, 0)
    else:
        for o in oriCov:
            dicOriCov[o] = (1, 0, 0, 0)
    for cov in allCovPath:  
        condition = False
        if ONLY_INTERSECTION:
            condition = (cov not in failFilePaths)
        else:
            condition = (str(cov).strip() != str(oriCovPath).strip())
        if condition:
            tf = open(cov, 'r')
            lines = tf.readlines()
            isFail = 1
            if str(cov).find('pass') != -1:
                isFail = 0
            for l in lines:
                if l in dicOriCov:  
                    dicOriCov[l] = (dicOriCov[l][0] + isFail, 0, dicOriCov[l][2] + 1 - isFail, 0)
    statementScoreEveryFile = {}
    for k in dicOriCov:
        dicOriCov[k] = (dicOriCov[k][0], failFileCnt - dicOriCov[k][0], dicOriCov[k][2], fileCnt - failFileCnt - dicOriCov[k][2])
        filename = str(k).strip().split(':')[-2]
        if filename not in statementScoreEveryFile:
            statementScoreEveryFile[filename] = []
        ret = ochiai(dicOriCov[k])
        statementScoreEveryFile[filename].append(ret)
    fileSuspicion = {}  
    for k in statementScoreEveryFile:
        fileSuspicion[k] = calFileSuspicion(statementScoreEveryFile[k])
    ranks = sorted(fileSuspicion.items(), key=lambda x: x[1], reverse=True)
    num = re.findall(r'[0-9]+/', oriCovPath0)[0].split('/')[0]  # TODO the logic of eval is regarded as a single module
    covFile = f"{llvmBugsPath}/{num}/bisect_bug_opt_pass.ir_cov"
    if os.path.exists(covFile):
        s = set()
        with open(covFile, 'r') as f:
            lines = f.readlines()
            for l in lines:
                s.add(l.strip().split(':')[0])
        l = list(s)
        ranks = [t for t in ranks if t[0].strip() in l]
    rf = open(suspicionRankPath, 'w')
    for i in range(len(ranks)):
        pre = str('%.8lf' % ranks[i][1])
        rf.write(pre + ' == ' + ranks[i][0] + '\n')
    rf.close()
