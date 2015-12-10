# -*- coding: utf-8 -*-

from lxml import etree
from lxml.etree import parse, XMLSchema, XMLSchemaParseError, _ElementTree, tostring
from xml.sax.saxutils import escape as escapeXml
from meresco.core import Observable
from copy import deepcopy
from StringIO import StringIO
from meresco.components.xml_generic.validate import ValidateException
from xml_validator import formatExceptionLine
from dateutil.parser import parse as parseDate
from datetime import *
from normalize_nl_didl import XML_ENCODING

import commons as comm

#Schema validatie:
from os.path import abspath, dirname, join

# This component handles ADD messages only.
# It will try to convert the supplied data (KNAWLong) from the 'metadata' part into KNAWshort. All other parts and data formats are ignored (blocked).
# If it fails in doing so, it will block (NOT pass) the ADD message.
# Returns: xml-string!


#Taken from: EduStandaard Semantiek, tabel 1 en 2. 
GENRES_SEMANTIEK = {
    "article" : "info:eu-repo/semantics/article",
    "bachelorthesis" : "info:eu-repo/semantics/bachelorThesis",
    "masterthesis" : "info:eu-repo/semantics/masterThesis",
    "doctoralthesis" : "info:eu-repo/semantics/doctoralThesis",
    "book" : "info:eu-repo/semantics/book",
    "bookpart" : "info:eu-repo/semantics/bookPart",
    "review" : "info:eu-repo/semantics/review",
    "conferenceobject" : "info:eu-repo/semantics/conferenceObject",
    "lecture" : "info:eu-repo/semantics/lecture",
    "workingpaper" : "info:eu-repo/semantics/workingPaper",
    "preprint" : "info:eu-repo/semantics/preprint",
    "report" : "info:eu-repo/semantics/report",
    "annotation" : "info:eu-repo/semantics/annotation",
    "contributiontoperiodical" : "info:eu-repo/semantics/contributionToPeriodical",
    "patent" : "info:eu-repo/semantics/patent",
    "other" : "info:eu-repo/semantics/other",
    "reportpart" : "info:eu-repo/semantics/reportPart",
    "bookreview" : "info:eu-repo/semantics/bookReview",
    "researchproposal" : "info:eu-repo/semantics/researchProposal",
    "studentthesis" : "info:eu-repo/semantics/studentThesis",
    "technicaldocumentation" : "info:eu-repo/semantics/technicalDocumentation",
    "semantics/conferenceposter" : "info:eu-repo/semantics/conferencePoster",
    "conferenceproceedings" : "info:eu-repo/semantics/conferenceProceedings",
    "conferenceitemnotinproceedings" : "info:eu-repo/semantics/conferenceItemNotInProceedings",
    "semantics/conferencepaper" : "info:eu-repo/semantics/conferencePaper",
    "conferenceitem" : "http://purl.org/eprint/type/ConferenceItem",
    "type/conferenceposter" : "http://purl.org/eprint/type/ConferencePoster",
    "type/conferencepaper" : "http://purl.org/eprint/type/ConferencePaper"
    }


MODS_VERSION = '3.4'
STR_MODS = "MODS:"

#Taken from: http://www.loc.gov/marc/relators/relacode.html (Updated: 2015-12-10)
MARC_ROLES=['abr','acp','act','adi','adp','aft','anl','anm','ann','ant','ape','apl','app','aqt','arc','ard','arr','art','asg','asn','ato','att','auc','aud','aui','aus','aut','bdd','bjd','bkd','bkp','blw','bnd','bpd','brd','brl','bsl','cas','ccp','chr','clb','cli','cll','clr','clt','cmm','cmp','cmt','cnd','cng','cns','coe','col','com','con','cor','cos','cot','cou','cov','cpc','cpe','cph','cpl','cpt','cre','crp','crr','crt','csl','csp','cst','ctb','cte','ctg','ctr','cts','ctt','cur','cwt','dbp','dfd','dfe','dft','dgg','dgs','dis','dln','dnc','dnr','dpc','dpt','drm','drt','dsr','dst','dtc','dte','dtm','dto','dub','edc','edm','edt','egr','elg','elt','eng','enj','etr','evp','exp','fac','fds','fld','flm','fmd','fmk','fmo','fmp','fnd','fpy','frg','gis','grt','his','hnr','hst','ill','ilu','ins','inv','isb','itr','ive','ivr','jud','jug','lbr','lbt','ldr','led','lee','lel','len','let','lgd','lie','lil','lit','lsa','lse','lso','ltg','lyr','mcp','mdc','med','mfp','mfr','mod','mon','mrb','mrk','msd','mte','mtk','mus','nrt','opn','org','orm','osp','oth','own','pan','pat','pbd','pbl','pdr','pfr','pht','plt','pma','pmn','pop','ppm','ppt','pra','prc','prd','pre','prf','prg','prm','prn','pro','prp','prs','prt','prv','pta','pte','ptf','pth','ptt','pup','rbr','rcd','rce','rcp','rdd','red','ren','res','rev','rpc','rps','rpt','rpy','rse','rsg','rsp','rsr','rst','rth','rtm','sad','sce','scl','scr','sds','sec','sgd','sgn','sht','sll','sng','spk','spn','spy','srv','std','stg','stl','stm','stn','str','tcd','tch','ths','tld','tlp','trc','trl','tyd','tyg','uvp','vac','vdg','voc','wac','wal','wam','wat','wdc','wde','win','wit','wpr','wst']
LOGGER1 = " is not a valid RFC3066 language code."
LOGGER2 = "Found unknown extension (no EDUstandaard)."

