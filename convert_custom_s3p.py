import os, subprocess, shutil, platform


source = r"FULLPATH_OF_SOURCE_HERE"
output = r"FULLPATH_OF_OUTPUT_HERE"
s3pExtract = r"FULLPATH_OF_BINFIKE_HERE/s3p_extract.exe"

customPath = "data/sound/custom"


if "Windows" == platform.system():
    FFMPEG = r"ffmpeg.exe"
else:
    FFMPEG = r"/usr/bin/env ffmpeg"


def getS3PFiles(sourcePath):
    targetPath = []
    filepath = os.path.join(sourcePath, customPath)
    for filename in listDirFilePath(filepath):
        if filename.endswith(".s3p"):
            targetPath.append(filename)
    return targetPath



# Credits to giltay @ stackoverflow 120656
def listDirFilePath(d):
    return [os.path.join(d, f) for f in os.listdir(d)]

def convertS3PtoWMA(files):
    cmd = s3pExtract
    for file in files:
        cmd += " \"" + file + "\""
    subprocess.run(cmd, shell=True)

def getWorkingDir():
    workingDirs = []
    for path in listDirFilePath(os.path.join(source,customPath)):
        if path.endswith(".s3p.out") and os.path.isdir(path):
            workingDirs.append(path)
    return workingDirs
    
def cleaning(workingDirs):
    for workdir in workingDirs:
        for file in listDirFilePath(workdir):
            os.remove(file)
        os.removedirs(workdir)

def getDefMap(s3pDirPath):
    s3pBasename = os.path.splitext(os.path.basename(s3pDirPath))[0]
    defPath = os.path.join(source,customPath,s3pBasename)+".def"
    if os.path.exists(defPath):
        with open(defPath, 'rt') as f:
            output=[]
            for defText in f.readlines():
                map = parseDef(defText)
                output.append(map)
        return output

def getDefName(s3pFilepath, defMap):
    basename = os.path.splitext(os.path.basename(s3pFilepath))
    index = basename[0]
    ext = basename[1]
    for map in defMap:
        if map[1] == index:
            return map[0] + ext
    return os.path.basename(s3pFilepath)

def parseDef(line):
    separated = line.split()
    separated.remove('#define')
    return separated

def renameWMA(s3pOutPath, output):
    tmp = os.path.basename(s3pOutPath)
    s3pPathTemp = os.path.splitext(tmp)[0]
    s3pBasename = os.path.splitext(s3pPathTemp)[0]
    srcs3pPath = os.path.join(os.path.dirname(s3pOutPath),s3pBasename)
    defMap = getDefMap(srcs3pPath)
    destPath = os.path.join(output, os.path.basename(s3pBasename))
    renamed = []
    for wmaPath in listDirFilePath(s3pOutPath):
        newWmaPath = getDefName(wmaPath, defMap)
        outPath = os.path.join(destPath, os.path.basename(newWmaPath))
        if not os.path.exists(destPath):
            os.makedirs(destPath)
        shutil.copy(wmaPath, outPath)
        renamed.append(outPath)
    return renamed
    
def filterNotExists(s3pFiles):
    dirlists = listDirFilePath(output)
    target = []
    for s3pFile in s3pFiles:
        s3pName = os.path.splitext(os.path.basename(s3pFile))[0]
        if not os.path.exists(os.path.join(output,s3pName)):
            target.append(s3pFile)
    return target

def convertAudio(filepaths):
    for filepath in filepaths:
        savedir = os.path.dirname(filepath)
        filename = os.path.splitext(os.path.basename(filepath))[0]
        filename = os.path.basename(os.path.dirname(filepath)) + "_" + filename
        outName1 = os.path.join(savedir, "m4a", filename + ".m4a")
        outName2 = os.path.join(savedir, "m4r", filename + ".m4r")
        if not os.path.exists(os.path.dirname(outName1)):
            os.makedirs(os.path.dirname(outName1))
        if not os.path.exists(os.path.dirname(outName2)):
            os.makedirs(os.path.dirname(outName2))
        
        cmd = '''"%s" -i "%s" -codec:a aac  "%s"'''
        exe_cmd = cmd % (FFMPEG, filepath, outName1)
        print(exe_cmd)
        subprocess.run(exe_cmd, shell=True, check=True)
        shutil.copy(outName1, outName2)

def main(argv = None):
    s3pFiles = getS3PFiles(source)
    targetS3PFiles = filterNotExists(s3pFiles)
    if len(targetS3PFiles) > 0:
        convertS3PtoWMA(targetS3PFiles)

    s3pOutDirs = getWorkingDir()
    if len(s3pOutDirs) > 0:
        for s3pOutDirPath in s3pOutDirs:
            s3pBaseName = os.path.splitext(os.path.basename(s3pOutDirPath))[0]
            if os.path.exists(os.path.join(output, s3pBaseName)):
                continue
            renamedPaths = renameWMA(s3pOutDirPath, output)
            convertAudio(renamedPaths)
        cleaning(s3pOutDirs)

main()


