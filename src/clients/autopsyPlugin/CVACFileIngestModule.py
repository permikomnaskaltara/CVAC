import jarray
import inspect
from javax.swing import JCheckBox
from javax.swing import BoxLayout
from java.io import File
from java.lang import System
from java.util.logging import Level
from java.util.UUID import randomUUID
from java.lang import IllegalArgumentException
from org.sleuthkit.datamodel import SleuthkitCase
from org.sleuthkit.datamodel import AbstractFile
from org.sleuthkit.datamodel import ReadContentInputStream
from org.sleuthkit.datamodel import BlackboardArtifact
from org.sleuthkit.datamodel import BlackboardAttribute
from org.sleuthkit.datamodel import TskData
from org.sleuthkit.autopsy.ingest import IngestModule
from org.sleuthkit.autopsy.ingest.IngestModule import IngestModuleException
from org.sleuthkit.autopsy.ingest import DataSourceIngestModule
from org.sleuthkit.autopsy.ingest import FileIngestModule
from org.sleuthkit.autopsy.ingest import IngestModuleFactoryAdapter
from org.sleuthkit.autopsy.ingest import IngestModuleIngestJobSettings
from org.sleuthkit.autopsy.ingest import IngestModuleIngestJobSettingsPanel
from org.sleuthkit.autopsy.ingest import IngestMessage
from org.sleuthkit.autopsy.ingest import IngestServices
from org.sleuthkit.autopsy.ingest import ModuleDataEvent
from org.sleuthkit.autopsy.coreutils import Logger
from org.sleuthkit.autopsy.casemodule import Case
from org.sleuthkit.autopsy.casemodule.services import Services
from org.sleuthkit.autopsy.casemodule.services import FileManager
from org.sleuthkit.autopsy.datamodel import ContentUtils

import shutil
from collections import namedtuple

import os
import sys
thisPath = os.path.dirname(os.path.abspath(__file__))
cvacPath = os.path.abspath(thisPath + "/cvac")
sys.path.append(thisPath)
import Ice
import Ice.Util
#Note since DetectorPrxHelper is a static class jypthon does not want
#a reference to it but only the parent class!
import cvac
import cvac.Detector
import cvac.DetectorPrx

import cvac.DetectorCallbackHandler
import cvac.RunSet
import cvac.Purpose
import cvac.ImageSubstrate
import cvac.Label
import cvac.Labelable
import cvac.PurposedLabelableSeq
import cvac.DetectorProperties
import java.util.logging.Level
import DetectorCallbackHandlerI

def myenum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)

# The list of detectors/algorithms  we will support.

_logger = Logger.getLogger("EASYCV Logger")

def dolog(mess):
    _logger.logp(java.util.logging.Level.WARNING, None .__class__.__name__, inspect.stack()[1][3], mess)

dolog("init cvac")

# We want to do this only once.  Startup gets called for each thread
args = sys.argv
args.append('--Ice.Config=config.client')
ic = Ice.Util.initialize(args)
CVAC_DataDir = ic.getProperties().getProperty("CVAC.DataDir")
propList = ic.getProperties()
propDict = propList.getPropertiesForPrefix("")
# Dictionary where the key is the detector name
# and the value is a named tuple of proxy and model
Det = namedtuple('Det', 'proxy model')
Detectors = {}

for k,v in propDict.iteritems():
    # The key will have either Proxy or  DetectorFilename

    if "Proxy" in k:
        name = k.split('.')
        if name[0] not in Detectors:
            dect = Det(v, None)
            Detectors[name[0]] = dect
        else:
            dect = Detectors[name[0]]
            newdect = Det(v,dect.model)
            Detectors[name[0]] = newdect
    elif "DetectorFilename" in k:
        name = k.split('.')
        if name[0] not in Detectors:
            dect = Det(None, v)
            Detectors[name[0]] = dect
        else:
            dect = Detectors[name[0]]
            newdect = Det(dect.proxy,v)
            Detectors[name[0]] = newdect

#Only keep detectors that have both a proxy and model
for k,v in Detectors.iteritems():
    if v.proxy == None or v.model == None:
        del Detectors[k]

dolog("init complete")

# This class keeps track of which detector/algorithms the user selected
class CVACIngestModuleSettings(IngestModuleIngestJobSettings):
    serialVersionUID = 1L

    def __init__(self, detectors):
        self.flags = {}
        for dname in detectors:
            self.flags[dname] = False

    def getVersionNumber(self):
        return self.serialVersionUID

    def getFlags(self):
        return self.flags

    def setFlags(self,  flags):
        self.flags = flags

