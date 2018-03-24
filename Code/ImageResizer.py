from resizeimage import resizeimage
from PIL import Image
import PIL.ExifTags
import os
import time

class ImageResizer():
    def __init__(self, rootDirectory, ignoreList, movingDirectory, logName, height, width):
        print("Starting...")
        self.logName = logName
        self.newHeight = height
        self.newWidth = width
        self.initializeLog()
        self.rootDirectory = rootDirectory
        self.movingDirectory = movingDirectory
        self.subDirectories = self.getSubDirectories()
        self.ignoreList = ignoreList
        self.applyIgnoreList()
        self.filesInMovingDirectory = self.getFilesInSpecificDirectory(self.movingDirectory)
        self.startProcess()
        # print(self.subDirectories[2])
        # files = [f for f in os.listdir(self.subDirectories[2]) if os.path.isfile(os.path.join(self.subDirectories[2], f))]
        # print(files)

    def initializeLog(self):
        if(os.path.isfile(self.logName)):
            print("Log Found. Appending to it.")
            pass
        else:
            print("No log Found. Creating New Log File.")
            with open(self.logName, "w") as csvFile:
                csvFile.write("File Name, Original DPI, Image Initial Size, Original Height, Original Width, Original Modified Date, Original Path, New File Size, New File Height, New File Width, New File Path\n")
            csvFile.close()

    def startProcess(self):
        for i in range(len(self.subDirectories)):
            print("Processing :", self.subDirectories[i], "...")
            listOfFiles = self.getFilesInSpecificDirectory(self.subDirectories[i])
            listOfFiles = self.listofFilesCleaner(listofFiles= listOfFiles)
            lastModifiedOriginal, listofTimeStringsOriginal = self.getLastModifiedTime(self.subDirectories[i], listOfFiles)
            listOfNamings = self.generateNaming(listofFiles= listOfFiles, path=self.subDirectories[i])
            listofTargetFiles = self.getFilesInSpecificDirectory(self.movingDirectory)

            self.moveFile(listofFiles=listOfFiles, listofTargetFiles=listofTargetFiles, path=self.subDirectories[i], listOfNamings=listOfNamings, lastModifiedDate=lastModifiedOriginal, originalTimeStrings=listofTimeStringsOriginal)
            # print(listofTargetFiles)


    def moveFile(self, listofFiles, listofTargetFiles, path, listOfNamings, lastModifiedDate, originalTimeStrings):
        with open(self.logName, "a") as csvFile:
            for i in range(len(listOfNamings)):
                if(listOfNamings[i] not in listofTargetFiles):
                    originalPathFile = str(path) + "\\" + str(listofFiles[i])
                    targetPath = str(self.movingDirectory) + "\\" + str(listOfNamings[i])
                    with open(originalPathFile, "r+b") as f:
                        with Image.open(f) as image:
                            # print(image.width, image.height)
                            # print(image._getexif(), originalPathFile)
                            try:
                                #Get the DPI
                                exif = {
                                    PIL.ExifTags.TAGS[k]:v
                                    for k, v in image._getexif().items()
                                    if k in PIL.ExifTags.TAGS
                                }
                                if(exif["YResolution"][0] > 10000):
                                    mydpi = (exif["YResolution"][0]/10000)
                                else:
                                    mydpi = (exif["YResolution"][0])
                            except:
                                #Unknown DPI Case.
                                mydpi=96
                            ScaledDpi, ScalingFactor = 300, 300 # For now.
                            #"File Name,Original DPI, Image Initial Size, Original Height, Original Width, Original Modified Date, New File Size, New File Height, New File Width\n"
                            originalWidth = round(image.width/ mydpi, 2)
                            originalHeight = round(image.height/mydpi, 2)
                            originalSize = (os.path.getsize(originalPathFile)/1000000)
                            newHeight = int(self.newHeight * ScalingFactor)
                            newWidth = int(self.newWidth * ScalingFactor)


                            #---------------------------- Resize Part
                            # print(newHeight, newWidth)
                            # image.resize((50,50))
                            newImage = resizeimage.resize_thumbnail(image, [newHeight, newWidth])
                            # print(newImage.info)
                            newImage.save(targetPath, dpi= (int(ScaledDpi),int(ScaledDpi)))
                            newSize = (os.path.getsize(targetPath) / 1000000)
                            # print(mydpi, round(image.width/ mydpi, 2), round(image.height/mydpi, 2), os.path.getsize(originalPathFile)/1000000, originalPathFile, targetPath)
                        csvFile.write(str(listOfNamings[i]) + ", " +
                                      str(mydpi) + ", " +
                                      str(originalSize) + ", " +
                                      str(originalHeight) + ", " +
                                      str(originalWidth) + ", " +
                                      str(originalTimeStrings[i]) + ", " +
                                      str(originalPathFile) +", " +
                                      str(newSize) + ", " +
                                      str(round(newImage.height/ScalingFactor, 2)) + ", " +
                                      str(round(newImage.width/ScalingFactor, 2)) + ", " +
                                      str(targetPath) +"\n"
                                      )

            csvFile.close()
