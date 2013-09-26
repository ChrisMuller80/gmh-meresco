# -*- coding: utf-8 -*-
# encoding: utf-8
## begin license ##
#
#    Meresco Examples is a project demonstrating some of the features of
#    various Meresco components.
#    Copyright (C) 2007-2008 SURF Foundation. http://www.surf.nl
#    Copyright (C) 2007-2009 Stichting Kennisnet Ict op school.
#       http://www.kennisnetictopschool.nl
#    Copyright (C) 2009 Delft University of Technology http://www.tudelft.nl
#    Copyright (C) 2009 Tilburg University http://www.uvt.nl
#    Copyright (C) 2007-2010 Seek You Too (CQ2) http://www.cq2.nl
#
#    This file is part of Meresco Examples.
#
#    Meresco Examples is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    Meresco Examples is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Meresco Examples; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##
from os import getuid
#WST
import sys
#
assert getuid() != 0, "Do not run tests as 'root'"
#WST:
sys.path.insert(0, "..")

import pdb
#
from os import system
from sys import exit, exc_info, stdout

from os.path import isdir, isfile

from unittest import main
from random import randint
from time import time
from glob import glob

from weightless.io import Reactor
from weightless.core import Transparent, be, compose
from amara.binderytools import bind_file, bind_string
from meresco_server.server import dna, config

from seecr.test import SeecrTestCase
from utils_local import sleepWheel

#Gebruik oude package voor get/postRequest met reactor.
#Voor loose coupling, zonder Reactor gebruik ze uit de seecr.test package.
from cq2utils import getRequest, postRequest


#Dit werkt:
#from meresco.harvester.oairequest import OaiRequest
#integrationTempdir = '/home/meresco/data/meresco'
integrationTempdir = '/home/meresco/test/integration_temp_dir'
reactor = Reactor()


class IntegrationTest(SeecrTestCase):

    def _path(self, subdir):
        return join(self.tempdir, subdir)
        
        
###SRU explainresponse##############
# <?xml version="1.0" encoding="UTF-8"?><srw:explainResponse xmlns:srw="http://www.loc.gov/zing/srw/"
#    xmlns:zr="http://explain.z3950.org/dtd/2.0/">
#     <srw:version>1.1</srw:version>
#     <srw:record>
#         <srw:recordPacking>xml</srw:recordPacking>
#         <srw:recordSchema>http://explain.z3950.org/dtd/2.0/</srw:recordSchema>
#         <srw:recordData>
#             <zr:explain>
#                 <zr:serverInfo protocol="SRU" version="1.1">
#                     <host>localhost</host>
#                     <port>8000</port>
#                     <database>sru</database>
#                 </zr:serverInfo>
#                 <zr:databaseInfo>
#                     <title lang="en" primary="true">SRU Database</title>
#                     <description lang="en" primary="true">Meresco SRU</description>
#                 </zr:databaseInfo>
#             </zr:explain>
#         </srw:recordData>
#     </srw:record>
# </srw:explainResponse>

#     def testExplain(self):
#         header, body = getRequest(reactor, port, '/sru', {})
#         explainResponse = body.explainResponse
#         self.assertEquals(config['host'], str(explainResponse.record.recordData.explain.serverInfo.host))
#         portNumber = int(explainResponse.record.recordData.explain.serverInfo.port)
#         self.assertTrue(50000 <= portNumber <= 60000, portNumber)
        
    def testRSS(self):
 #         #, 'maximumRecords':'2'
        body = self._doQuery({'ridd':'knaw_mir', 'maximumRecords':'3'}, path="/rss")
        items = [(str(item.guid), str(item.description), str(item.pubDate)) for item in body.rss.channel.item]
         
        print '\nRSS BODY:', body.xml(),
        #for item in items:
        #    print '\nRss ITEM:', item
             
        self.assertEquals(3, len(items))
#       self.assertSruQuery(1, 'volgens')
        #print str(items)
#         # self.assertEquals([('Condition assessment PVC', 'Projectomschrijving<br>Ontwikkeling van betrouwbare\n                        methoden, procedures en extrapolatiemodellen om de conditie en\n                        restlevensduur van in gebruik zijnde PVC-leidingen te\n                        bepalen.<br>Beoogde projectopbrengsten<br>-\n               ', 'http://www.narcis.nl/research/RecordID/OND1272024/Language/en'), ('Example Publication', 'This is an example RDF entity to illustrate the structure of an Enhanced Publication.', 'http://www.narcis.nl/vpub/RecordID/vpub%3Aurn%3Anbn%3Anl%3Aui%3A10-1234/xyz/Language/en'), ('Example Program 1', 'This is an example program about Search with Meresco', 'http://www.narcis.nl/publication/RecordID/record%3A1/Language/en'), ('Example Program 2', 'This is an example program about Programming with Meresco', 'http://www.narcis.nl/publication/RecordID/record%3A2/Language/en')], items)

         
      #Should be tested by reindex-client in tools dir??  
