"""
The module implements a pyparsing - based special-purpose RTF parser
specifically for extracting HTML from RTF contained within a TNEF
attachment.
"""

import sys
from logging import critical

from pyparsing import Optional, Literal, Word, Group
from pyparsing import Suppress, Combine, replaceWith
from pyparsing import alphas, nums, printables, alphanums
from pyparsing import restOfLine, oneOf, OneOrMore, ZeroOrMore
from pyparsing import ParseException

__all__ = ("extract_html_line", "extract_html_lines", "RTFParserException", "parse", "write_html_document")

class RTFParserException(Exception):
   "indicate failed RTF parsing"

htmchars = printables.replace("<","").replace(">","").replace("\\","").replace("{","").replace("}","") + " " + "\t"

SEP = Literal(';')

BRCKT_L = Literal('{')
BRCKT_R = Literal('}')
BRCKT = BRCKT_L | BRCKT_R
BRCKT.setName("Bracket")

# basic RTF control codes, ie. "\labelname3434"
CTRL_LABEL = Combine(Word(alphas + "'") + Optional(Word(nums)))
BASE_CTRL = Combine(Literal('\\') + CTRL_LABEL)

# in some rare cases (color table declarations), control has ' ;' suffix
BASE_CTRL = Combine(BASE_CTRL + SEP) | BASE_CTRL
BASE_CTRL.setName("BaseControl")

#\*\html93394
HTM_CTRL = Combine(Literal('\\*\\') + CTRL_LABEL)
HTM_CTRL.setName("HtmlControl")

RTF_CTRL = BASE_CTRL | HTM_CTRL
RTF_CTRL.setName("Control")

RTFCODE = OneOrMore(RTF_CTRL | BRCKT)

# handle "{\*\htmltag4 \par }""
HTM_CTRL_NEWLINE = HTM_CTRL.suppress() + Literal("\\par").setParseAction(replaceWith("\n"))
HTM_CTRL_NEWLINE.suppress()

# handle "{\*\htmltag84       }"
HTM_CTRL_EMPTY = HTM_CTRL.suppress() + Word(" ").leaveWhitespace()

HTM_TXT =  OneOrMore(Word(htmchars))
HTM_CTRL_CONTENT = HTM_CTRL.suppress() + Optional(BRCKT_R).suppress() + HTM_TXT

# Both opening and closing tags and their contents
HTM_TAG = Combine(Literal("<") + Word(htmchars) + Literal(">"))
HTM_TAG.leaveWhitespace()
HTM_TAG.setName("HtmlTag")
     
#HTM_TAG_EMPTYCONTENT = Word(" ") + BRCKT_R.suppress()
HTM_TAG_PLUS_CONTENT = HTM_TAG + Optional(BRCKT_R.suppress() + HTM_TXT)
HTM_TAG_PLUS_CONTENT.leaveWhitespace()

# Text content inside HTML
HTM_CONTENT_IND = Suppress("\\htmlrtf0 ")
HTM_CONTENT = HTM_CONTENT_IND + OneOrMore(Word(htmchars))

HTM_CONTENT.setName("Html content")
HTM_CONTENT.leaveWhitespace()

RTFLINK = Suppress("HYPERLINK \"") + Word(htmchars.replace('"','')) + Literal('"').suppress()

RTF = OneOrMore(
   HTM_CTRL_CONTENT | \
   HTM_TAG_PLUS_CONTENT | \
   HTM_CONTENT |  \
   HTM_CTRL_NEWLINE | \
   #HTM_CTRL_EMPTY | \
   RTFLINK.suppress() | \
   RTF_CTRL.suppress() | \
   BRCKT.suppress()
)  


def parse(rtfstring):
   "return parse result as string"
   try:
      result = RTF.parseString(rtfstring)
   except ParseException, e:
      raise RTFParserException("could not parse '%s'... : %s" % (rtfstring[:30], e))
   return "".join(result)
      
   
def extract_html_line(rtfline):
   "extract a single line of HTML embedded in RTF"
   return rtfline if rtfline.isspace() else parse(rtfline)
   
   
def extract_html_lines(rtffile):
   "extract a full HTML document embedded in RTF"

   for i, l in enumerate(rtffile):
      try:
         if l:
            result = extract_html_line(l)
      except RTFParserException, e:
         raise RTFParserException("line %i: %s" % (i, e))
         
      if result:
         yield result

   
def write_html_document(sourcefilename, htmlfilename):
   "convenience for writing html out from rtf"
   src = open(sourcefilename)
   htmlfile = open(htmlfilename, "w")
   for l in extract_html_lines(src):
      htmlfile.write(l)
   src.close()
   htmlfile.close()
   
