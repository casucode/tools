import logging
import logging.handlers
def log_gen(level='DEBUG',logfile=None,threads=False,log_only=False,email_level=None,email_data={}):
    """
 *+
 *  Name:
 *      log_gen
 *
 *  Purpose:
 *      Generate a python logging instance
 *
 *  Description:
 *      This method provides the mechanism to generate a python logger for
 *      recording structured information with levels from DEBUG to CRITICAL.
 *      Optional email escalation for submissions above a particular level
 *      is available.
 *      
 *      File output is via a rotating file handler that will archive the log 
 *      when it reaches 5MB in size. The output format of the log entry is:
 *      
 *      Day nn Month hr:mm:ss yyyy @module.<function>() [level] [thread_id] : message
 *
 *  Arguments:
 *      level ['DEBUG']
 *          The minimum reporting level to output
 *      logfile [None]
 *          String to output logfile if required
 *      threads [False]
 *          Will multiple threads be generating log entries?
 *      log_only [False]
 *          Only output to the logfile (do not output to stdout)
 *      email_level [None]
 *          Define minimum loglevel for email escalation
 *      email_data [{}]
 *          Python dictionary containing information needed for email messaging. Keys:
 *                 'FROM'    : The email address of the author
 *                 'TO'      : The target email address
 *                 'SUBJECT' : Subject line for the email
 *                 'BUFFER'  : Number of lines before the buffer is flushed (ie, send email)
 *      
 *  Returned values:
 *      Instance of <logging.RootLogger>
 *
 *  Notes:
 *      None
 *
 *  Dependencies:
 *      Python core 
 *
 *  Authors:
 *      David Murphy (CASU, IoA)
 *
 *  Copyright:
 *      Copyright (C) 2017-2018 Cambridge Astronomy Survey Unit.
 *      All Rights Reserved.
 *
+*  
    """
    import sys
    import logging
    from tools import ColourFormatter

    if level not in ['DEBUG','INFO','WARNING','ERROR','CRITICAL']:
            print "defined level '%s' not recognised. Setting to DEBUG" %(level)
            level = 'DEBUG'

    log = logging.getLogger()

    if not len(log.handlers):
            log.setLevel(level)
            if threads:
                    formatter = logging.Formatter('%(asctime)s @%(module)s.%(funcName)s() [%(levelname)s] [%(threadName)s] : %(message)s',datefmt="%a %d %b %H:%M:%S %Y")
            else:
                    formatter = logging.Formatter('%(asctime)s @%(module)s.%(funcName)s() [%(levelname)s] : %(message)s',datefmt="%a %d %b %H:%M:%S %Y")

            if email_level != None:
                from tools import SMTPBufferHandler
                MAILHOST = 'smtp.ast.cam.ac.uk'
                try:
                    FROM = email_data['FROM']
                except KeyError:
                    FROM = 'dmurphy@ast.cam.ac.uk'
                try:
                    TO = email_data['TO']
                except:
                    TO = 'dnamurphy@gmail.com'
                try:
                    SUBJECT = email_data['SUBJECT']
                except:
                    SUBJECT  = 'A critical message from your server'
                try:
                    buffer_size = email_data['BUFFER']
                except:
                    buffer_size = 1
                eh = SMTPBufferHandler(MAILHOST, FROM, TO, SUBJECT, buffer_size)
                eh.setLevel('CRITICAL')
                eh.setFormatter(formatter)
                eh.set_name('email_stream')
                log.addHandler(eh)


            if (not log_only) or (not logfile):
                    ch = logging.StreamHandler(sys.stdout)
                    ch.setLevel(level)
                    ch.setFormatter(formatter)

                    ch.setFormatter(ColourFormatter(threads=threads))
                    ch.set_name('stdout')
                    log.addHandler(ch)
                    

            if logfile:
                    from logging.handlers import RotatingFileHandler
                    fh = RotatingFileHandler(logfile, maxBytes=5242880, backupCount=20)
#                    fh = logging.FileHandler(logfile)
                    fh.setLevel(level)
                    fh.setFormatter(formatter)
                    fh.set_name('log_file')
                    log.addHandler(fh)
    return log            

