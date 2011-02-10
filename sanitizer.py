#!/usr/bin/env python

import re
import unicodedata

import AsciiDammit

__author__ = "Erik Smartt"
__copyright__ = "Copyright 2010, Erik Smartt"
__license__ = "MIT"
__version__ = "0.3"
__url__ = "http://github.com/smartt/pysanitizer"

# --
def ascii_dammit(s):
    """Tries really hard to return an ASCII string."""

    s = unicode(s, 'utf-8', 'replace')

    # EBS: Trying to replace before normalizing can raise a UnicodeDecodeError
    #s = s.replace(u'\u201c', '"')
    #s = s.replace(u'\u201d', '"')
    #s = s.replace(u'\u2014', '--')
    #s = s.replace(u'\u2019', "'")

    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore')
    #s = unicodedata.normalize('NFKD', s).encode('ascii', 'replace')

    return AsciiDammit.asciiDammit(s)

# --
def html_dammit(s):
    return AsciiDammit.htmlDammit(s)

# --
def compress_whitespace(s):
    """
    Convert whitespace (ie., spaces, tabs, linebreaks, etc.) to spaces, and
    compress multiple-spaces into single-spaces.

    >>> compress_whitespace('   Oh   hai    there   ')
    'Oh hai there'

    >>> compress_whitespace('      ')
    ''

    """
    # Cast to string
    s = str(s).strip()

    # Sanity check
    if (len(s) == 0):
        return ''

    s = re.sub(r'\s', ' ', s)
    s = re.sub(r' +', ' ', s)

    return s.strip()

# --
def strip_and_compact_str(s):
    """
    Remove tags, spaces, etc.  Basically, if someone passed in multiple
    paragraphs, we're going to compact the text into a single block.

    >>> strip_and_compact_str('Hi there. <br /><br />Whats up?')
    'Hi there. Whats up?'

    >>> strip_and_compact_str('     Hi         there. <br />    <br />  Whats    up?   ')
    'Hi there. Whats up?'

    >>> strip_and_compact_str('\t  Hi \r there. <br /><br />Whats up?')
    'Hi there. Whats up?'

    >>> strip_and_compact_str('<p>Hi there. <br /><br />Whats up?</p>')
    'Hi there. Whats up?'

    >>> strip_and_compact_str("Hi there.  Let's have tea.")
    "Hi there. Let's have tea."

    >>> strip_and_compact_str("<i>Hi there.</i><i>Let's have tea.")
    "Hi there.Let's have tea."

    """
    # Strip tabs
    s = strip_tags(s)

    # Compact whitespace
    s = compress_whitespace(s)

    try:
        # Append a trailing period if there's no ending punctuation.
        if (s[-1] not in ('.', '!', ')', '?')):
            s = '%s.' % (s)
    except IndexError:
        # Odds are len(s) == 0
        pass

    return s

# --
def escape(html):
    """
    Returns the given HTML with ampersands, quotes and carets encoded.

    >>> escape('<b>oh hai</b>')
    '&lt;b&gt;oh hai&lt;/b&gt;'

    >>> escape("Quote's Test")
    'Quote&#39;s Test'

    """
    return ("%s" % (html)).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;')

# --
def extract_numbers_safe(s):
    """
    >>> extract_numbers_safe('123')
    '123'

    >>> extract_numbers_safe('1a2b3c')
    '123'

    >>> extract_numbers_safe('1-2-3-')
    '123'

    >>> extract_numbers_safe(None)
    ''

    """
    return ''.join([i for i in escape(s) if (i>='0') and (i<='9')])

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

# --
def slugify(s):
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

    value = re.sub('[^\w\s-]', '', s).strip().lower()
    value = re.sub('[-\s]+', '-', value)
    value = re.sub('[_\s]+', '-', value)
    return value

# --
def sql_safe(s):
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
    if (s == None):
        return None

    s = strip_tags(s).replace(';', '').replace('--', ' ').replace('/', '').replace('*', '').replace('/', '').replace("'", "\'").replace('"', '\"').strip()
    return s

# --
def strip_tags(value):
    """
    Returns the given HTML with all tags stripped.

    >>> strip_tags('<b>oh hai</b>')
    'oh hai'

    >>> strip_tags(None)

    >>> strip_tags('<p>oh hai.</p><p>goodbye</p>')
    'oh hai. goodbye'

    >>> strip_tags('<i>oh hai.</i><i>goodbye</i>')
    'oh hai.goodbye'

    """
    if value == None:
        return None

    s = re.sub(r'<\/?p>', ' ', '%s' % value)
    s = re.sub(r'<[^>]*?>', '', s)
    return compress_whitespace(s)