#     def testReindexAll(self):
#         print '\nStarting reindex'
#         #First call: creates batchfiles and processes them all...
#         header, body = getRequest(reactor, port, '/reindex', {'session':['narcisindex'], 'batchsize': ['2'], 'processbatch' : ['all']}, parse=False) #parse=False: returns string
#         self.assertEquals('HTTP/1.0 200 OK\r\nContent-Type: plain/text', header)        
#         print body
#         batches_created =  int(body.count('#'))
#         self.assertEquals(6, batches_created)
#     
#         remaining_batches =  int(body[len(body)-1])
#         print 'Remainder:', remaining_batches
#         ##Process all batches one by one:
#         while remaining_batches > 0:
#             header, body = getRequest(reactor, port, '/reindex', {'session':['narcisindex'], 'processbatch' : ['single']}, parse=False)            
#             remaining_batches =  int(body[len(body)-1])
#             self.assertEquals('HTTP/1.0 200 OK\r\nContent-Type: plain/text', header)
#             print "remaining_batches:", remaining_batches
#         self.assertEquals(0, remaining_batches)
        
    def testOaiListMetadataFormats(self):
        header, body = getRequest(reactor, port, '/oai', {'verb': 'ListMetadataFormats'})
        #print 'ListMetadataFormats:', body.xml()
        self.assertEquals('HTTP/1.0 200 OK\r\nContent-Type: text/xml; charset=utf-8', header)
        self.assertEquals(3, len(body.OAI_PMH.ListMetadataFormats.metadataFormat))
        self.assertEquals('metadata', body.OAI_PMH.ListMetadataFormats.metadataFormat[0].metadataPrefix)
        self.assertEquals('nl_didl_combined', body.OAI_PMH.ListMetadataFormats.metadataFormat[1].metadataPrefix)
        self.assertEquals('nl_didl_norm', body.OAI_PMH.ListMetadataFormats.metadataFormat[2].metadataPrefix)
         
    def testOaiIdentify(self):
        header, body = getRequest(reactor, port, '/oai', {'verb': 'Identify'})
        #print 'Identify:', body.xml()
        self.assertEquals('HTTP/1.0 200 OK\r\nContent-Type: text/xml; charset=utf-8', header)
        self.assertEquals('Gemeenschappelijk Harvester DANS-KB', body.OAI_PMH.Identify.repositoryName)
        self.assertEquals('martin.braaksma@dans.knaw.nl', body.OAI_PMH.Identify.adminEmail)
         
    def testOaiListSets(self):
        header, body = getRequest(reactor, port, '/oai', {'verb': 'ListSets'})
        #print 'ListSets:', body.xml()
        self.assertEquals('HTTP/1.0 200 OK\r\nContent-Type: text/xml; charset=utf-8', header)
        #self.assertEquals(9, len(body.OAI_PMH.ListSets.set))
        #self.assertEquals('ir', body.OAI_PMH.ListSets.set[0].setSpec)
        #self.assertEquals('ir:repo_id', body.OAI_PMH.ListSets.set[1].setSpec)
        
    def testOaiListRecords(self):
        header, body = getRequest(reactor, port, '/oai', {'verb': 'ListRecords', 'metadataPrefix': 'nl_didl_combined'}) #, 'set': 'ir'
        #print 'ListRecords:', body.xml()
        self.assertEquals('HTTP/1.0 200 OK\r\nContent-Type: text/xml; charset=utf-8', header)
        self.assertEquals(1, len(body.OAI_PMH.ListRecords.record))
        
        header, body = getRequest(reactor, port, '/oai', {'verb': 'ListRecords', 'metadataPrefix': 'nl_didl_combined', 'set': 'knawgroup:archive-40'})
        #print 'ListRecords:', body.xml()
        self.assertEquals('HTTP/1.0 200 OK\r\nContent-Type: text/xml; charset=utf-8', header)
        self.assertEquals(1, len(body.OAI_PMH.ListRecords.record))
        
