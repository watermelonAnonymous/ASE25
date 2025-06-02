import os
import configparser
from utils import get1FailType, judgeExecRes, clearPassLine, collect_one_cov_dir_big  # these all for getMinOptLevel

# test data points
testNums = {
    'llc': [48813, 50519, 56103, 108722],
    'opt': [69097, 66986, 66066, 68260, 64669, 64598, 64345, 64333, 64259, 60944, 58401, 63926, 63763, 63727, 64047, 63327, 62088, 61312, 59704, 58725, 58340, 57899, 62175, 58441, 66484, 69096, 70547, 54228, 54224, 54217, 63336, 63337, 56039, 54235, 54112, 54023, 52722, 51618, 51136, 50727, 50469, 50430, 50387, 50296, 50291, 50288, 50250, 50246, 49965, 49931, 49597, 49005, 44705, 82243, 87630, 87534, 85536, 129244, 121110, 88103, 114879, 131465, 102351, 80113, 116483, 79743, 119646, 94897, 121745, 79861, 119173, 84807, 108698, 98838, 98139, 124275, 116553, 122496, 71700, 72831, 74739, 75298, 76162, 76789, 115149, 124387, 70507, 70509, 70510, 70470, 63611]
}
cfg = configparser.ConfigParser()
cfg.read('./config/config.ini')  # run start "my-src" dir
optPassLinePath = cfg.get('llvm-main', 'OPT_PASS_LINE_PATH')
llvmBugsPath = cfg.get('llvm-main', 'LLVM_BUGS_PATH')
# seedPoolPath irCovsPath helpIRCovsPath helpIRsPath
seedPoolPath = cfg.get('llvm-main', 'SEED_POOL_PATH')
irCovsPath = cfg.get('llvm-main', 'IR_COVS_PATH')
helpIRCovsPath = cfg.get('llvm-main', 'HELP_IR_COVS_PATH')
helpIRsPath = cfg.get('llvm-main', 'HELP_IRS_PATH')

llvmDisPath = cfg.get('llvm-main', 'LLVM_DIS_15')
execLogPath = cfg.get('llvm-main', 'EXEC_LOG_PATH')
llvmVersionsPathPre = cfg.get('llvm-main', 'LLVM_VERSIONS_PATH_PRE')
expResultsPath = cfg.get('llvm-main', 'exp_results_path')

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

def init():
    if os.path.exists(execLogPath):
        os.system(f'rm -f {execLogPath}')
    os.system(f'touch {execLogPath}')

def writeLog(content: str):
    log = open(execLogPath, 'a')  
    print(content, file=log)
    log.flush()  
    log.close()

def getMinOptiLevel(num):
    loc = parseLocationsFile(num)
    failOpt = loc['fail opti level']
    preOpt = loc['pre-opt-fail opti level']
    optOpts = loc['opt-fail opti level']
    branch = loc['test trunk']
    numOptPath = f"{llvmVersionsPathPre}/llvm-versions/{branch}/bin/opt"
    numLLIPath = f"{llvmVersionsPathPre}/llvm-versions/{branch}/bin/lli"
    oriFailPath = f"{llvmBugsPath}/{num}/1.fail"
    failType = get1FailType(branch, 'opt', optOpts, '-O0', oriFailPath)
    print(num, end=' => ')
    if str(failType[2]) == 'False':
        print((failType[0], failType[1], failType[2], int(failType[3] >> 8)))
    else:
        print(failType)
    l = 0
    r = 800
    passLine = ''
    lines = []
    while l <= r:
        i = (l + r) // 2
        i_1 = i - 1
        if i == 0:
            i_1 = 0
        res = judgeExecRes(branch, oriFailPath, f"{optOpts} -opt-bisect-limit={i}", f"{optOpts} -opt-bisect-limit={i_1}", failType, 'opt', True)
        if res == 'fail':
            os.system(f"{llvmDisPath} {oriFailPath} -o {oriFailPath}.ll")
            os.system(f"{numOptPath} {optOpts} -opt-bisect-limit={i} {oriFailPath}.ll -o /dev/null 2> {oriFailPath}.out")
            with open(f"{oriFailPath}.out", 'r') as f:
                lines = f.readlines()
            os.system(f"rm -f {oriFailPath}.ll {oriFailPath}.out")
            passLine = [x.strip() for x in lines if f'pass ({i})' in x][0]
            break
        elif res == 'pass':
            l = i + 1
        else: 
            r = i - 1
    if l > r:
        return False
    rk = [l.strip() for l in lines if clearPassLine(passLine) == clearPassLine(l.strip())].index(passLine) + 1
    return (i, passLine, rk)