EXCEPTION1 = "Mandatory MODS metadata not found in DIDL Item."
EXCEPTION2 = "Mandatory MODS titleInfo not found."
EXCEPTION3 = "MODS titleInfo/title has empty value."
EXCEPTION4 = "MODS invalid role macrelator: "
EXCEPTION5 = "Mandatory MODS name  not found."
EXCEPTION6 = "No valid MODS genre found."
EXCEPTION7 = "Mandatory MODS originInfo/dateIssued not found."


mods_edu_extentions_ns = {
    'gal': "info:eu-repo/grantAgreement",
    'dai': "info:eu-repo/dai",
    'hbo': "info:eu-repo/xmlns/hboMODSextension",
    'wmp': "http://www.surfgroepen.nl/werkgroepmetadataplus",
}

# , ('hbo/hboMODSextension.xsd', 'self::hbo:hbo')
# ('xml-schema location', 'xpath to root', 'schema location'):
mods_edu_extentions = [ ('dai/dai-extension.xsd', 'self::dai:daiList', 'info:eu-repo/dai http://purl.org/REP/standards/dai-extension.xsd'), 
                        ('gal/gal-extension.xsd', 'self::gal:grantAgreementList', 'info:eu-repo/grantAgreement http://purl.org/REP/standards/gal-extension.xsd'),
                        ('wmp/wmp-extension.xsd', 'self::wmp:rights', 'http://www.surfgroepen.nl/werkgroepmetadataplus http://purl.org/REP/standards/wmp-extension.xsd')]

## Do not list "extension" here. So it will be removed by default. <extension> is handeled by a different function. 
mods_edu_tlelements = ["titleInfo", "relatedItem", "name", "language", "typeOfResource", "genre", "abstract", "identifier", "classification", "subject", "originInfo"]
# Skipped tl elements because not part of EduStandaard: , ["location", "note", "physicalDescription", "recordInfo", "tableOfContents", "targetAudience"]


