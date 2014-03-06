
import sys
sys.path.append('./lib')

import pystache
import io, re
import bottle
from bottle import Bottle, request, response

app = Bottle()
bottle.debug(True)

class ParseError(Exception):
  def __init__(self, msg):
    self.msg = msg
  def __str__(self):
    return self.msg

def render(filename, data):
  return pystache.render(open(filename, 'r').read(), data)

def numerical_ok(line):
  return re.match('\d*', line.strip())

def timing_ok(line):
  return re.match('\d\d:\d\d:\d\d,\d\d\d --> \d\d:\d\d:\d\d,\d\d\d', line.strip())

def parse(input):
  output = io.StringIO() 
  buffer = []
  for lnum, iline in enumerate(input):
    #print(lnum, iline)
    if iline.strip() != "": 
      buffer.append(iline.decode('UTF-8'))
    else:
      if len(buffer)>2:
        if not numerical_ok(buffer[0]) or not timing_ok(buffer[1]):
          raise ParseError("Error on line: %d Malfomed caption"%(lnum+1) )
        buffer = buffer[2:]
        for oline in buffer:
          output.write(oline)
      print(buffer)
      buffer = []
  output.seek(0)
  return output

@app.route('/')
def home():
  return render("templates/index.html", {})

@app.error(404)
def error_404(error):
  return render("templates/404.html", {})

@app.route('/upload', method='POST')
def do_upload():
  upload = request.files.get('upload')
  error = None
  output = None
  try:
    output = parse(upload.file).read() 
  except ParseError as err:
    error = str(err)
  return render("templates/upload.html", {
    'transcript': output,
    'error':error
  })