#     def testOaiGetRecord(self):
#         #header, body = getRequest(reactor, port, '/oai', {'verb': 'GetRecord', 'metadataPrefix': 'knaw_long', 'identifier': 'knaw_mir:oai:depot.knaw.nl:557'}) 
#         header, body = getRequest(reactor, port, '/oai', {'verb': 'GetRecord', 'metadataPrefix': 'gh_combined', 'identifier': 'cwi:oai:cwi.nl:2271'})
#         #print body.xml()
#         self.assertEquals('HTTP/1.0 200 OK\r\nContent-Type: text/xml; charset=utf-8', header)
#         self.assertEquals(1, len(body.OAI_PMH.GetRecord.record))

#     def testDeleteRecord(self):
#         # Record #3 should not exist...
#         self.assertSruQuery(0, 'untokenized.oai_identifier exact "record:3"')
#         # #2 should...
#         self.assertSruQuery(1, 'untokenized.oai_identifier exact "record:2"')
#         
#         header, body = getRequest(reactor, port, '/oai', {'verb': 'ListIdentifiers', 'metadataPrefix': 'oai_dc'})
#         #print body.xml()
#         self.assertEquals(8, len(body.OAI_PMH.ListIdentifiers.header))
# 
#         header, body = getRequest(reactor, port, '/oai', {'verb': 'GetRecord', 'identifier': 'meresco:record:3', 'metadataPrefix': 'oai_dc'})
#         #print body.xml()        
#         self.assertEquals('deleted', body.OAI_PMH.GetRecord.record[0].header.status)
#     
#         
#     def doDrilldown(self, query, drilldownField):
#         message = self._doQuery({'query':query, 'x-term-drilldown': drilldownField, 'maximumRecords': '0'})
#         result = message.searchRetrieveResponse
#         return result
# 
#     def assertSruQuery(self, numberOfRecords, query):
#         message = self._doQuery({'query':query})        
#         result = message.searchRetrieveResponse
#         self.assertEquals(numberOfRecords, int(str(result.numberOfRecords)))
#         return result
# 
    def _doQuery(self, arguments, path="/rss"):
        #queryArguments = {'version': '1.1', 'operation': 'searchRetrieve', 'sortKeys': 'untokenized.mutatiedatum,,1', 'recordSchema':'meta'} #sort_title_en
        queryArguments = {}
        queryArguments.update(arguments)
        header, body = getRequest(reactor, port, path, queryArguments)
        #print 'HEADER:', header
        #print 'BODY:', body.xml()
        #there are more terms than documents in field "untokenized.mutatiedatum", but it's impossible to sort on tokenized fields
        return body


def createDatabase(port):
    recordPacking = 'xml'
    start = time()
    print "Creating database in", integrationTempdir
    sourceFiles = glob('/home/meresco/test/updaterequests/delete/*.updateRequest') #normalize/
    for updateRequestFile in sorted(sourceFiles):
        print 'Sending:', updateRequestFile
        
        #header, result = getRequest(self.harvesterInternalServerPortNumber, '/get', {'verb': 'GetStatus', 'domainId': DOMAIN, 'repositoryId': REPOSITORY}, parse='lxml')
        #self.assertEquals(['0'], xpath(result, "/status:saharaget/status:GetStatus/status:status/status:total/text()"))

        #postRequest(port, path, data, contentType='text/xml; charset="utf-8"', parse=True, timeOutInSeconds=None, additionalHeaders=None):
        #header, body = postRequest(port, '/update', open(updateRequestFile).read(), parse=False)  #parse=False, 'lxml'
        header, body = postRequest(reactor, port, '/update', open(updateRequestFile).read(), parse=False)
        print 'postResponse HEADER:', header
        print 'postResponse BODY:', body
        
        if '200 Ok' not in header:
            print 'No 200 Ok response, but:'
            print header
            exit(123)
        if "srw:diagnostics" in body:
            print 'ERROR: "srw:diagnostics"'
            print body
            #exit(1234)
    print "Finished creating database in %s seconds" % (time() - start)

if __name__ == '__main__':
    from sys import argv
    if not '--fast' in argv:
        system('rm -rf ' + integrationTempdir)
        system('mkdir --parents '+ integrationTempdir)

    port = randint(50000, 60000)
    
    server = be(dna(reactor, config['host'], portNumber=port, databasePath=integrationTempdir))
    list(compose(server.once.observer_init()))       #server.once.observer_init()  

    print "Server listening on", config['host'], "at port", port
    print "   - database:", integrationTempdir, "\n"
    
    stdout.flush()

    if '--fast' in argv and isdir(integrationTempdir):
        argv.remove('--fast')
        print "Reusing database in", integrationTempdir
    else:
        #sleepWheel(1)
        createDatabase(port)    
    main()