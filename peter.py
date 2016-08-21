#!/usr/bin/env python

import sys, os, time, atexit
from signal import SIGTERM
import logging, logging.handlers
import ConfigParser
from time import gmtime, strftime
from flask import Flask, request, jsonify

CONFIG_FILE = '/etc/peter.conf'
LOG_FILE = '/var/log/peter.log'
config = ConfigParser.ConfigParser()
config.read(CONFIG_FILE)
HTTP_LISTEN = config.get("global", "listen")
HTTP_PORT = config.get("global", "port")

peter_logger = logging.getLogger('PeterService')
peter_logger.setLevel(logging.DEBUG)
logging.basicConfig(filename = LOG_FILE, filemode = 'a',\
                     level = logging.DEBUG,\
                     format = '%(asctime)s - %(levelname)s: %(message)s',\
                     datefmt = '%d/%m/%Y %I:%M:%S %p')


class Daemon:
  def __init__(self, pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
    self.stdin = stdin
    self.stdout = stdout
    self.stderr = stderr
    self.pidfile = pidfile

  def daemonize(self):
    try:
      pid = os.fork()
      if pid > 0:
        sys.exit(0)
    except OSError, e:
      sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
      sys.exit(1)

    os.chdir("/")
    os.setsid()
    os.umask(0)

    try:
      pid = os.fork()
      if pid > 0:
        sys.exit(0)
    except OSError, e:
      sys.stderr.write("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
      sys.exit(1)

    sys.stdout.flush()
    sys.stderr.flush()
    si = file(self.stdin, 'r')
    so = file(self.stdout, 'a+')
    se = file(self.stderr, 'a+', 0)
    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())

    atexit.register(self.delpid)
    pid = str(os.getpid())
    file(self.pidfile,'w+').write("%s\n" % pid)

  def delpid(self):
    os.remove(self.pidfile)

  def start(self):
    try:
      pf = file(self.pidfile,'r')
      pid = int(pf.read().strip())
      pf.close()
    except IOError, e:
      pid = None

    if pid:
      message = "pidfile %s already exist. Daemon already running?\n"
      sys.stderr.write(message % self.pidfile)
      sys.exit(1)

    self.daemonize()
    self.run()

  def stop(self):
    try:
      pf = file(self.pidfile,'r')
      pid = int(pf.read().strip())
      pf.close()
    except IOError:
      pid = None

    if not pid:
      message = "pidfile %s does not exist. Daemon not running?\n"
      sys.stderr.write(message % self.pidfile)
      return
    try:
      while 1:
        os.kill(pid, SIGTERM)
        time.sleep(0.1)
    except OSError, err:
      err = str(err)

    if err.find("No such process") > 0:
      if os.path.exists(self.pidfile):
        os.remove(self.pidfile)
    else:
      print str(err)
      sys.exit(1)

  def restart(self):
    self.stop()
    self.start()

  def run(self):
    """
    You should override this method when you subclass Daemon. It will be called after the process has been
    daemonized by start() or restart().
    """


class PeterDaemon(Daemon):
  def run(self):
    while True:
      app = Flask(__name__)
      @app.route('/')
      @app.route('/index')
      def index():
        return """
          <h1>PETER SERVICE</h1>
          <h3>SIMPLE HOW-TO:</h3>
          <p>curl -H "Content-Type: application/json" -X POST -d '{"simple": "post"}' 0.0.0.0:80</p>
          <p>Log: /var/log/peter.log</p>
          <p>Pid: /var/run/peter.pid</p>
          <p>Config: /etc/peter.conf</p>
          """

      @app.route('/', methods = ['POST'])
      def post():
        json = request.json
        get_time = strftime("%H:%M:%S", gmtime())
        get_date = date=strftime("%Y-%m-%d", gmtime())
        resp = jsonify(time=get_time, date=get_date, post_request=json)
        return resp

      app.run(debug = False, port = HTTP_PORT, host = HTTP_LISTEN)


if __name__ == "__main__":
  daemon = PeterDaemon('/var/run/peter.pid')
  if len(sys.argv) == 2:
    if 'start' == sys.argv[1]:
      daemon.start()
    elif 'stop' == sys.argv[1]:
      daemon.stop()
    elif 'restart' == sys.argv[1]:
      daemon.restart()
    else:
      print "Unknown command"
      sys.exit(2)
    sys.exit(0)
  else:
    print "usage: %s start|stop|restart" % sys.argv[0]
    sys.exit(2)

