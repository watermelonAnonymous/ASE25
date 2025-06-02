import os
import configparser

from utils import calFilesRank

cfg = configparser.ConfigParser()
cfg.read('./config/config.ini')
expResultsPath = cfg.get('llvm-main', 'exp_results_path')
llvmBugsPath = cfg.get('llvm-main', 'LLVM_BUGS_PATH')

def parseLocationsFile(num) -> dict:
    locationsFilePath = f"{llvmBugsPath}/{num}/locations"
    f = open(locationsFilePath, 'r')
    lines = f.readlines()
    dic = {}
    for l in lines:
        t = l.strip()
        if t.find('locations') != -1:
            continue
        lst = t.split(':')
        if lst[0].strip() not in dic:
            if lst[0].strip() == 'fail opti level':
                dic[lst[0].strip()] = lst[1].strip().split('/')[0].strip()  
            else:
                dic[lst[0].strip()] = lst[1].strip()
        else:
            if str(type(dic[lst[0].strip()])) != "<class 'list'>":
                dic[lst[0].strip()] = [dic[lst[0].strip()]]
            dic[lst[0].strip()].append(lst[1].strip())
    opts = str(dic['fail opti level']).split(' ')
    dic['pre-opt-fail opti level'] = ''  
    dic['opt-fail opti level'] = ''  
    i = 0
    optSkipList = ['-mllvm', '-w', '-fno-inline']
    while i < (len(opts)):
        if opts[i] in optSkipList:
            i += 1
            continue
        dic['opt-fail opti level'] += str(opts[i]) + ' '  
        i += 1
    i = 0
    while i < (len(opts)):
        if opts[i] != '-mllvm':
            dic['pre-opt-fail opti level'] += str(opts[i])
            dic['pre-opt-fail opti level'] += ' '
        else:  
            i += 1
        i += 1
    dic['pre-opt-fail opti level'] = dic['pre-opt-fail opti level'].strip()
    dic['opt-fail opti level'] = dic['opt-fail opti level'].strip()
    return dic


def calRank(rankFilePath: str, bugNum):
    loc = parseLocationsFile(bugNum)
    bugFiles = []
    if not str(type(loc['file'])) == "<class 'list'>":
        bugFiles.append(loc['file'].strip().split(';')[0].split('/')[-1])
    else:
        for f in loc['file']:
            bugFiles.append(str(f).strip().split(';')[0].split('/')[-1])
    ranks = []
    lines: list
    with open(rankFilePath, 'r') as f:
        lines = f.readlines()
    for bugFile in bugFiles:
        ranks.append([(index + 1) for index in range(len(lines)) if lines[index].find(bugFile) != -1][0])
    for i in range(len(ranks)):
        rk = ranks[i]
        sameRankLines = []
        if ',' in lines[0] and False:
            sameRankLines = [x for x in lines if x.strip().split(',')[1] == lines[int(rk) - 1].strip().split(',')[1]]
        else:
            sameRankLines = [x for x in lines if x.split(' ')[0] == lines[int(rk) - 1].split(' ')[0]]
        cnt = len(sameRankLines)
        if cnt != 1:
            realRank = lines.index(sameRankLines[-1]) + 1  
            ranks[i] = realRank
    return ranks


topn = [0, 0, 0, 0, 0]
metrics = [1, 3, 5, 10, 20]
MFR = 0
MAR = 0
sumMFRRank = 0
sumMARRank = 0
numMFRCnt = 0
numMARCnt = 0
for num in os.listdir(expResultsPath):
    numResDirPath = f'{expResultsPath}/{num}'
    covsPath = f'{numResDirPath}/ir_covs'
    helpCovsPath = f'{numResDirPath}/help_ir_covs'
    
    covs = [f"{covsPath}/{x}" for x in os.listdir(covsPath)]
    covs += [f"{helpCovsPath}/{x}" for x in os.listdir(helpCovsPath)]

    numRankResPath = f'{numResDirPath}/rankRes'
    calFilesRank(numRankResPath, covs, f"{covsPath}/1.fail.ir_cov")
    res = calRank(numRankResPath, num)
    sumMFRRank += min(res)
    numMFRCnt += 1
    sumMARRank += sum(res)
    numMARCnt += len(res)
    for i in range(len(metrics)):
        if min(res) <= metrics[i]:
            while i <= 4:
                topn[i] += 1
                i += 1
            break
print(f"top-1/3/5/10/20: {topn}")
print(f"MFR: {sumMFRRank / numMFRCnt}; MAR: {sumMARRank / numMARCnt}")