class Normalize_nl_MODS(Observable):
    """A class that normalizes MODS metadata to the EduStandaard applicationprofile"""
    
    def __init__(self, nsMap={}):
        Observable.__init__(self)
        
        self._nsMap = mods_edu_extentions_ns.copy()
        self._nsMap.update(nsMap or {})
        self._bln_success = False
        
        self._edu_extension_schemas = []
        
        ## Fill the schemas list for later use:
        for schemaPath, xPad, s_loc in mods_edu_extentions:
            print 'schema init:' ,schemaPath, xPad, s_loc
            try:
                self._edu_extension_schemas.append((XMLSchema(parse(join(dirname(abspath(__file__)), 'xsd/'+ schemaPath) ) ), xPad, s_loc ))
            except XMLSchemaParseError, e:
                print 'XMLSchemaParseError.', e.error_log.last_error
                raise
        
        
    def _detectAndConvert(self, anObject):
        if type(anObject) == _ElementTree:
            return self.convert(anObject)
        return anObject

    def convert(self, lxmlNode):
        self._bln_success = False
        self._bln_hasTypOfResource = False
        result_tree = self._normalizeRecord(lxmlNode)
        if result_tree != None:
            self._bln_success = True            
        return result_tree

    def all_unknown(self, method, *args, **kwargs):
        self._identifier = kwargs.get('identifier')        
        
        newArgs = [self._detectAndConvert(arg) for arg in args]     
        newKwargs = dict((key, self._detectAndConvert(value)) for key, value in kwargs.items())
        if self._bln_success:
            yield self.all.unknown(method, *newArgs, **newKwargs)

    def _normalizeRecord(self, lxmlNode):        
        # MODS normalisation in 4 steps:
        # 1. Get Mods from the lxmlNode.
        # 2. Normalize it
        # 3. Put it back in place.
        # 4. return the lxmlNode containing the normalized MODS.
        
        #1: Get Mods from the lxmlNode:
        lxmlMODS = lxmlNode.xpath('(//mods:mods)[1]', namespaces=self._nsMap)
        
        ## Our normalisation functions to call:
        modsFunctions = [ self._convertFullMods2GHMods ]
        
        if len(lxmlMODS) > 0:
        #2: Normalize it
            str_norm_mods = ''            
            for function in modsFunctions:
                str_norm_mods += function(lxmlMODS[0])            
            
        #3: Put it back in DIDL/place:        
            lxmlMODS[0].getparent().replace(lxmlMODS[0], etree.fromstring(str_norm_mods) )

        else: #This should never happen @runtime: record should have been validated up front...
            raise ValidateException(formatExceptionLine(EXCEPTION1, prefix=STR_MODS))

        #4: Return the lxmlNode containing the normalized MODS:
        #print(etree.tostring(lxmlNode, pretty_print=True))
        return lxmlNode


    def _convertFullMods2GHMods(self, lxmlMODSNode):
        returnxml = ''
        ## We need a deepcopy, otherwise we'll modify the lxmlnode by reference!!
        e_modsroot_copy = deepcopy(lxmlMODSNode)
        
        ## Check if version 3.4 was supplied: correct otherwise.
        self._normalizeModsVersion(e_modsroot_copy)
        
        ## Valideer en normaliseer alle extension tags in 1 tag en bewaar deze voor later....
        e_extensions = self._getValidModsExtension(e_modsroot_copy)
        ## LET OP: Alle <extension> tags worden hieronder verwijdert doordat _tlExtension() 'None' terug geeft.       
        
        ## Valideer en normaliseer alle titleInfo tags:
        self._normalizeTitleinfo(e_modsroot_copy)

        ## Valideer en normaliseer alle <name> tags op e_modsrppt_copy...
        self._validateNames(e_modsroot_copy)
        ## LET OP: Alle <name> tags worden hieronder verwijderd doordat _tlNames() 'None' terug geeft.
        
        #N Normaliseer alle Genre tags...       
        self._validateGenre(e_modsroot_copy)

        ## Itereer over ALLE toplevel elementen:
        for child in e_modsroot_copy.iterchildren():
            
            for tlelement in mods_edu_tlelements: ## Iterate over all top level elements...
                if child.tag == ('{%s}'+tlelement) % self._nsMap['mods']:
                    ## Call normalisation function on current child:
                    returnChild = eval("self._tl" + tlelement.capitalize())(child)
                    
                    if returnChild is None:
                        e_modsroot_copy.remove(child)
                    else:
                        child.getparent().replace(child, returnChild)
                    break
            else: #Wordt alleen geskipped als ie uit 'break' komt...
                e_modsroot_copy.remove(child)
                
        ## Append our <extension> child elements to the root:
        if e_extensions is not None:
            for child in e_extensions.iterfind(('{%s}extension') % self._nsMap['mods']):
                e_modsroot_copy.append(child)
        
        ## Append one typeOfResource to root, if it does not exist:
        if not self._bln_hasTypOfResource:
            self._addTypeOfResource(e_modsroot_copy)
        
        ## We'll add the MODS node to a new custom element and remove it again, so that lxml will use the mods prefix used in the namespacemap.
        ## Otherwise default namespaces may be used for MODS...
        root = etree.Element('{'+self._nsMap['mods']+'}temp', nsmap=self._nsMap)
        root.append(e_modsroot_copy)       
                
        ## Some namespaces may not be in use anymore after normalisation: remove them...
        etree.cleanup_namespaces(root)
        
        returnxml = tostring(root.find( ('{%s}mods') % self._nsMap['mods'] ) , pretty_print=True, encoding=XML_ENCODING)
        #returnxml = etree.tostring(e_modsroot_copy, pretty_print=True, encoding=XML_ENCODING)
        
        return returnxml

