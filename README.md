# tools
Collection of common tools (logging, config file read / writes etc)

This will create a sub-directory in the CWD called tools

To create a logging instance:

from tools.logger import log_gen

loglevel = 'INFO'

logile = './log.txt'
nthreads = 1

email_data = {}

email_data['FROM'] = 'David Murphy <dmurphy@ast.cam.ac.uk>'

email_data['TO'] = ['a@b.com','c@d.com']

email_data['SUBJECT'] = '[SERVER] CRITICAL: service unhappy'

email_data['BUFFER'] = 10

log = log_gen(level=loglevel,logfile=logpath,threads=nthreads>1,log_only=False,email_level='INFO',email_data=email_data)

