import sys, os, shutil, re

DEBUG = True
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

def debug(string):
    if DEBUG:
        print string

def make_link(source_path, dest_path, tiered=False):
    debug('  linking %s%s' % (dest_path, ' [tiered]' if tiered else '',))
    if DRY_RUN: return

    try:
        os.remove(dest_path)
    except: pass
    os.symlink(source_path, dest_path)

def copy_file(source_path, dest_path, tiered=False):
    debug ('  copying %s%s' % (dest_path, ' [tiered]' if tiered else '',))
    if DRY_RUN: return

    try:
        os.remove(dest_path)
    except: pass
    shutil.copyfile(source_path, dest_path)

def split_file(file_path):
    result = {}
    if os.path.exists(file_path):
        fp = open(file_path)
        for path in fp:
            result[path.strip()] = 1
        fp.close()
    return result

def walk_scheme(scheme, tier, operation=make_link, copy_list={}, ignore_list={}):
    debug('creating links for scheme "%s"...' % (scheme,))

    #dev_reg = re.compile(r'.*\.development$')
    #stag_reg = re.compile(r'.*\.staging$')
    #prod_reg = re.compile(r'.*\.production$')
    #tier_reg = re.compile(r'.*\.'+tier+'$')

    for dirname, subdirs, files in os.walk(scheme):

        if len(dirname) == len(scheme): continue #don't do anything in root dir
        dirname = dirname[len(scheme)+1:] #remove scheme name from paths

        for filename in files:
            tiered = False
            source_path = os.path.join(BASE_DIR, scheme, dirname, filename)
            dest_path = os.path.join('/', dirname, filename)

            '''
            if dev_reg.match(source_path) or stag_reg.match(source_path) or prod_reg.match(source_path):
                if tier_reg.match(source_path):
                    tiered = True
                    dest_path = dest_path.replace('.'+tier, '')
                else:
                    continue
            '''

            if dest_path in copy_list:
                copy_file(source_path, dest_path, tiered=tiered)
            elif dest_path in ignore_list:
                debug('  skipping %s' % (dest_path,))
            else:
                operation(source_path, dest_path, tiered=tiered)

if __name__ == '__main__':

    if len(sys.argv) != 3:
        print "usage: python homeworld.py <scheme:home> <test|real>"
        sys.exit(2)

    scheme = sys.argv[1]
    #tier = sys.argv[2]
    DRY_RUN = sys.argv[2] != 'real'

    if DRY_RUN:
        debug('NOTE: This is just a test run. No links are being created or deleted!')

    IGNORE_FILE = scheme + '/IGNORE'
    COPY_FILE = scheme + '/COPY'

    ignore_list = split_file(IGNORE_FILE)
    copy_list = split_file(COPY_FILE)

    walk_scheme(scheme, tier=None, copy_list=copy_list, ignore_list=ignore_list)
