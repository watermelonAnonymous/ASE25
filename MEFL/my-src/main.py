import os
import configparser
import random
import datetime
import sys
import time as TimeModule

from utils import collect_one_cov_dir_big, getClusterDiv, calSeedScore, Scope, StrategyScopePool, StrategyScope, \
    calFilesRank, judgeExecRes, judgeIREqual, haveSameIR, parseRealMutateScopeFile, calFailSeedCnt, get1FailType

expectedCnt = 6
if len(sys.argv) < expectedCnt or 'FEN_GE' not in sys.argv:
    print(f"main.py exec ERROR, at least {expectedCnt} args")
    exit(1)

cfg = configparser.ConfigParser()
cfg.read('./config/config.ini')
pool = StrategyScopePool() 
time = cfg.getint('llvm-main', 'MUTATE_TIME')
fuzzerPath = cfg.get('llvm-main', 'FUZZER_PATH')
seedPoolPath = cfg.get('llvm-main', 'SEED_POOL_PATH')
tempPoolPath = cfg.get('llvm-main', 'TEMP_SEEDS_POOL_PATH')
irCovsPath = cfg.get('llvm-main', 'IR_COVS_PATH')
helpIRCovsPath = cfg.get('llvm-main', 'HELP_IR_COVS_PATH')
helpIRsPath = cfg.get('llvm-main', 'HELP_IRS_PATH')
llvmVersionsPathPre = cfg.get('llvm-main', 'LLVM_VERSIONS_PATH_PRE')
realMutateLocPath =  cfg.get('llvm-main', 'REAL_MUTATE_LOC')
testObj = 'llc'
testObjPath = ''
branch = sys.argv[1]
numBranchPre = f"{llvmVersionsPathPre}/llvm-versions/{branch}"
workDir = numBranchPre

if len(sys.argv) > 1:
    testObj = sys.argv[2]
if testObj == 'llc':
    testObj = 'llc'
    testObjPath = numBranchPre + '/bin/llc'
elif testObj == 'opt':
    testObj = 'opt'
    testObjPath = numBranchPre + '/bin/opt'

seedCnt = 1
openThrowNeedle = True 
timeBound = int(cfg.get('llvm-main', 'time_bound'))
seedToReadNum = 1
helpIRNum = 0
failOpt = ''  
compOpt = ''  
failType = 0
i = 3
while i < len(sys.argv):
    if sys.argv[i] == 'FEN_GE':
        i += 1
        break
    failOpt += f' {sys.argv[i]}'
    i += 1
while i < len(sys.argv):
    compOpt += f' {sys.argv[i]}'
    i += 1
failOpt = failOpt.strip()
compOpt = compOpt.strip()
beginTime = datetime.datetime.now()  
isOverTime = False  

def getNowExecTime():
    return int((datetime.datetime.now() - beginTime).seconds)

realMutateLocTemp = {}

def readSeed() -> str:  
    return '1.fail'

def throwNeedles(seedPath: str):  
    IRName = seedPath.strip().split('/')[-1]
    realMutateLocTemp.clear()
    mutateTime = 50  
    tempStrategyPool = StrategyScopePool()
    tempStrategyPool.addStrategy(1, Scope(1, 0, 1, 0, 1, 0), 1)
    tempStrategyPool.addStrategy(2, Scope(1, 0, 1, 0, 1, 0), 1)
    tempStrategyPool.addStrategy(3, Scope(1, 0, 1, 0, 1, 0), 1)
    ret = {} 
    t = 0
    for i in range(mutateTime):
        st = tempStrategyPool.randStrategy()
        ss = st[0]
        os.system(f'{fuzzerPath} {seedPath} -o {tempPoolPath}/{IRName}.needle -scope {ss.s.f1} {ss.s.f2} {ss.s.b1} {ss.s.b2} {ss.s.i1} {ss.s.i2} -msn {ss.num} > {realMutateLocPath}')  
        e = judgeExecRes(branch, f"{tempPoolPath}/{IRName}.needle", failOpt, compOpt, failType, testObj)
        if e == 'pass':
            r = parseRealMutateScopeFile(realMutateLocPath)
            iFloor = r['i'] - 1
            if iFloor < 0:
                iFloor = 0
            _ss = StrategyScope(Scope(r['f'], r['f'], r['b'], r['b'], iFloor, r['i'] + 1), ss.num)
            if _ss not in ret:
                ret[_ss] = 0
            ret[_ss] += 1
            t += 1
    os.system(f'rm -f {tempPoolPath}/{IRName}.needle')
    return ret