def buildCompiler(num):
    compilersPath = f"{llvmVersionsPathPre}/llvm-versions"
    loc = parseLocationsFile(num)
    branch = loc['test trunk']
    if branch not in os.listdir(compilersPath): # if the compiler exists, skip building
        oriDir = os.getcwd()
        os.chdir(compilersPath)
        os.system('git clone https://github.com/llvm/llvm-project.git')
        os.system(f'mv llvm-project {branch}')
        os.chdir(f'{compilersPath}/{branch}')
        os.system(f"git checkout {branch.split('-')[0]}")
        if os.path.exists(f"{compilersPath}/{branch}/llvm/include/llvm/Support/Signals.h"):
            # solve possible compile error(s)
            addCStdin(f"{compilersPath}/{branch}/llvm/include/llvm/Support/Signals.h")
        # gcc and c++ version => 13.1.0
        os.system(f"cmake -DCMAKE_C_COMPILER=gcc -DCMAKE_CXX_COMPILER=c++ -DLLVM_ENABLE_PROJECTS=clang -DCMAKE_BUILD_TYPE=Release -DCMAKE_C_FLAGS=\"-g -O0 -fprofile-arcs -ftest-coverage\" -DCMAKE_CXX_FLAGS=\"-g -O0 -fprofile-arcs -ftest-coverage\" -DCMAKE_EXE_LINKER_FLAGS=\"-g -fprofile-arcs -ftest-coverage -lgcov\" llvm")
        os.system(f'make -j64 clang opt lli llc')
        os.chdir(oriDir)
    else:
        print(f'llvm {branch} exists, skip building')


def main():
    init()
    for k in testNums:
        for num in testNums[k]:
            print(f'the compiler version of {num} bug will begin build (if not exist)')
            buildCompiler(num)     
            print(f"-----------------------------", flush=True)  
            print(f"BEGIN BEGIN: {num} begin isolation", flush=True)
            writeLog(f"{num} begin isolation")
            loc = parseLocationsFile(num)
            branch = loc['test trunk']
            failOptions = loc['fail opti level']
            optOpts = loc['opt-fail opti level']
            if k == 'llc':
                os.system(f"cp {llvmBugsPath}/{num}/1.fail {seedPoolPath}/1.fail")
                compOptOpts = '-O0'
                # the limit of one hour is completed inside main.py
                exitCode = os.system(f"timeout 7200s python3 main.py {branch} llc {failOptions} FEN_GE {compOptOpts}")
                exitCode >>= 8
                if exitCode == 124:
                    writeLog(f"{num} bug python3 main.py timeout")
                elif exitCode != 0:
                    writeLog(f"{num} bug python3 main.py ERROR, ExitCode = {exitCode}")
                else:
                    writeLog(f"{num} bug isolation ok!")
            elif k == 'opt':
                os.system(f"cp {llvmBugsPath}/{num}/1.fail {seedPoolPath}/1.fail")
                compOptOpts = '-O0'
                exitCode = os.system(f"timeout 7200s python3 main.py {branch} opt {optOpts} FEN_GE {compOptOpts}")
                exitCode >>= 8  
                if exitCode == 124:
                    writeLog(f"{num}号 bug python3 main.py timeout")
                elif exitCode != 0:
                    writeLog(f"{num}号 bug python3 main.py ERROR, ExitCode = {exitCode}")
                else:
                    writeLog(f"{num}号 bug isolation ok!")
                optInfo = getMinOptiLevel(num)
                if optInfo != False:
                    # collect coverage -opt-bisect-limit
                    opt = f'{optOpts} -opt-bisect-limit={optInfo[0]}'
                    collect_one_cov_dir_big(
                        workdir=f"{llvmVersionsPathPre}/llvm-versions/{branch}",
                        stmtfilename='1.fail.ir_cov',
                        covdir='', 
                        gcov_path='gcov',
                        testObj_path=f"{llvmVersionsPathPre}/llvm-versions/{branch}/bin/opt",
                        options=f'{opt}',
                        ir_path=f'{llvmBugsPath}/{num}/1.fail',  # 要收集覆盖率的IR对象
                        collectfiles={}  # 空即可, 表示不指定而全收集
                    )
                    os.system(f'mv {llvmVersionsPathPre}/llvm-versions/{branch}/1.fail.ir_cov {llvmBugsPath}/{num}/bisect_bug_opt_pass.ir_cov')

            # save process files
            # seedPoolPath irCovsPath helpIRCovsPath helpIRsPath
            numResultPath = f"{expResultsPath}/{num}"
            if os.path.exists(numResultPath):
                os.system(f'rm -r -f {numResultPath}')
            os.system(f"mkdir {numResultPath}")
            for sfp in [seedPoolPath, irCovsPath, helpIRCovsPath, helpIRsPath]:
                os.system(f'cp -p -r {sfp} {numResultPath}')

if __name__ == '__main__':
        main()