def sub_greeks(s):
    # The following list was seeded using a dictionary within the ReportLab paraparser.py
    # library, licensed under a BSD License.  For more, see: http://www.reportlab.com/software/opensource/

    sublist = {
        '\xc2\xa0': 'nbsp',
        '\xc2\xa1': 'iexcl',
        '\xc2\xa2': 'cent',
        '\xc2\xa3': 'pound',
        '\xc2\xa4': 'curren',
        '\xc2\xa5': 'yen',
        '\xc2\xa6': 'brvbar',
        '\xc2\xa7': 'sect',
        '\xc2\xa8': 'uml',
        '\xc2\xa9': 'copy',
        '\xc2\xaa': 'ordf',
        '\xc2\xab': 'laquo',
        '\xc2\xac': 'not',
        '\xc2\xad': 'shy',
        '\xc2\xae': 'reg',
        '\xc2\xaf': 'macr',
        '\xc2\xb0': 'deg',
        '\xc2\xb1': 'plusmn',
        '\xc2\xb2': 'sup2',
        '\xc2\xb3': 'sup3',
        '\xc2\xb4': 'acute',
        '\xc2\xb5': 'micro',
        '\xc2\xb5': 'mu',
        '\xc2\xb6': 'para',
        '\xc2\xb7': 'middot',
        '\xc2\xb8': 'cedil',
        '\xc2\xb9': 'sup1',
        '\xc2\xba': 'ordm',
        '\xc2\xbb': 'raquo',
        '\xc2\xbc': 'frac14',
        '\xc2\xbd': 'frac12',
        '\xc2\xbe': 'frac34',
        '\xc2\xbf': 'iquest',
        '\xc3\x80': 'Agrave',
        '\xc3\x81': 'Aacute',
        '\xc3\x82': 'Acirc',
        '\xc3\x83': 'Atilde',
        '\xc3\x84': 'Auml',
        '\xc3\x85': 'Aring',
        '\xc3\x86': 'AElig',
        '\xc3\x87': 'Ccedil',
        '\xc3\x88': 'Egrave',
        '\xc3\x89': 'Eacute',
        '\xc3\x8a': 'Ecirc',
        '\xc3\x8b': 'Euml',
        '\xc3\x8c': 'Igrave',
        '\xc3\x8d': 'Iacute',
        '\xc3\x8e': 'Icirc',
        '\xc3\x8f': 'Iuml',
        '\xc3\x90': 'ETH',
        '\xc3\x91': 'Ntilde',
        '\xc3\x92': 'Ograve',
        '\xc3\x93': 'Oacute',
        '\xc3\x94': 'Ocirc',
        '\xc3\x95': 'Otilde',
        '\xc3\x96': 'Ouml',
        '\xc3\x97': 'times',
        '\xc3\x98': 'Oslash',
        '\xc3\x99': 'Ugrave',
        '\xc3\x9a': 'Uacute',
        '\xc3\x9b': 'Ucirc',
        '\xc3\x9c': 'Uuml',
        '\xc3\x9d': 'Yacute',
        '\xc3\x9e': 'THORN',
        '\xc3\x9f': 'szlig',
        '\xc3\xa0': 'agrave',
        '\xc3\xa1': 'aacute',
        '\xc3\xa2': 'acirc',
        '\xc3\xa3': 'atilde',
        '\xc3\xa4': 'auml',
        '\xc3\xa5': 'aring',
        '\xc3\xa6': 'aelig',
        '\xc3\xa7': 'ccedil',
        '\xc3\xa8': 'egrave',
        '\xc3\xa9': 'eacute',
        '\xc3\xaa': 'ecirc',
        '\xc3\xab': 'euml',
        '\xc3\xac': 'igrave',
        '\xc3\xad': 'iacute',
        '\xc3\xae': 'icirc',
        '\xc3\xaf': 'iuml',
        '\xc3\xb0': 'eth',
        '\xc3\xb1': 'ntilde',
        '\xc3\xb2': 'ograve',
        '\xc3\xb3': 'oacute',
        '\xc3\xb4': 'ocirc',
        '\xc3\xb5': 'otilde',
        '\xc3\xb6': 'ouml',
        '\xc3\xb7': 'divide',
        '\xc3\xb8': 'oslash',
        '\xc3\xb9': 'ugrave',
        '\xc3\xba': 'uacute',
        '\xc3\xbb': 'ucirc',
        '\xc3\xbc': 'uuml',
        '\xc3\xbd': 'yacute',
        '\xc3\xbe': 'thorn',
        '\xc3\xbf': 'yuml',
        '\xc5\x92': 'OElig',
        '\xc5\x93': 'oelig',
        '\xc5\xa0': 'Scaron',
        '\xc5\xa1': 'scaron',
        '\xc5\xb8': 'Yuml',
        '\xc6\x92': 'fnof',
        '\xcb\x86': 'circ',
        '\xcb\x9c': 'tilde',
        '\xce\x91': 'Alpha',
        '\xce\x92': 'Beta',
        '\xce\x93': 'Gamma',
        '\xce\x95': 'Epsilon',
        '\xce\x96': 'Zeta',
        '\xce\x97': 'Eta',
        '\xce\x98': 'Theta',
        '\xce\x99': 'Iota',
        '\xce\x9a': 'Kappa',
        '\xce\x9b': 'Lambda',
        '\xce\x9c': 'Mu',
        '\xce\x9d': 'Nu',
        '\xce\x9e': 'Xi',
        '\xce\x9f': 'Omicron',
        '\xce\xa0': 'Pi',
        '\xce\xa1': 'Rho',
        '\xce\xa3': 'Sigma',
        '\xce\xa4': 'Tau',
        '\xce\xa5': 'Upsilon',
        '\xce\xa6': 'Phi',
        '\xce\xa7': 'Chi',
        '\xce\xa8': 'Psi',
        '\xce\xb1': 'alpha',
        '\xce\xb2': 'beta',
        '\xce\xb3': 'gamma',
        '\xce\xb4': 'delta',
        '\xce\xb5': 'epsilon',
        '\xce\xb5': 'epsiv',
        '\xce\xb6': 'zeta',
        '\xce\xb7': 'eta',
        '\xce\xb8': 'theta',
        '\xce\xb9': 'iota',
        '\xce\xba': 'kappa',
        '\xce\xbb': 'lambda',
        '\xce\xbd': 'nu',
        '\xce\xbe': 'xi',
        '\xce\xbf': 'omicron',
        '\xcf\x80': 'pi',
        '\xcf\x81': 'rho',
        '\xcf\x82': 'sigmaf',
        '\xcf\x82': 'sigmav',
        '\xcf\x83': 'sigma',
        '\xcf\x84': 'tau',
        '\xcf\x85': 'upsilon',
        '\xcf\x86': 'phis',
        '\xcf\x87': 'chi',
        '\xcf\x88': 'psi',
        '\xcf\x89': 'omega',
        '\xcf\x91': 'thetasym',
        '\xcf\x91': 'thetav',
        '\xcf\x92': 'upsih',
        '\xcf\x95': 'phi',
        '\xcf\x96': 'piv',
        '\xe2\x80\x82': 'ensp',
        '\xe2\x80\x83': 'emsp',
        '\xe2\x80\x89': 'thinsp',
        '\xe2\x80\x8c': 'zwnj',
        '\xe2\x80\x8d': 'zwj',
        '\xe2\x80\x8e': 'lrm',
        '\xe2\x80\x8f': 'rlm',
        '\xe2\x80\x93': 'ndash',
        '\xe2\x80\x94': 'mdash',
        '\xe2\x80\x98': 'lsquo',
        '\xe2\x80\x99': 'rsquo',
        '\xe2\x80\x9a': 'sbquo',
        '\xe2\x80\x9c': 'ldquo',
        '\xe2\x80\x9d': 'rdquo',
        '\xe2\x80\x9e': 'bdquo',
        '\xe2\x80\xa0': 'dagger',
        '\xe2\x80\xa1': 'Dagger',
        '\xe2\x80\xa2': 'bull',
        '\xe2\x80\xa6': 'hellip',
        '\xe2\x80\xb0': 'permil',
        '\xe2\x80\xb2': 'prime',
        '\xe2\x80\xb3': 'Prime',
        '\xe2\x80\xb9': 'lsaquo',
        '\xe2\x80\xba': 'rsaquo',
        '\xe2\x81\x84': 'frasl',
        '\xe2\x82\xac': 'euro',
        '\xe2\x84\x91': 'image',
        '\xe2\x84\x98': 'weierp',
        '\xe2\x84\x9c': 'real',
        '\xe2\x84\xa6': 'Omega',
        '\xe2\x84\xb5': 'alefsym',
        '\xe2\x86\x90': 'larr',
        '\xe2\x86\x91': 'uarr',
        '\xe2\x86\x92': 'rarr',
        '\xe2\x86\x93': 'darr',
        '\xe2\x86\x94': 'harr',
        '\xe2\x86\xb5': 'crarr',
        '\xe2\x87\x90': 'lArr',
        '\xe2\x87\x91': 'uArr',
        '\xe2\x87\x92': 'rArr',
        '\xe2\x87\x93': 'dArr',
        '\xe2\x87\x94': 'hArr',
        '\xe2\x88\x80': 'forall',
        '\xe2\x88\x82': 'part',
        '\xe2\x88\x83': 'exist',
        '\xe2\x88\x85': 'empty',
        '\xe2\x88\x86': 'Delta',
        '\xe2\x88\x87': 'nabla',
        '\xe2\x88\x88': 'isin',
        '\xe2\x88\x89': 'notin',
        '\xe2\x88\x8b': 'ni',
        '\xe2\x88\x8f': 'prod',
        '\xe2\x88\x91': 'sum',
        '\xe2\x88\x92': 'minus',
        '\xe2\x88\x97': 'lowast',
        '\xe2\x88\x9a': 'radic',
        '\xe2\x88\x9d': 'prop',
        '\xe2\x88\x9e': 'infin',
        '\xe2\x88\xa0': 'ang',
        '\xe2\x88\xa7': 'and',
        '\xe2\x88\xa8': 'or',
        '\xe2\x88\xa9': 'cap',
        '\xe2\x88\xaa': 'cup',
        '\xe2\x88\xab': 'int',
        '\xe2\x88\xb4': 'there4',
        '\xe2\x88\xbc': 'sim',
        '\xe2\x89\x85': 'cong',
        '\xe2\x89\x88': 'asymp',
        '\xe2\x89\xa0': 'ne',
        '\xe2\x89\xa1': 'equiv',
        '\xe2\x89\xa4': 'le',
        '\xe2\x89\xa5': 'ge',
        '\xe2\x8a\x82': 'sub',
        '\xe2\x8a\x83': 'sup',
        '\xe2\x8a\x84': 'nsub',
        '\xe2\x8a\x86': 'sube',
        '\xe2\x8a\x87': 'supe',
        '\xe2\x8a\x95': 'oplus',
        '\xe2\x8a\x97': 'otimes',
        '\xe2\x8a\xa5': 'perp',
        '\xe2\x8b\x85': 'sdot',
        '\xe2\x8c\xa9': 'lang',
        '\xe2\x8c\xaa': 'rang',
        '\xe2\x97\x8a': 'loz',
        '\xe2\x99\xa0': 'spades',
        '\xe2\x99\xa3': 'clubs',
        '\xe2\x99\xa5': 'hearts',
        '\xe2\x99\xa6': 'diams',
        '\xef\xa3\xa5': 'oline',
        '\xef\xa3\xaa': 'trade',
        '\xef\xa3\xae': 'lceil',
        '\xef\xa3\xb0': 'lfloor',
        '\xef\xa3\xb9': 'rceil',
        '\xef\xa3\xbb': 'rfloor',
    }

    for k in sublist:
        s = s.replace(k, '&%s;' % sublist[k])

    return s


