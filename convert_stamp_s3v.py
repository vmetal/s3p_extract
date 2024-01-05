import os, subprocess, shutil, platform

voiceName = "rasys"

source = r"FULLPATH_OF_SOURCE_HERE"
output = r"FULLPATH_OF_OUTPUT_HERE/" + voiceName
vgmstream = r"FULLPATH_OF_BINFIKE_HERE/vgmstream-cli.exe"

customPath = "data/sound/stamp/" + voiceName


if "Windows" == platform.system():
    FFMPEG = r"ffmpeg.exe"
else:
    FFMPEG = r"/usr/bin/env ffmpeg"


def getTargetFiles(sourcePath: str,targetExt: str):
    targetPath = []
    filepath = os.path.join(sourcePath, customPath)
    for filename in listDirFilePath(filepath):
        if filename.endswith(targetExt):
            targetPath.append(filename)
    return targetPath



# Credits to giltay @ stackoverflow 120656
def listDirFilePath(d):
    return [os.path.join(d, f) for f in os.listdir(d)]

def convertS3VtoWAV(files):
    cmd = vgmstream
    for file in files:
        cmd += " \"" + file + "\""
    subprocess.run(cmd, shell=True)

def getWorkingDir():
    workingDirs = []
    for path in listDirFilePath(os.path.join(source,customPath)):
        if os.path.isdir(path):
            workingDirs.append(path)
    return workingDirs
    
def cleaning(workingDirs):
    for workdir in workingDirs:
        for file in listDirFilePath(workdir):
            os.remove(file)
        os.removedirs(workdir)

def rename(outPath :str, output :str):
    tmp = os.path.basename(outPath)
    pathTemp = os.path.splitext(tmp)[0]
    basename = os.path.splitext(pathTemp)[0]
    srcPath = os.path.join(os.path.dirname(outPath),basename)
    destPath = os.path.join(output, os.path.basename(basename))
    renamed = []
    for audioPath in listDirFilePath(outPath):
        renamedPath = getDefName(audioPath, defMap)
        outPath = os.path.join(destPath, os.path.basename(renamedPath))
        if not os.path.exists(destPath):
            os.makedirs(destPath)
        shutil.copy(audioPath, outPath)
        renamed.append(outPath)
    return renamed
    
    
def filterNotExists(files):
    dirlists = listDirFilePath(output)
    target = []
    for file in files:
        filename = os.path.splitext(os.path.basename(file))[0]
        if not os.path.exists(os.path.join(output,filename)):
            target.append(file)
    return target

def convertAudio(filepaths):
    for filepath in filepaths:
        savedir = os.path.dirname(filepath)
        filename = os.path.splitext(os.path.basename(filepath))[0]
        outName1 = os.path.join(savedir, filename + ".wav")
        if not os.path.exists(os.path.dirname(outName1)):
            os.makedirs(os.path.dirname(outName1))

def main(argv = None):
    targetFiles = getTargetFiles(source, ".s3v")
    if not os.path.exists(output):
        os.makedirs(output)
    targetS3VFiles = filterNotExists(targetFiles)
    if len(targetS3VFiles) > 0:
        convertS3VtoWAV(targetS3VFiles)

    s3vOutDirs = getWorkingDir()
    if len(s3vOutDirs) > 0:
        for s3vOutDirPath in s3vOutDirs:
            s3vBaseName = os.path.splitext(os.path.basename(s3vOutDirPath))[0]
            if os.path.exists(os.path.join(output, s3vBaseName)):
                continue
            renamedPaths = rename(s3vOutDirPath, output)
            convertAudio(renamedPaths)
        cleaning(s3vOutDirs)

main()