#Dro_Tim_War_Warsaw14_67

            # with open("lol3erra.jpg", "r+b") as f:
            #     with Image.open(f) as image:
            #         width = 4 * 96
            #         cover = resizeimage.resize_contain(image, [width, width])
            #         details = image.info
            #         print(details)
            #         print("Original Image Size :", image.width / 96, " x ", image.height / 96, "Inches")
            #         print("New Image Size :", cover.width / 96, " x ", cover.height / 96, "Inches")
            #         cover.save("test.jpeg", image.format, dpi=(500,500))


    def listofFilesCleaner(self, listofFiles):
        runner = 0
        while runner < len(listofFiles):
            if(("JPG" not in str(listofFiles[runner]))):
                if ("jpg" not in str(listofFiles[runner])):
                    listofFiles.pop(runner)
                    runner-=1
            runner+=1
        return listofFiles

    def generateNaming(self,path,  listofFiles):
        brokenPath = path.split("\\")
        for i in range(1, len(brokenPath)):
            brokenPath[i] = brokenPath[i][:3]
        word = ""
        for i in range(1, len(brokenPath)):
            if(i+1 < len(brokenPath)):
                word += str(brokenPath[i]) +"_"
            else:
                word += str(brokenPath[i])
        listofBrokenFiles = []
        for i in range(len(listofFiles)):
            listofBrokenFiles.append(str(word) + "_" + listofFiles[i])
        return listofBrokenFiles
        # print(path.split("\\"), listofFiles)

    def getSubDirectories(self):
        print("Getting Sub Directories...")
        walk = os.walk(self.rootDirectory)
        subDirectories = []
        for i in walk:
            subDirectories.append(i[0])
        return subDirectories

    def applyIgnoreList(self):
        print("There are Total of ", len(self.subDirectories), "Directories including:", self.ignoreList)
        print("Removig Unwanted Directories...")
        for i in range(len(self.ignoreList)):
            self.subDirectories = [x for x in self.subDirectories if self.ignoreList[i] not in x]
        print("There are Total of ", len(self.subDirectories), "Directories after Removing unwanted directories")

    def getFilesInSpecificDirectory(self, directoryPth):
        return [f for f in os.listdir(directoryPth) if os.path.isfile(os.path.join(directoryPth, f))]

    def getLastModifiedTime(self, Path, fileNames):
        modifiedDateList = []
        modifiedTimeString = []
        for i in range(len(fileNames)):
            pathPlusName = str(Path) + "\\" + fileNames[i]
            modifiedDateList.append(time.localtime(os.path.getmtime(pathPlusName)))
            modifiedTimeString.append(time.ctime(os.path.getmtime(pathPlusName)))
        return modifiedDateList, modifiedTimeString







#------------------------INPUT

logName = "ImageResizerLog.csv" #THE NAME OF THE LOG. RENAME IF YOU WANT
rootDirectory = "C:\Dropbox (Personal)\ImageCatalog\Collections" #THE ROOT DIRECTORY THAT HAS ALL THE FOLDERS THAT HAS IMAGES
movingDirectory = "\\\\Desktop-t55dtu3\mssqlserver\LigdaArtFileTable\ArtConfirmation" #THE TARGET DIRECTORY WHERE WE MOVE IMAGES
#--movingDirectory = "C:\\resize"
ignoreList = ["Process", "process"]#IGNORE LIST. ADD WHATEVER YOU WANT TO IT!
newHeight = 4 #SET HEIGHT AND WIDTH IN INCHES!
newWidth = 4

#--------------------
resize = ImageResizer(rootDirectory=rootDirectory, ignoreList=ignoreList, movingDirectory=movingDirectory, logName=logName, height=newHeight, width=newWidth)










#-----------------------Dont go down.







#https://www.dropbox.com/scl/fo/p1xod4clwmjiqroe6tk1z/AAAASLNyefeaoHXPt4bkD1Vua/Performance?dl=0
#https://pypi.python.org/pypi/python-resize-image https://pypi.python.org/pypi/python-resize-image
# class ImageResizer():
#     def __init__(self, imagePath, width, height):
#         self.imagePath = imagePath
#         self.width = width
#         self.height = height

# appKey = "ymedmua3xw5xlgq"
# appSecret = "9dy09dvlxdvz24i"

# flow = dropbox.client.DropboxOAuth2FlowNoRedirect(appKey, appSecret)
# flow = dropbox.client.DropboxClient("yTD_VqA7KzAAAAAAAAAAKCPcA4NXNbhfqShcDUT0E_FVcgaeqH_7ePu5t2dK3lTw")
# one = dropbox.Dropbox("yTD_VqA7KzAAAAAAAAAAKCPcA4NXNbhfqShcDUT0E_FVcgaeqH_7ePu5t2dK3lTw")
# print(flow.account_info())
# print(one.users_get_current_account())
# authorizeUrl = flow.start()
# print(authorizeUrl)

# t , b = flow.finish("yTD_VqA7KzAAAAAAAAAAKCPcA4NXNbhfqShcDUT0E_FVcgaeqH_7ePu5t2dK3lTw")
# print(t, b)
# with open("lol3erra.jpg", "r+b") as f:
#     with Image.open(f) as image:
#         width = 4 * 96
#         cover = resizeimage.resize_contain(image, [width, width])
#         details = image.info
#         print(details)
#         print("Original Image Size :", image.width / 96, " x ", image.height / 96, "Inches")
#         print("New Image Size :", cover.width / 96, " x ", cover.height / 96, "Inches")
#         cover.save("test.jpeg", image.format, dpi=(500,500))