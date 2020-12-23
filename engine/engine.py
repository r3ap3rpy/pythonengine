import html
import os
import logging
import socket
import psycopg2
import subprocess
import smtplib
import ssl
from time import sleep

from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv

if os.name == 'nt':
    import wmi
else:
    import signal

CWD = os.path.sep.join(os.path.abspath(__file__).split(os.path.sep)[:-1])
LOGS = os.path.sep.join([CWD, 'Logs'])
LOGFILENAME = f'PyEngine.log'
PIDS = os.path.sep.join([CWD, 'PIDS'])
MYPID = os.getpid()
PIDFILE = os.path.sep.join([PIDS,str(MYPID)])
Credentials = ['GMDBSERVER','GMDB','GMDBUSER','GMDBPASS','GMADMIN','GMTIMEOUT','GMSCHEDFREQ','SMTPSERVER','SMTPPORT']
CONFIGFILE = os.path.sep.join([CWD,'Config','.env'])

logging.basicConfig(format='%(asctime)s %(levelname)s :: %(message)s', level=logging.INFO)
logger = logging.getLogger('PyEngine')
handler = RotatingFileHandler(os.path.sep.join([LOGS,LOGFILENAME]), mode='a', maxBytes=1000000, backupCount=100, encoding='utf-8', delay=0)
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

logger.info(f"#########################################")
logger.info(f"### Initializing ###")

logger.info(f"My PID: {MYPID}")


logger.info(f"Checking for config file!")
if os.path.isfile(CONFIGFILE):
    load_dotenv(dotenv_path=os.path.sep.join([CWD,'Config','.env']))
    logger.info(f"Configuration successfully read!")
else:
    logger.critical(f"Cannot find configuration file: {CONFIGFILE}, aborting!")
    logger.info(f"#########################################")
    raise SystemExit()

logger.info(f"Verifying credentials...")
for credential in Credentials:
    if os.getenv(credential):
        logger.info(f"Credential: {credential} found!")
    else:
        logger.critical(f"Credential: {credential} cannotbe found, aborting!")
        logger.info(f"#########################################")
        raise SystemExit


timeout = int(os.getenv('GMTIMEOUT'))
schedfreq = int(os.getenv('GMSCHEDFREQ'))
worker = (os.getenv('COMPUTERNAME').split('.')[0].upper() if os.name == 'nt' else os.getenv('HOSTNAME').split('.')[0].upper())
logger.info(f"Worker: {worker}")
pendingtimeout = timeout + schedfreq
logger.info(f"Timeout: {timeout} seconds")

logger.info(f"Checking SMTP server availability...")
tobeusedSMTP = os.getenv('SMTPSERVER')
logger.info(f"Using smtp server {tobeusedSMTP} ")
logger.info(f"Creating pidfile!")
with open(PIDFILE, 'w') as mcf:
    mcf.write(f"{str(datetime.now())}")

logger.info(f"Killing and removing pidfiles for processes past timeout of {timeout}")
pasttimeout = [ _ for _ in os.listdir(PIDS) if not _ == str(MYPID) ]

if pasttimeout:
    logger.info(f"A total of {len(pasttimeout)} pids found, checking their remaining time!")
    currenttime = datetime.now()
    for file in pasttimeout:
        try:
            with open(os.path.sep.join([PIDS, file])) as f:
                spawntime = datetime.strptime(f.read(), '%Y-%m-%d %H:%M:%S.%f')
            logger.info(f"The process was spawned at: {spawntime}")
        except Exception as e:
            logger.critical(f"Cannot identify when the process was spawned because: {e}")

        diff = (datetime.now() - spawntime).seconds
        logger.info(f"The process was spawned {diff} seconds ago!") 
        if diff > timeout:
            logger.info(f"Attempting to kill it!")
            try:
                if os.name == 'nt':
                    f = wmi.WMI()
                    for process in f.Win32_Process(ProcessID=int(file)):
                        process.Terminate()
                else:
                    os.kill(int(file),signal.SIGKILL)
                
                logger.info(f"Successfully killed the process...")
                os.remove(os.path.sep.join([PIDS, file]))
            except ProcessLookupError as e:
                logger.info(f"The process does not exist anymore with PID: {file}, removing lockfile.")
                os.remove(os.path.sep.join([PIDS, file]))
            except Exception as e:
                logger.critical(f"Unable to kill process because: {e}, aborting...")
                raise SystemExit
        else:
            logger.info(f"Has {timeout-diff} seconds to complete it's task!")