class ColourFormatter(logging.Formatter):
  BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)
  NONE = 9
  
  RESET_SEQ = "\033[0m"
  COLOUR_SEQ = "\033[1;%dm"
  COLOUR_SEQ2 = "\033[1;%dm\033[1;%dm"
  COLOUR_SEQ2 = "\033[%dm\033[%dm"
  NORMAL = ""
  BOLD = "\033[1m"
  UBER = "\033[4m"

  BGCOLOURS = {
    'WARNING': NONE,
    'INFO': NONE,
    'DEBUG': NONE,
    'CRITICAL': RED,
    'ERROR': NONE
    }

  COLOURS = {
    'WARNING': YELLOW,
    'INFO': GREEN,
    'DEBUG': CYAN,
    'CRITICAL': YELLOW,
    'ERROR': RED
  }

  FONT = {
    'WARNING': BOLD,
    'INFO': NORMAL,
    'DEBUG': NORMAL,
    'CRITICAL': BOLD,
    'ERROR': BOLD
  }

  def __init__(self, use_colour=True,threads=False):
    if threads == True:
      self.FORMAT = '%(asctime)s @%(module)s.%(funcName)s() [%(levelname)s] [%(threadName)s] : %(message)s'
    else:
      self.FORMAT = '%(asctime)s @%(module)s.%(funcName)s() [%(levelname)s] : %(message)s'

    msg = self.formatter_msg(self.FORMAT, use_colour)
    logging.Formatter.__init__(self, msg,datefmt="%a %d %b %H:%M:%S %Y")
    self.use_colour = use_colour


  def formatter_msg(self, msg, use_colour = True):
    if use_colour:
      msg = msg.replace("$RESET", self.RESET_SEQ)
    else:
      msg = msg.replace("$RESET", "")
    return msg

  def format(self, record):
    levelname = record.levelname
    if self.use_colour and levelname in self.COLOURS:
      fore_colour = 30 + self.COLOURS[levelname]
      back_colour = 40 + self.BGCOLOURS[levelname]
      levelname_colour = self.COLOUR_SEQ % fore_colour + levelname + self.RESET_SEQ
      levelname_colour = self.COLOUR_SEQ2 % (fore_colour , back_colour) + levelname + self.RESET_SEQ
      levelname_colour = self.COLOUR_SEQ2 % (fore_colour , back_colour) + self.FONT[levelname] + levelname + self.RESET_SEQ

      record.levelname = levelname_colour
    return logging.Formatter.format(self, record)

class SMTPBufferHandler(logging.handlers.BufferingHandler):
    import logging, logging.handlers, email
    import email.encoders
    import email.header
    import email.mime.base
    import email.mime.multipart
    import email.mime.text

    def __init__(self, mailhost, fromaddr, toaddrs, subject, capacity):
        logging.handlers.BufferingHandler.__init__(self, capacity)
        self.mailhost = mailhost
        self.mailport = None
        self.ccaddrs = None
        self.fromaddr = fromaddr
        if type(toaddrs) == type([]):
            self.toaddrs = toaddrs[0]
            self.ccaddrs = toaddrs[1:]
        else:
            self.toaddrs = toaddrs

        self.subject = subject
        self.setFormatter(logging.Formatter("%(asctime)s %(levelname)-5s %(message)s"))

    def flush(self):
        if len(self.buffer) > 0:
            
            if 1:
                import smtplib
                port = self.mailport
                if not port:
                    port = smtplib.SMTP_PORT
                smtp = smtplib.SMTP(self.mailhost, port)
                msg = email.mime.multipart.MIMEMultipart()
                msg.set_charset( 'utf-8' )
                msg['Subject'] = email.header.Header(self.subject)
                msg['From'] = email.header.Header(self.fromaddr)
                msg['To'] = email.header.Header(self.toaddrs)
                email_to = self.toaddrs
                if self.ccaddrs != None:
                    cc_list = ','.join(self.ccaddrs)
                    msg['Cc'] = email.header.Header( cc_list )
                    if type(email_to) == type(''):
                        email_to = [email_to] + list(self.ccaddrs)
                    else:
                        email_to = email_to + list(self.ccaddrs)
                        
                msg['Date'] = email.header.Header(email.utils.formatdate())
                msg['Message-ID'] = email.header.Header(email.utils.make_msgid())
                msg['X-Priority'] = "1"
                
                message = "The following urgent errors have been issued by the server: \n\n"
                for record in self.buffer:
                    s = self.format(record)
                    _rec = s.__repr__()
                    _rec = _rec.replace('\\x1b[33m\\x1b[41m\\x1b[1m','')
                    _rec = _rec.replace('\\x1b[0m','')
                    _rec = _rec.replace("'",'')
                    _rec = _rec.replace('"','')
                    message = message + _rec + "\r\n"
                msg.attach( email.mime.text.MIMEText( message, 'plain' ) )
                
                smtp.sendmail(self.fromaddr, email_to, msg.as_string())
                smtp.quit()
            else:
                self.handleError(None)
            self.buffer = []

