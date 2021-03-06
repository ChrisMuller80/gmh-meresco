## begin license ##
# 
# "Meresco Oai" are components to build Oai repositories, based on
# "Meresco Core" and "Meresco Components". 
# 
# Copyright (C) 2007-2008 SURF Foundation. http://www.surf.nl
# Copyright (C) 2007-2010 Seek You Too (CQ2) http://www.cq2.nl
# Copyright (C) 2007-2009 Stichting Kennisnet Ict op school. http://www.kennisnetictopschool.nl
# Copyright (C) 2009 Delft University of Technology http://www.tudelft.nl
# Copyright (C) 2009 Tilburg University http://www.uvt.nl
# Copyright (C) 2010 Maastricht University Library http://www.maastrichtuniversity.nl/web/Library/home.htm
# Copyright (C) 2011 Nederlands Instituut voor Beeld en Geluid http://instituut.beeldengeluid.nl
# Copyright (C) 2011-2012 Seecr (Seek You Too B.V.) http://seecr.nl
# 
# This file is part of "Meresco Oai"
# 
# "Meresco Oai" is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# "Meresco Oai" is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with "Meresco Oai"; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
# 
## end license ##

from cgi import parse_qs

from meresco.core import Transparent, Observable
from weightless.core import be, compose
from oaiidentify import OaiIdentify
from meresco.oai.oailist import OaiList
from meresco.oai.oaigetrecord import OaiGetRecord
from meresco.oai.oailistmetadataformats import OaiListMetadataFormats
from meresco.oai.oailistsets import OaiListSets
from meresco.oai.oaierror import OaiError
from meresco.oai.oaiidentifierrename import OaiIdentifierRename
from meresco.oai.oairecord import OaiRecord

class OaiPmh(object):
    def __init__(self, repositoryName, adminEmail, repositoryIdentifier=None, batchSize=OaiList.DEFAULT_BATCH_SIZE, supportXWait=False, fixIdentifyBaseURL=False):
        outside = Transparent() if repositoryIdentifier == None else OaiIdentifierRename(repositoryIdentifier)
        self.addObserver = outside.addObserver
        self.addStrand = outside.addStrand
        self._internalObserverTree = be(
            (Observable(),
                (OaiError(),
                    (OaiIdentify(repositoryName=repositoryName, adminEmail=adminEmail, repositoryIdentifier=repositoryIdentifier, fixIdentifyBaseURL=fixIdentifyBaseURL), 
                        (outside,)
                    ),
                    (OaiList(batchSize=batchSize, supportXWait=supportXWait),
                        (OaiRecord(),
                            (outside,)
                        )
                    ),
                    (OaiGetRecord(),
                        (OaiRecord(),
                            (outside,)
                        )
                    ),
                    (OaiListMetadataFormats(),
                        (outside,)
                    ),
                    (OaiListSets(),
                        (outside,)
                    ),
                )
            )
        )

    def observer_init(self):
        list(compose(self._internalObserverTree.once.observer_init()))

    def handleRequest(self, Method, arguments, Body=None, **kwargs):
        if Method == 'POST':
            arguments.update(parse_qs(Body))
        verb = arguments.get('verb', [None])[0]
        message = verb[0].lower() + verb[1:] if verb else ''
        yield self._internalObserverTree.all.unknown(message, arguments=arguments, **kwargs)