else:
    logger.info(f"There are no remnants or stuck processes past timeout!")


logger.info("Trying to establish connection with the database.")
try:
    conn = psycopg2.connect( host=os.getenv("GMDBSERVER"), dbname = os.getenv("GMDB"), user=os.getenv("GMDBUSER") ,password = os.getenv("GMDBPASS"))
    cursor = conn.cursor()
    logger.info("# Connection and cursor are ready!")
except Exception as e:
    logger.critical(f"# Could not connect to the database because: {e}")
    logger.info("#################################################")
    raise SystemExit

CommandPalette = {}
logger.info("Loading command palette from database!")
try:
    cursor.execute("SELECT * FROM tools")
    for _ in cursor.fetchall():

        CommandPalette[_[0]] = {"TaskList":_[1].split(','),"Path":_[2]}
except Exception as e:
    logger.critical(f"Database error, cannot load the command palette because: {e}")
    logger.info(f"#########################################")
    raise SystemExit

logger.info(f"### Execution ###")
logger.info("Checking for any available requests.")

try:
    cursor.execute(f"""SELECT * FROM requests WHERE "Worker" = '{worker}' and "Status"='SUBMITTED'""")
    quests = [ _ for _ in cursor.fetchall()]
except Exception as e:
    logger.critical(f"# Could not query quests for worker: {worker} because, {e}")
    logger.info("#################################################")
    raise SystemExit