def mutateSeed(seedName: str):
    realMutateLocTemp.clear()
    if os.path.exists(tempPoolPath):
        os.system(f'rm -f -r {tempPoolPath}')
    os.system(f'mkdir {tempPoolPath}')
    banIndex = -2
    while True:
        resCnt = {}
        i = 0
        constantInvalid = 0
        constantSame = 0
        ret = pool.randStrategy()  
        ss = ret[0]
        index = ret[1]
        while banIndex == int(index):  
            ret = pool.randStrategy()  
            ss = ret[0]
            index = ret[1]
        banIndex = -2
        while i < time:  
            newName = f'{i}.{index}'  
            newPath = f'{tempPoolPath}/{newName}'
            genBTime = datetime.datetime.now()
            os.system(f'{fuzzerPath} {seedPoolPath}/{seedName} -o {newPath} -scope {ss.s.f1} {ss.s.f2} {ss.s.b1} {ss.s.b2} {ss.s.i1} {ss.s.i2} -msn {ss.num} > {realMutateLocPath}')  
            e = judgeExecRes(branch, newPath, failOpt, compOpt, failType, testObj)
            genETime = datetime.datetime.now()
            genTime = (genETime - genBTime).total_seconds()
            if e == False or haveSameIR(newPath) or judgeIREqual(f'{seedPoolPath}/{seedName}', f'{newPath}'):  
                os.system(f'rm -f {newPath}')
                constantInvalid += 1
                if constantInvalid >= time:
                    banIndex = index
                    break
                continue
            else:
                constantInvalid = 0
            if e not in resCnt:
                resCnt[e] = 0
            resCnt[e] += 1
            t = newPath + '.' + e
            os.system(f'mv {newPath} {t}')
            realMutateLocTemp[t.strip()] = parseRealMutateScopeFile(realMutateLocPath)
            i += 1
        if len(os.listdir(tempPoolPath)) != 0 or getNowExecTime() >= timeBound:  
            break

def getTempSeedCov():
    tempNames = os.listdir(f'{tempPoolPath}')
    collectOverNames = []
    for name in tempNames:
        ir_path = f"{tempPoolPath}/{name}"
        covName = f"{name}.ir_cov"
        collect_one_cov_dir_big(  
            workdir=workDir,
            stmtfilename=covName,  
            covdir='',  
            gcov_path='gcov',  
            testObj_path=testObjPath,
            options=f'{failOpt}',  
            ir_path=ir_path,  
            collectfiles={}  
        )
        os.system(f'mv {workDir}/{covName} {tempPoolPath}/{covName}')
        collectOverNames.append(name)
        if getNowExecTime() >= timeBound:  
            print('[] search is end (collect) !!')
            for n in tempNames:
                if n not in collectOverNames:
                    os.system(f"rm -f {tempPoolPath}/{n}")
            break


def feedback():  
    newSeedPathList1 = os.listdir(f'{tempPoolPath}')
    if len(newSeedPathList1) == 0:
        return 0
    newSeedPathList = []
    for i in range(len(newSeedPathList1)):  
        if newSeedPathList1[i].find('ir_cov') == -1:  
            newSeedPathList.append(f'{tempPoolPath}/' + newSeedPathList1[i])
    existIRCovPaths = os.listdir(f'{irCovsPath}')
    for i in range(len(existIRCovPaths)):
        existIRCovPaths[i] = f'{irCovsPath}/' + existIRCovPaths[i]
    for f in os.listdir(helpIRCovsPath):
        existIRCovPaths.append(f"{helpIRCovsPath}/{str(f)}")
    clusters = getClusterDiv(existIRCovPaths, f"{irCovsPath}/1.fail.ir_cov")
    sc = {}  
    scores = []  
    scoreSum = 0.0
    for nsp in newSeedPathList:
        sc[nsp] = calSeedScore(nsp, clusters)  
        scores.append(sc[nsp])
        scoreSum += sc[nsp]
        print(f"sc[nsp]: {sc[nsp]}")
    if scoreSum == 0.0:
        return False
    preAddWeight = {}
    for nsp in newSeedPathList: 
        dw = pool.getMinWeight() * (sc[nsp] / scoreSum)
        index = int(nsp.split('/')[-1].split('.')[-2])
        preAddWeight[index] = dw
    scores.sort(reverse=True)
    for s in scores:  
        print(s, end=' ')
    print('')
    MAX_CNT = 1
    trunc = MAX_CNT - 1
    if trunc >= len(scores):
        trunc = len(scores) - 1
    bound = scores[trunc]  
    cnt = 0
    for nsp in newSeedPathList:
        if sc[nsp] >= bound and sc[nsp] != 0.0: 
            global seedCnt
            seedCnt += 1
            newIRName = f"{seedCnt}.{nsp.strip().split('.')[-1]}"  
            os.system(f'mv {nsp} {seedPoolPath}/{newIRName}')
            os.system(f'mv {nsp}.ir_cov {irCovsPath}/{newIRName}.ir_cov')
            loc = realMutateLocTemp[nsp.strip()]
            index = int(nsp.split('/')[-1].split('.')[-2])
            if len(loc) == 2:  
                pool.addWeight(index, preAddWeight[index])
                print(f'[] feedback: {pool.getStrategy(index)} add weight {str(dw)}, now weight: {pool.getWeight(index)}')
            elif int(loc['i']) >= 0:  
                iFloor = loc['i'] - 1  
                if iFloor < 0:
                    iFloor = 0
                scope = Scope(loc['f'], loc['f'], loc['b'], loc['b'], iFloor, loc['i'] + 1)
                nss = StrategyScope(scope, pool.getStrategy(index).num)  
                ret = pool.existSameStrategyScope(nss)
                if ret != False:
                    pool.addWeight(ret, preAddWeight[index])
                    print(f'[] feedback: {pool.getStrategy(ret)} add weight {str(dw)}, now weight: {pool.getWeight(index)}')
                else:  
                    newIndex = pool.addStrategy(nss.num, nss.s, 1)
                    pool.addWeight(newIndex, preAddWeight[index])
                    print(f'[] feedback: {pool.getStrategy(newIndex)} add weight {str(dw)}, now weight: {pool.getWeight(newIndex)}')
            cnt += 1
            if cnt == MAX_CNT:  
                break
    print(f'[] the number of new witness IR tests in this iteration: {cnt}')
    global helpIRNum
    for f in os.listdir(tempPoolPath):
        if str(f).find(".ir_cov") != -1: 
            nameList = str(f).strip().split(".")
            os.system(f"mv {tempPoolPath}/{str(f)} {helpIRCovsPath}/{helpIRNum}.{nameList[-2]}.{nameList[-1]}")
            os.system(f"mv {tempPoolPath}/{str(f)[0: (len(str(f)) - 7)]} {helpIRsPath}/{helpIRNum}.{nameList[-2]}")
            helpIRNum += 1
    os.system(f'rm -f -r {tempPoolPath}')
    os.system(f'mkdir {tempPoolPath}')