# UI shown for the user for each ingest job.
# Note!!!! Python Errors in this module do not get reported!
# If an error occurs the Ingest Modules panel is just not shown
# This includes python syntax errors so use dolog to isolate the problem
# This displays a checkbox for each detector.  When a new detector/algorithm
# has been added above then add it here.
class CVACIngestModuleSettingsPanel(IngestModuleIngestJobSettingsPanel):
    # Note settings is used by base class
    def __init__(self, settings, detectors):
        dolog("init")
        self.local_settings = settings
        self.checkBoxTuples = []
        # Add JPanel components here
        dolog("init comp")
        self.initComponents(detectors)
        dolog("cutomzie")
        self.customizeComponents()
        dolog("init done")

    def checkAllBoxes(self, event):
        dolog("checking boxes")
        for dname, ckbox in self.checkBoxTuples:
            if ckbox.isSelected():
                flags = self.local_settings.getFlags()
                flags[dname] = True
                dolog(dname + " true")
                self.local_settings.setFlags(flags)
            else:
                flags = self.local_settings.getFlags()
                flags[dname] = False
                dolog(dname + " false")
                self.local_settings.setFlags(flags)

    def checkBox(self,event):
        self.checkAllBoxes(event)

    def initComponents(self, detectors):
        self.setLayout(BoxLayout(self, BoxLayout.Y_AXIS))
        for k,v in detectors.iteritems():
            checkbox = JCheckBox(k, actionPerformed=self.checkBox)
            if not checkbox:
                dolog("checkbox failed")
            self.add(checkbox)
            self.checkBoxTuples.append((k,checkbox))

    def customizeComponents(self):
        dolog("in cust")
        flags = self.local_settings.getFlags()
        dolog("got flags")
        if not flags:
            dolog("No Flags!!!")
        if self.checkBoxTuples == None:
            dolog("No Detectors!")
        else:
            dolog("checking")
            dolog("len {0}".format(len(self.checkBoxTuples)))
            for dname, cbox in self.checkBoxTuples:
                dolog(dname)
                #cbox.setSelected(flags[dname])

    def getSettings(self):
        dolog("getting settings")
        return self.local_settings

# This is the Factory class that creates our ingest class
class CVACIngestModuleFactory(IngestModuleFactoryAdapter):

    moduleName = "EasyCV Ingest Module"

    def __init__(self):
        self.settings = None

    def getModuleDisplayName(self):
        return self.moduleName

    def getModuleDescription(self):
        return "EasyCV Bridge to Computer Vision Services"

    def getModuleVersionNumber(self):
        return "1.0"

    def isFileIngestModuleFactory(self):
        return True

    def createFileIngestModule(self, ingestOptions):
        res = CVACFileIngestModule(self.settings, Detectors)
        return res

    def hasIngestJobSettingsPanel(self):
        return True

    def getDefaultIngestJobSettings(self):
        return CVACIngestModuleSettings(Detectors)

    def getIngestJobSettingsPanel(self, settings):
        #if not isinstance(settings, CVACIngestModuleSettings):
        #   raise IllegalArgumentException("Expected CVACIngestModuleSettings")
        self.settings = settings
        panel = CVACIngestModuleSettingsPanel(self.settings, Detectors)
        return panel

