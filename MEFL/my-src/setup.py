import os
import configparser

cfg = configparser.ConfigParser()
cfg.read('./config/config.ini')  # run start "my-src" dir

# get pwd and setup
MEFL_PATH = os.getcwd()
cfg.set('llvm-main', 'MEFL_PATH', MEFL_PATH)
with open('./config/config.ini', 'w') as f:
    cfg.write(f)

# initialize work dirs
workdirs = []
workdirs.append(cfg.get('llvm-main', 'seed_pool_path'))
workdirs.append(cfg.get('llvm-main', 'temp_seeds_pool_path'))
workdirs.append(cfg.get('llvm-main', 'help_irs_path'))
workdirs.append(cfg.get('llvm-main', 'ir_covs_path'))
workdirs.append(cfg.get('llvm-main', 'help_ir_covs_path'))
workdirs.append(cfg.get('llvm-main', 'exp_results_path'))

workfiles = []
workfiles.append(cfg.get('llvm-main', 'exec_log_path'))
workfiles.append(cfg.get('llvm-main', 'real_mutate_loc'))

for d in workdirs:
    if not os.path.exists(d):
        os.system(f'mkdir {d}')

for f in workfiles:
    if not os.path.exists(f):
        os.system(f"touch {f}")


# build compilers





# setup permission
os.system(f'chmod -R 777 {MEFL_PATH}/../') # make sure normal execution