## mods version:
    def _normalizeModsVersion(self, e_modsroot):
        #We'll always normalize to MODS_VERSION and proper schemalocation:
        e_modsroot.set("version", MODS_VERSION)
        e_modsroot.set("{http://www.w3.org/2001/XMLSchema-instance}schemaLocation", "http://www.loc.gov/mods/v3 http://www.loc.gov/standards/mods/v3/mods-"+ MODS_VERSION.replace(".", "-") +".xsd")
        return e_modsroot

## titleInfo:
    def _normalizeTitleinfo(self, modsNode):
        ## Select all titleInfo's
        hasTitleInfo = False
        for child in modsNode.iterfind(('{%s}titleInfo') % self._nsMap['mods']):
            hasTitleInfo = True 
            if not self._isValidTitleInfoTag(child):
                modsNode.remove(child)
        if not hasTitleInfo:
            raise ValidateException(formatExceptionLine(EXCEPTION2, prefix=STR_MODS))

    def _isValidTitleInfoTag(self, lxmlNode):
        #Correct @type:
        #if lxmlNode.get('type') != 'translated':
        #    if lxmlNode.attrib.has_key('type'):
        #        del lxmlNode.attrib['type'] # Remove 'type' attribute if value other than 'translated'...
        #Throw Exception if no or empty title tag:
        for title in lxmlNode.iterfind(('{%s}title') % self._nsMap['mods']):
            if not title.text:
                raise ValidateException(formatExceptionLine(EXCEPTION3, prefix=STR_MODS))
        return True

    def _tlTitleinfo(self, childNode):
        ## Pass thru all (normalized) titleInfo nodes...
        return childNode

## Name:
    def _validateNames(self, modsNode): 
        for name in modsNode.iterfind(('{%s}name') % self._nsMap['mods']):
            role = name.xpath("self::mods:name/mods:role/mods:roleTerm[@type='code' and @authority='marcrelator']/text()", namespaces=self._nsMap)
            if not role or len(role) < 1: ## Geen roleterm gevonden, of lege string voor type code en authority marcrelator: Verwijder dit name element:
                modsNode.remove(name)
            elif len(role) > 0 and not self.__isValidRoleTerm(role[0]):
                raise ValidateException(formatExceptionLine( EXCEPTION4 + role[0], prefix=STR_MODS))        
        if len(modsNode.xpath("//mods:mods/mods:name", namespaces=self._nsMap)) <= 0:
            raise ValidateException(formatExceptionLine(EXCEPTION5, prefix=STR_MODS))

    def __isValidRoleTerm(self, str_roleTerm):
        return True if str_roleTerm.strip() in MARC_ROLES else False
        
    def _tlName(self, childNode):
        ## Pass thru all (normalized) name nodes...
        return childNode

## Language:
    def _tlLanguage(self, childNode):
        ## SSDC mandates iso639-1, SSMODS mandates iso639-1 or iso639-2 if iso639-1 is not available, but we'll settle for either 2 or 3 chars. iso639-2b, rfc3066, iso639-3, iso639-1
        rfc3066_lang = childNode.xpath("self::mods:language/mods:languageTerm[@type='code' and @authority]/text()", namespaces=self._nsMap)
        txt_lang = childNode.xpath("self::mods:language/mods:languageTerm[@type='text']/text()", namespaces=self._nsMap)
        if len(rfc3066_lang) > 0:
            #See also: ftp://ftp.rfc-editor.org/in-notes/rfc3066.txt
            #match = self._patternRFC3066.match(rfc3066_lang[0])
            #if match and match.group(1).lower() in RFC3066:
            if comm.isValidRFC3066(rfc3066_lang[0]):
            #if rfc3066_lang[0].strip() in RFC3066:
                #Set @authority to RFC3066 on child languageTerm, since that is what has been checked for:
                for lt in childNode.iterfind('{'+self._nsMap.get('mods')+'}languageTerm'):
                    lt.set('authority', 'rcf3066')
                return childNode
            self.do.logMsg(self._identifier, rfc3066_lang[0] + LOGGER1, prefix=STR_MODS)
            return None
        elif len(txt_lang) > 0:
            return childNode
        else:
            return None