def price_like(s):
    """
    >>> price_like('')
    ''

    >>> price_like('$19.95')
    '19.95'

    >>> price_like('19.95')
    '19.95'

    >>> price_like('19.95345')
    '19.95'

    >>> price_like('19.5')
    '19.50'

    >>> price_like('19.')
    '19.00'

    >>> price_like('19')
    '19.00'

    >>> price_like('19.5.34')
    ''

    >>> price_like('.19')
    '0.19'

    """
    if s.strip() == '':
        return ''

    parts = s.split('.')

    if not len(parts): # == 0
        # This shouldn't happen. split() should always return at least a one-item list
        return ''

    if len(parts) == 2:
        dollars = extract_numbers_safe(parts[0].strip())
        cents = extract_numbers_safe(parts[1].strip())

    elif len(parts) == 1:
        dollars = extract_numbers_safe(parts[0].strip())
        cents = '00'

    else:
        return ''

    if dollars == '':
        dollars = '0'

    if len(cents) == 2:
        pass

    elif len(cents) > 2:
        # Change '12345' to '12'
        cents = cents[:2]

    elif len(cents) == 1:
        # Chagne '5' to '50'
        cents = '%s0' % cents

    else:
        # Change '' to '00'
        cents = '00'

    return "%s.%s" % (dollars, cents)


## ---------------------
if __name__ == "__main__":
    import doctest
    print "Testing..."
    doctest.testmod()
    print "Done."