def init():
    for p in os.listdir(f"{seedPoolPath}"):
        if p != '1.fail':
            os.system(f'rm -f {seedPoolPath}/{p}')
    for p in os.listdir(f"{irCovsPath}"):
        if p != '1.fail.ir_cov':
            os.system(f'rm -f {irCovsPath}/{p}')
    for p in os.listdir(helpIRCovsPath):  
        os.system(f"rm -f {helpIRCovsPath}/{p}")
    for p in os.listdir(helpIRsPath):
        os.system(f"rm -f {helpIRsPath}/{p}")
    global failType
    loopCnt = 0
    while True:
        loopCnt += 1
        if testObj == 'opt':
            failType = get1FailType(branch, "opt", failOpt, compOpt)  
        elif testObj == 'llc':
            failType = get1FailType(branch, "llc", failOpt, compOpt)  
        if failType[0] != True:  
            print(f'get1FailType[0] is not True, repeat this after 5s!, {failType}')
            TimeModule.sleep(5)
        else:
            break
        if loopCnt >= 6:
            print(f'1.fail failType Except => {failType}')
            exit(114)
    
    print('[] to collect the coverage of the initial failing test 1.fail ...')
    collect_one_cov_dir_big(  
        workdir=workDir,
        stmtfilename='1.fail.ir_cov',  
        covdir='',  
        gcov_path='gcov',  
        testObj_path=testObjPath,
        options=f'{failOpt}',  
        ir_path=f'{seedPoolPath}/1.fail',  
        collectfiles={}  
    )
    os.system(f'mv {workDir}/1.fail.ir_cov {irCovsPath}/1.fail.ir_cov')
    print('[] collect ok! ')
    pool.addStrategy(1, Scope(1, 0, 1, 0, 1, 0), 1)
    pool.addStrategy(2, Scope(1, 0, 1, 0, 1, 0), 1)
    pool.addStrategy(3, Scope(1, 0, 1, 0, 1, 0), 1)
    if openThrowNeedle:  
        throwRes = throwNeedles(f'{seedPoolPath}/1.fail')
        if len(throwRes) > 0:
            sumCnt = 0
            for k in throwRes:
                sumCnt += int(throwRes[k])
            for k in throwRes:
                pool.addStrategy(k.num, k.s, 1 + throwRes[k] / sumCnt)
            print('[] candidate construction ok !')
            pool.printAll(0)
        else:
            print('[] candidate construction ok but no result !')

def main():
    print('[] to init...')
    init()
    print('[] init over...')
    while True:
        if getNowExecTime() >= timeBound:  
            print('[] search is end!!')
            break
        seedName = readSeed()
        mutateSeed(seedName)
        pool.printAll(1)
        print('[] to collect the coverage of witness tests in this iteration')
        getTempSeedCov()
        print('[] collect over, next feedback...')
        feedback()
        print('[] feedback over...')
        pool.printAll(3)
        print('[] the next iteration will begin...')

if __name__ == '__main__':  
    main()