## Genre:
    def _validateGenre(self, modsNode):
    
        fqGenre = None
        bln_hasValid = False        
        ## Loop all 'genre' elements as separate nodes:
        for genre in modsNode.iterfind('{'+self._nsMap.get('mods')+'}genre'):
        
            for key, value in GENRES_SEMANTIEK.iteritems():
                    if genre.text.strip().lower().find(key) >= 0: #found a (lowercased) genre
                        fqGenre = value                           
                        break
        
            if fqGenre is not None and not bln_hasValid:
                bln_hasValid = True
                genre.text = fqGenre
            else:
                modsNode.remove(genre)
                
        if not bln_hasValid:
            raise ValidateException(formatExceptionLine(EXCEPTION6, prefix=STR_MODS))

    def _tlGenre(self, childNode):
        return childNode ## Genres have been normalised already by _validateGenre()

## OriginInfo:
    def _tlOrigininfo(self, childNode):
        hasDateIssued = False
        ## Select all children from originInfo having 'encoding' attribute:
        children = childNode.xpath("self::mods:originInfo/child::*[@encoding='w3cdtf' or @encoding='iso8601']", namespaces=self._nsMap)
        if len(children) > 0:
            for child in children:
                if self._validateISO8601( child.text ):                    
                    child.text = self._granulateDate(child.text)
                    child.set('encoding', 'w3cdtf')
                    if child.tag == ('{%s}dateIssued') % self._nsMap['mods']: hasDateIssued = True
                else:
                    child.getparent().remove(child)
        if not hasDateIssued:
            raise ValidateException(formatExceptionLine(EXCEPTION7, prefix=STR_MODS))
        return childNode if len(childNode) > 0 else None


    def _validateISO8601(self, datestring):
        ## See: http://labix.org/python-dateutil
        if datestring is None: return False
        
        try:
            parseDate(datestring, ignoretz=True, fuzzy=True)
        except ValueError:
            return False
        return True
        
        
    def _granulateDate(self, str_date):
        """returns only date parts that are succesfully parsed."""
        di_1 = parseDate(str_date, ignoretz=True, fuzzy=True, default=datetime(1900, 12, 28, 0, 0)) #1900-12-28 default year, month and day. (day 28 exists for every month:-)
        di_2 = parseDate(str_date, ignoretz=True, fuzzy=True, default=datetime(2000, 01, 01, 0, 0)) #2000-01-01 default year, month and day.
        
        ## Parsed date with no defaults used:
        if str(di_1.date()) == str(di_2.date()):
            return str(di_1.date()) # Dates are the same: date is parsed completely.
        
        ## Check for dft day and month:
        if di_1.date().day != di_2.date().day and di_1.date().month != di_2.date().month:
            return str(di_1.date().year) # Only year has been parsed succesfully.
        if di_1.date().day != di_2.date().day and di_1.date().month == di_2.date().month:
            return ('%s-%s') % (di_1.date().year, di_1.date().month) # Only year and month have been parsed succesfully.

## Location:
#    def _tlLocation(self, childNode):
#        for url in childNode.iterfind(('{%s}url') % self._nsMap['mods']):
#            if not self._isURL(url.text): childNode.remove(url)
#        return childNode if len(childNode) > 0 else None

## Abstract:
    def _tlAbstract(self, childNode):
        ## Pass thru all abstract nodes: xml-schema validation of MODS has already taken place...
        #We need to remove all 'attributes' except xml:lang (EduStandaard)...
        for k, v in childNode.attrib.iteritems():
            if k != '{http://www.w3.org/XML/1998/namespace}lang':
                del childNode.attrib[k]
        return childNode


## PhysicalDescription:
    def _tlPhysicaldescription(self, childNode): #Extent check, skip otherwise...
        pages = childNode.xpath('self::mods:physicalDescription/mods:extent/text()', namespaces=self._nsMap)
        if len(pages) <= 0:
            return childNode
        elif not pages[0].strip():
            return None
        return childNode

