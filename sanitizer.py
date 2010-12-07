#!/usr/bin/env python

import re

__author__ = "Erik Smartt"
__copyright__ = "Copyright 2010, Erik Smartt"
__license__ = "MIT"
__version__ = "0.3"
__url__ = "http://github.com/smartt/pysanitizer"

def slugify(str):
  """
  >>> slugify('oh hai')
  'oh-hai'

  >>> slugify('OH HAI')
  'oh-hai'

  >>> slugify('"oh_hai!"')
  'oh-hai'

  >>> slugify("oh_hai!'s")
  'oh-hais'
  """

  value = re.sub('[^\w\s-]', '', str).strip().lower()
  value = re.sub('[-\s]+', '-', value)
  value = re.sub('[_\s]+', '-', value)
  return value

def escape(html):
  """
  Returns the given HTML with ampersands, quotes and carets encoded.

  >>> escape('<b>oh hai</b>')
  '&lt;b&gt;oh hai&lt;/b&gt;'

  >>> escape("Quote's Test")
  'Quote&#39;s Test'

  """
  return ("%s" % (html)).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;')

def strip_tags(value):
  """
  Returns the given HTML with all tags stripped.

  >>> strip_tags('<b>oh hai</b>')
  'oh hai'

  >>> strip_tags(None)


  """
  if value == None:
    return None

  return re.sub(r'<[^>]*?>', '', '%s' % value)

# --
def sql_safe(str):
  """
  >>> sql_safe(None)


  >>> sql_safe('hi there')
  'hi there'

  >>> sql_safe('foo/')
  'foo'

  >>> sql_safe('hi -- there')
  'hi   there'

  >>> sql_safe('hi; there')
  'hi there'

  >>> sql_safe("hi' WHERE=1")
  "hi\' WHERE=1"

  >>> sql_safe('hi /* there */')
  'hi  there'
  """
  if (str == None):
    return None

  s = strip_tags(str).replace(';', '').replace('--', ' ').replace('/', '').replace('*', '').replace('/', '').replace("'", "\'").replace('"', '\"').strip()
  return s

# --
def extract_numbers_safe(str):
  """
  >>> extract_numbers_safe('123')
  '123'

  >>> extract_numbers_safe('1a2b3c')
  '123'

  >>> extract_numbers_safe(None)
  ''

  """
  return ''.join([i for i in escape(str) if (i>='0') and (i<='9')])

# --
def safe_int(arg, default=None):
  """
  >>> safe_int('0')
  0

  >>> safe_int('1')
  1

  >>> safe_int('a')

  >>> safe_int('12.3')
  123

  >>> safe_int('1a2b3c')
  123

  >>> safe_int('<1a2b3c/>')
  123

  >>> safe_int(None)


  >>> safe_int(1)
  1

  >>> safe_int(u'')


  >>> safe_int(1, None)
  1

  >>> safe_int('hi', 0)
  0

  >>> safe_int(None, 0)
  0

  >>> safe_int(None, None)


  >>> safe_int(u'', 0)
  0

  >>> safe_int(u'-1')
  -1

  """
  try:
    return int(arg)
  except:
    try:
      return int(extract_numbers_safe(arg))
    except ValueError:
      return default

# --
def safe_bool(input):
  """
  >>> safe_bool('1')
  True

  >>> safe_bool('True')
  True

  >>> safe_bool(True)
  True

  >>> safe_bool(False)
  False

  >>> safe_bool('False')
  False

  >>> safe_bool('0')
  False

  >>> safe_bool(None)
  False

  >>> safe_bool('on')
  True

  """
  if input is None:
    return False

  safe_arg = strip_tags(input)

  if safe_arg == u'0' or safe_arg == '0':
    return False

  #if safe_arg == u'on' or safe_arg == 'on':
    #return True

  elif safe_arg == u'False' or safe_arg == 'False':
    return False

  else:
    if bool(safe_arg):
      return True
    else:
      return False

#  --
def safe_split(input, delimiter='_'):
  """
  >>> safe_split('hi_there', '_')
  ['hi', 'there']

  >>> safe_split('<blink>Hai World</blink>', ' ')
  ['&lt;blink&gt;Hai', 'World&lt;/blink&gt;']

  >>> safe_split('_', '_')
  ['', '']

  """
  return escape(input).split(delimiter)


## ---------------------
if __name__ == "__main__":
  import doctest
  print "Testing..."
  doctest.testmod()
  print "Done."