# File-level ingest module.  One gets created per thread.
class CVACFileIngestModule(FileIngestModule):

    def __init__(self, settings, detectors):
        self.localSettings = settings
        self.detectors = detectors
        self.validDets = []

    def log(self, level, msg):
        _logger.logp(level, self.__class__.__name__, inspect.stack()[1][3], msg)

    # Where any setup and configuration is done
    # 'context' is an instance of org.sleuthkit.autopsy.ingest.IngestJobContext.
    # See: http://sleuthkit.org/autopsy/docs/api-docs/3.1/classorg_1_1sleuthkit_1_1autopsy_1_1ingest_1_1_ingest_job_context.html


    def startUp(self, context):
        self.log(java.util.logging.Level.INFO, "in startup")

        flags = self.localSettings.getFlags()

        try:
            self.log(java.util.logging.Level.INFO, "creating detectors")
            det = None
            for k,v in self.detectors.iteritems():
                if flags[k] == True:
                    det = ic.stringToProxy(v.proxy)
                    det = cvac.DetectorPrxHelper.checkedCast(det)
                    if not det:
                        raise IngestModuleException("Invalid Detector service proxy for " + k)
                    self.log(java.util.logging.Level.INFO, "Using detector " + k)
                    self.validDets.append ((det,v.model,k))

            if det:
                self.log(java.util.logging.Level.INFO, "created detectors")
            else:
                self.log(java.util.logging.Level.ERROR, "No Detectors selected")
                raise IngestModuleException("No Detectors selected!")
        except Ice.ConnectionRefusedException:
            raise IngestModuleException("Cannot connect one of the detectors")

        self.log(java.util.logging.Level.INFO, "startup complete")

    # Where the analysis is done.  Each file will be passed into here.
    # The 'file' object being passed in is of type org.sleuthkit.datamodel.AbstractFile.
    # See: http://www.sleuthkit.org/sleuthkit/docs/jni-docs/classorg_1_1sleuthkit_1_1datamodel_1_1_abstract_file.html

    def process(self, file):

        # Skip non-files
        if ((file.getType() == TskData.TSK_DB_FILES_TYPE_ENUM.UNALLOC_BLOCKS) or
            (file.getType() == TskData.TSK_DB_FILES_TYPE_ENUM.UNUSED_BLOCKS) or
            (file.isFile() == False)):
            return IngestModule.ProcessResult.OK

        runset = cvac.RunSet()
        purpose = cvac.Purpose(cvac.PurposeType.UNPURPOSED, -1)
        tempfile = os.path.join(CVAC_DataDir, file.getName())
        extracted_file = File(tempfile)
        ContentUtils.writeToFile(file, extracted_file)

        #shutil.copyfile(localpath, CVAC_DataDir + "/" + localpath)
        #path, filename = os.path.split(localpath)
        dataroot = cvac.DirectoryPath()
        filePath = cvac.FilePath(dataroot,file.getName())
        substrate = cvac.ImageSubstrate(width=0, height=0, path= filePath)
        label = cvac.Label(False, "", None, cvac.Semantics())
        labelable = cvac.Labelable(0.0,label, substrate)
        seq = cvac.PurposedLabelableSeq(purpose, [labelable])
        runset.purposedLists = [seq]

        detectorRoot = cvac.DirectoryPath("detectors")

        adapter = ic.createObjectAdapter("")
        cbID = Ice.Identity()
        cbID.name = randomUUID().toString()

        cbID.category = ""
        # DetectorCallbackHanderI is a java callback.  This is required to get ICE
        # callback despatcher to find the callback since it will not find a
        # python one.
        callback = DetectorCallbackHandlerI()

        adapter.add(callback, cbID)
        adapter.activate()

        artifact = False

        for det,model,name  in self.validDets:
            if not det:
                continue
            if not model:
                continue
            detectorProps = det.getDetectorProperties()
            if not detectorProps:
                dolog("detector props returned None")
            modelPath = cvac.FilePath(detectorRoot, model)
            det.ice_getConnection().setAdapter(adapter)
            #self.log(java.util.logging.Level.INFO, name)
            det.process(cbID, runset, modelPath, detectorProps )

            labelText = None
            # The java callback returns an array of resultSets.
            # It seems to work better to access these java arrays via indexes
            # instead of normal python syntax.
            resultSetArray = callback.getResults()

            for x in range(len(resultSetArray)):
                resList = resultSetArray[x]
                for j in range(len(resList.results)):
                    res = resList.results[j]
                    for k in range(len(res.foundLabels)):
                        labelable = res.foundLabels[k]
                        if labelable.lab.hasLabel:
                            labelText = labelable.lab.name
                            self.log(java.util.logging.Level.INFO, "Found label " + labelText)
                            # Lets just use the first label we get
                            # If its negative then don't report it.
                            if labelText == 'negative':
                                labelText = None
                            elif name == "BagOfWordsFlags":
                                if labelText == 'ca':
                                    labelText =  "California flag"
                                if labelText == 'us':
                                    labelText =  "US flag"
                                if labelText == 'kr':
                                    labelText =  "Korean flag"
                            break
            if labelText:
                artifact = True
                art = file.newArtifact(BlackboardArtifact.ARTIFACT_TYPE.TSK_KEYWORD_HIT)
                att = BlackboardAttribute(BlackboardAttribute.ATTRIBUTE_TYPE.TSK_KEYWORD.getTypeID(),
                              CVACIngestModuleFactory.moduleName, name, labelText)
                art.addAttribute(att)
                art = file.newArtifact(BlackboardArtifact.ARTIFACT_TYPE.TSK_GEN_INFO)
                att = BlackboardAttribute(BlackboardAttribute.ATTRIBUTE_TYPE.TSK_TAG_NAME.getTypeID(),
                              CVACIngestModuleFactory.moduleName, name, labelText)
                art.addAttribute(att)

        if artifact:
            # Fire an event to notify the UI and others that there is a new artifact
            IngestServices.getInstance().fireModuleDataEvent(
                ModuleDataEvent(CVACIngestModuleFactory.moduleName,
                                BlackboardArtifact.ARTIFACT_TYPE.TSK_KEYWORD_HIT, None))
            IngestServices.getInstance().fireModuleDataEvent(
                ModuleDataEvent(CVACIngestModuleFactory.moduleName,
                                BlackboardArtifact.ARTIFACT_TYPE.TSK_GEN_INFO, None))


        return IngestModule.ProcessResult.OK

    def shutDown(self):

        pass