if quests:
    logger.info(f"A total of {len(quests)} quest(s) are waiting to be completed!")
    for q in quests:
        solution = q[3]
        datesubmitted = q[4]
        requestor = q[1]
        logger.info(f"Checking if submitted request:{solution}, is supported, date of submission: {datesubmitted}")
        
        if solution in CommandPalette:
            logger.info(f"Checking if the path is available.")
            if os.path.isdir(CommandPalette[solution]['Path']):
                #logger.info("Path is available, setting task status to PENDING")
                #try:
                #    cursor.execute(f"""UPDATE requests SET "Status"='PENDING' WHERE "TaskID"={q[0]}""")
                #    conn.commit()
                #    logger.info(f"Successfully updated status!")
                #except Exception as e:
                #    logger.critical(f"Failed to update task status because: {e}, skipping the rest of the process!")
                #    continue
                print(q)
                task = q[4]
                targets = q[5]
                extraargs = q[6]
                logger.info(f"Executing solution: {solution}, with task: {task}, on target(s): {targets}, with extra argument(s): {extraargs}")
                PerMachine = []
                if task and not targets and not extraargs:
                    logger.info("Local command!")
                    PerMachine.append([f"invoke {task}",worker])
                elif task and targets and not extraargs:
                    logger.info("Machine without extra arguments")
                    if len(targets.split(','))> 1:
                        for m in targets.split(','):
                            PerMachine.append([f"invoke {task} --Machine '{m}'",m])
                    else:
                        PerMachine.append([f"invoke {task} --Machine '{targets}'",targets])
                elif task and not targets and extraargs:
                    logger.info(f"Local Command with extraargs!")
                    PerMachine.append([f"invoke {task} {extraargs}",worker])
                elif task and targets and extraargs:
                    logger.info("Machine with extraarguments!")
                    if len(targets.split(','))> 1:
                        for m in targets.split(','):
                            PerMachine.append([f"invoke {task} --Machine '{m}' {extraargs}",m])
                    else:
                        PerMachine.append([f"invoke {task} --Machine '{targets}' {extraargs}",targets])
                else:
                    logger.critical(f"Cannot do anything with this request: {task}, {targets}, {extraargs}")
                    continue
                logger.info(PerMachine)
                msg = MIMEMultipart('mixed')
                subject = f"GodMode :: {worker} :: Requestor :: {requestor} :: "
                Errors = 0
                Results = {}
                for _ in PerMachine:
                    command = _[0]
                    target = _[1]
                    Results[target] = {"ExitCode" : 0, "Result":""}
                    sentinel = subprocess.Popen(command,shell=True,cwd = CommandPalette[solution]['Path'],stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
                    (output, errors) = sentinel.communicate()
                    tmp = output.decode()
                    
                    Results[target]["ExitCode"] += sentinel.returncode
                    Results[target]["Result"] = tmp                    
                    logger.info(f"The output of the execution on {target}")
                    for line in tmp.split('\n'):
                        logger.info(f"{line}")
                logger.info(Results)
                FinalExitCode = 0
                for r in Results:
                    FinalExitCode += Results[r]["ExitCode"]

                if FinalExitCode == 0:
                    subject += "SUCCESS"
                    logger.info("The quest has completed successfully, updating result and status in database!")
                    try:
                        cursor.execute(f"""UPDATE requests SET "Status"='SUCCESS', "Result"='Successfully completed!s' WHERE "TaskID"={q[0]}""")
                        conn.commit()
                        logger.info(f"Successfully updated status!")
                    except Exception as e:
                        logger.critical(f"Failed to update task status because: {e}, skipping the rest of the process!")
                else:
                    subject += "FAILURE"
                    logger.info("The quest has failed, updating result and status in database!")
                    try:
                        cursor.execute(f"""UPDATE requests SET "Status"='FAILURE', "Result"='Error occured during execution!' WHERE "TaskID"={q[0]}""")
                        conn.commit()
                        logger.info(f"Successfully updated status!")
                    except Exception as e:
                        logger.critical(f"Failed to update task status because: {e}, skipping the rest of the process!")
                
                FinalResult = ""
                for r in Results:
                    FinalResult += Results[r]["Result"]

                logger.info(f"Updating the Result column!")
                FinalResult = FinalResult.replace("""'""","""''""")
                try:
                    cursor.execute(f"""UPDATE requests SET "Result"='{FinalResult}' WHERE "TaskID"={q[0]}""")
                    conn.commit()
                    logger.info(f"Successfully updated status!")
                except Exception as e:
                    logger.critical(f"Failed to update task result because: {e}, skipping the rest of the process!")
                logger.info(f"Mailing results to the requestor!")                               
                msg['Subject'] = subject
                msg['From'] = 'cnods@itron-hosting.com'
                msg['To'] = requestor
                msg['Cc'] = os.getenv('GMADMIN')
                HTML = "<html>"
                HTML += f"<h4>Dear {requestor},</h4>"
                HTML += "Below are the details of your request!"
                HTML += f"<p><strong>The status of your request is:</strong> {subject.split('::')[-1]}<br><strong>Solution:</strong> {solution}<br><strong>Task:</strong> {task}<br><strong>Targets:</strong> {targets if targets else worker}<br><strong>Extra arguments:</strong> {extraargs if extraargs else 'N.A.'}</p>"
                HTML += "<p>Below is the output of the execution!</p>"
                HTML += "<hr>"
                for r in Results:
                    HTML += f"<p><strong>Target:</strong> {r}, <strong>exit code:</strong> {Results[r]['ExitCode']}</p>"
                    Results[r]['Result'] = html.escape(Results[r]['Result']).replace('\n',"<br>")
                    HTML += f"<p>{Results[r]['Result']}</p>"
                HTML += "<hr>"
                HTML += "<p>Best Regards,<br>GMSAutomation</p>"
                HTML += "</html>"
                Final = MIMEText(HTML, 'html')
                msg.attach(Final)
                logger.info("# Trying to notify admin via e-mail!")
                context = ssl.create_default_context()
                with smtplib.SMTP(os.getenv('SMTPSERVER'), os.getenv('SMTPPORT')) as server:
                    server.ehlo()
                    server.starttls(context=context)
                    server.ehlo()
                    server.login(os.getenv('GMAIL_USER'), os.getenv('GMAIL_PASS'))
                    server.sendmail(msg['From'], msg['To'].split(','), msg.as_string())                  
                #try:
                #    s = smtplib.SMTP(tobeusedSMTP,'25')
                #    s.sendmail(msg['From'], msg['To'].split(','), msg.as_string())
                #    s.quit()
                #    logger.info("# Successfully sent the e-mail!")
                #except Exception as e:
                #    logger.critical(f"Failed to send the e-mail because: {e}")
            else:
                logger.critical(f"Cannot find the local path: {CommandPalette[solution]['Path']}, on worker: {worker}")
        else:
            logger.critical(f"The submitted request cannot be completed as it is missing from the solution palette: {','.join(CommandPalette.keys())}")
else:
    logger.info(f"There are no pending SUBMITTED for this worker.")


logger.info(f"Checking if there are any tasks stuck in PENDING state beyond expiration of {pendingtimeout} seconds!")
try:
    cursor.execute(f"""SELECT * FROM requests WHERE "Worker" = '{worker}' and "Status"='PENDING'""")
    pending = [ _ for _ in cursor.fetchall()]
except Exception as e:
    logger.critical(f"# Could not query quests for worker: {worker} because, {e}")
    logger.info("#################################################")
    raise SystemExit

expired = []
logger.info("Verifying if pending tasks have expired!")
for p in pending:
    subtime = datetime.strptime(str(p[4]), '%Y-%m-%d %H:%M:%S.%f')
    diff = datetime.now() - subtime
    if diff.seconds > pendingtimeout:
        logger.info(f"This transaction is expired: ID: {p[0]}, Submission Date: {str(p[4])}, Requester: {p[1]}, Solution: {p[3]}, Task: {p[5]}, Targets {p[6]}")
        try:
            cursor.execute(f"""UPDATE requests SET "Status"='EXPIRED', "Result"='Expired transaction!' WHERE "TaskID"={p[0]}""")
            conn.commit()
            logger.info(f"Successfully updated Status!")
            expired.append(p)
        except Exception as e:
            logger.critical(f"Failed to update task status because: {e}, skipping the rest of the process!")
    else:
        logger.info(f"This transaction is NOT expired, leaving it pending: ID: {p[0]}, Submission Date: {str(p[4])}, Requester: {p[1]}, Solution: {p[3]}, Task: {p[5]}, Targets {p[6]}</li>")

if expired:
    logger.info(f"A total of {len(expired)} quest(s) are in EXPIRED state!")
    msg = MIMEMultipart('mixed')
    subject = f"GodMode :: {worker} :: Total of {len(expired)} quest(s) are in EXPIRED state!"
    msg['Subject'] = subject
    msg['From'] = 'cnods@itron-hosting.com'
    msg['To'] = os.getenv('GMADMIN')

    HTML = "<html>"
    HTML += "<h5>Dear Admin,</h5>"
    HTML += f"<p>List of expired:</p>"
    HTML += "<ul>"
    for p in expired:
        HTML += f"<li>ID: {p[0]}, Submission Date: {str(p[4])}, Requester: {p[1]}, Solution: {p[3]}, Task: {p[5]}, Targets {p[6]}</li>"
    HTML += "</ul>"

    HTML += "<p>Best Regards,<br>GMSAutomation</p>"
    HTML += "</html>"
    Final = MIMEText(HTML, 'html')
    msg.attach(Final)
    logger.info("# Trying to notify admin via e-mail!")

    context = ssl.create_default_context()
    with smtplib.SMTP(os.getenv('SMTPSERVER'), os.getenv('SMTPPORT')) as server:
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        server.login(os.getenv('GMAIL_USER'), os.getenv('GMAIL_PASS'))
        server.sendmail(msg['From'], msg['To'].split(','), msg.as_string())    

else:
    logger.info("There are no expired tasks!")

logger.info("This is the end of execution, closing DB connection!")
conn.close()
logger.info(f"Removing pidfile: {PIDFILE}")
if os.path.isfile(PIDFILE):
    os.remove(PIDFILE)
    logger.info(f"Pidfile is gone!")
logger.info("#################################################")