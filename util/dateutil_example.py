from dateutil.relativedelta import *
from dateutil.easter import *
from dateutil.rrule import *
from dateutil.parser import *
from datetime import *
import commands
import os
now = parse(commands.getoutput("date"))

yourdate = parse('20041215')


try:
    yourdate = dateutil.parser.parse('2004-09-15T26:17:33Z')
except ValueError:
    print 'Fout bij parsen...'
    pass



today = now.date()
year = rrule(YEARLY,bymonth=8,bymonthday=13,byweekday=FR)[0].year
rdelta = relativedelta(easter(year), today)
print "Today is:", today
print "Year with next Aug 13th on a Friday is:", year
print "How far is the Easter of that year:", rdelta
print "And the Easter of that year is:", today+rdelta
print 'mydate' , yourdate