## RelatedItem:
    def _tlRelateditem(self, childNode):
        #1: Remove all non-Edustandaard 'types' (only type=host):
        type_attr = childNode.get('type')
        if type_attr is None or (type_attr is not None and not type_attr.strip() in ['host']): #['preceding', 'host', 'succeeding', 'series', 'otherVersion']
            return None
        
        #2: Check if <start>, <end> and <total> tags are integers:
        children = childNode.xpath("self::mods:relatedItem/mods:part/mods:extent[@unit='page']/child::*", namespaces=self._nsMap)
        if len(children) > 0:
            for child in children: # <start>, <end>, <total> tags...
                if child.tag in [('{%s}start') % self._nsMap['mods'], ('{%s}end') % self._nsMap['mods'], ('{%s}total') % self._nsMap['mods']] and not comm.isInt(child.text):
                    ouder = child.getparent()
                    ouder.remove(child)
                    if len(ouder) == 0:
                        ouder.getparent().remove(ouder)
        
        
        #3: Normalize <part><date encoding=""> tag:
        children = childNode.xpath("self::mods:relatedItem/mods:part/mods:date", namespaces=self._nsMap)
        if len(children) > 0:
            for child in children:
                #if self._validateISO8601( child.text ):                    
                #    child.text = self._granulateDate(child.text)
                #    child.set('encoding', 'w3cdtf')
                #else:
                    child.getparent().remove(child)
        
        return childNode if len(childNode) > 0 else None

## Part (relatedItem):
    def _isValidPart(self, partNode):
        return False


## TypeOfResource:
    def _tlTypeofresource(self, childNode):
        terug = childNode if not self._bln_hasTypOfResource else None
        self._bln_hasTypOfResource = True
        return terug

    def _addTypeOfResource(self, modsNode):
        ## Adds exactly one typeOfResource element to the mods node.
        tor = etree.SubElement(modsNode, ('{%s}typeOfResource') % self._nsMap['mods'])
        tor.text = 'text'

## Identifier:
    def _tlIdentifier(self, childNode):
        if len(childNode.attrib) == 0 or childNode.text is None:
            return None
        return childNode ## Transfer 'as is'.

## Classification:        
    def _tlClassification(self, childNode):
        if not (childNode.attrib.has_key('authority') or childNode.attrib.has_key('authorityURI') ) or childNode.text is None:
            return None
        return childNode ## Transfer 'as is'.

## Subject:
    def _tlSubject(self, childNode):
        if len(childNode.xpath('mods:topic', namespaces=self._nsMap)) < 1:
            return None      
        return childNode ## Transfer 'as is'.

## Extension:
    def _tlExtension(self, childNode):
        ## All <extension> tags will be removed, when returning None!
        return None

    def _getValidModsExtension(self, modsNode):
        ## Select all 'extension' child elements as separate nodes:        
        extensions = modsNode.xpath('self::mods:mods/mods:extension/child::*', namespaces=self._nsMap)
        e_rootExten = etree.Element(('{%s}extension') % self._nsMap['mods'])
        for extension in extensions:
            if self._isValidEduStandaardExtension(extension):
                e_ext = etree.SubElement(e_rootExten, ('{%s}extension') % self._nsMap['mods']) #Create extension sub-element.
                #Normalize schemalocation:
                #extension.set("{http://www.w3.org/2001/XMLSchema-instance}schemaLocation", "http://www.loc.gov/mods/v3 http://www.loc.gov/standards/mods/v3/mods-"+ MODS_VERSION.replace(".", "-") +".xsd")
                e_ext.append(extension)
                e_rootExten.append(e_ext)
        return e_rootExten if len(e_rootExten) > 0 else None

    #TODO: Find out why HBO.xsd (lxml) doesnt validate, but Oxygen (Xerces) does?!?
    def _isValidEduStandaardExtension(self, lxmlNode):
        for schema, xpad, slocation in self._edu_extension_schemas:
            extent = lxmlNode.xpath(xpad, namespaces=self._nsMap)
            if len(extent) > 0: ## Validate found EduStandaard extension:
                schema.validate(lxmlNode)
                if schema.error_log:
                    return False
                else:
                    #print "EduStandaard extension IS VALID", lxmlNode.tag
                    lxmlNode.set("{http://www.w3.org/2001/XMLSchema-instance}schemaLocation", slocation) 
                    return True
        ## Looped over all allowed Edustandaard extensions types: None was found...        
        self.do.logMsg(self._identifier, LOGGER2, prefix=STR_MODS)
        return False


## Helper methods:
#    def _checkURNFormat(self, pid):
#        m = comm.patternURNNBN.match(pid)
#        if not m:
#            raise ValidateException(formatExceptionLine(EXCEPTION8 + pid, prefix=STR_MODS))
#        return True


    def __str__(self):
        return 'Normalize_nl_MODS'
