import pyautogui,os,cv2,numpy,time,math
from PIL import Image
#1440x2560 DPI 640
#PC:2560*1440 125%缩放
#MuMu窗口宽度：711*1306
def judge(result):
    leftLength=len(result[0])
    rightLength=len(result[1])
    if leftLength < rightLength:
        return False
    elif leftLength > rightLength:
        return True
    else:
        for i in range(leftLength):
            if result[0][i]>result[1][i]:
                return True
            elif result[0][i]==result[1][i]:
                continue
            else:
                return False

#centerPos是问题中间那个问号的位置
def problemScreenShot(position,middlePos):
    centerPos = list(map(int,middlePos))
    position = list(map(int,position))
    nextImgLeft = math.floor(position[0])
    nextImgWidth = math.floor(position[2])
    nextImgHeight = math.floor(centerPos[3] * 0.7)
    nextImgTop = centerPos[1]+centerPos[3]
    img = pyautogui.screenshot(region=(position[0],centerPos[1],position[2],centerPos[3]))
    nextImg = pyautogui.screenshot(region=(nextImgLeft,nextImgTop,nextImgWidth,nextImgHeight))
    return img,nextImg

def OCR(SeparatedCharacters,templateGroup):
    result=[[],[]]
    for j in range(2):
        for character in SeparatedCharacters[j]:
            for i in range(0,10):
                #cv2.imwrite('test.png',character)
                template = templateGroup[i]
                mseResult = mse(character,template)
                #print(f'数字{i},置信度为{mseResult}')
                if mseResult < 0.1:
                    result[j].append(i)
                    break
    print(result)
    return(result)

def mse(img1,img2):
    #先修正尺寸
    size1 = (img1.shape[1],img1.shape[0])
    size2 = (img2.shape[1],img2.shape[0])
    if size1!=size2:
        targetSize = (max(size1[0],size2[0]),max(size1[1],size2[1]))
        img1 = cv2.resize(img1,targetSize,interpolation=cv2.INTER_LINEAR)
        img2 = cv2.resize(img2,targetSize,interpolation=cv2.INTER_LINEAR)
    else:
        targetSize = (img1.shape[1],img2.shape[0])
    img1 = img1.astype(numpy.float64) / 255
    img2 = img2.astype(numpy.float64) / 255
    mse = numpy.mean((img1-img2) ** 2)
    return mse

def sortContours(contours):
    boundingBoxes = [cv2.boundingRect(c) for c in contours]
    (sortedContours,boundingBoxes) = zip(*sorted(zip(contours,boundingBoxes),key=lambda b:b[1][0]))
    return sortedContours

def extractText(contours,img,leftPos):
    contours = sortContours(contours)
    leftResult,rightResult=[],[]
    for i in range(len(contours)):
        x,y,width,height = cv2.boundingRect(contours[i])
        character = img[y:y+height,x:x+width]
        if x < leftPos:
            leftResult.append(character)
        else:
            rightResult.append(character) 
        cv2.imwrite('character.png',character)
    return [leftResult,rightResult]

def move(judgeResult,Location):
    boxLocation=pyautogui.center(Location)
    pyautogui.moveTo(boxLocation)
    if judgeResult == True:
        pyautogui.mouseDown()
        time.sleep(0.008)
        pyautogui.moveRel(80,0,0.005)
        pyautogui.moveRel(-80,80,0.005)
        pyautogui.mouseUp()
    else:
        pyautogui.mouseDown()
        time.sleep(0.008)
        pyautogui.moveRel(-80,0,0.005)
        pyautogui.moveRel(80,80,0.005)
        pyautogui.mouseUp()

def firstImgProcess(img,middleBox,problemBoxPos):
    x=(problemBoxPos[2]-middleBox[2])//2
    y=0
    GreyImg = cv2.cvtColor(numpy.asarray(img),cv2.COLOR_RGB2GRAY)
    _,BinaryImg = cv2.threshold(GreyImg,150,255,cv2.THRESH_BINARY_INV)
    postImg = cv2.rectangle(BinaryImg,(x,y),(x+middleBox[2],y+middleBox[3]),(0,0,0),thickness=-1)
    #cv2.imwrite('test2.png',postImg)
    contours,_ = cv2.findContours(postImg,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    SeparatedCharacters = extractText(contours,postImg,x)
    return SeparatedCharacters

#problemBox是整个问题框,centerPos是问题中间那个问号的位置,接着给问号涂掉防止识别错误 
def nextImgProcess(nextImg,centerPos,problemBoxPos):
    nextImgLeft = math.floor(problemBoxPos[0])
    nextImgWidth = math.floor(problemBoxPos[2])
    nextImgHeight = math.floor(centerPos[3] * 0.7)
    nextImgTop = centerPos[1]+centerPos[3]
    blackBoxWidth = math.floor(centerPos[2] * 0.5)
    x = (problemBoxPos[2] - centerPos[2] ) // 2 + 50
    y = 0
    nextGreyImg = cv2.cvtColor(numpy.asarray(nextImg),cv2.COLOR_RGB2GRAY)
    _,binaryNextImg = cv2.threshold(nextGreyImg,150,255,cv2.THRESH_BINARY_INV)
    postNextImg = cv2.rectangle(binaryNextImg,(x,y),(x+blackBoxWidth,nextImgHeight),(0,0,0),thickness=-1)
    postNextImg = cv2.rectangle(binaryNextImg,(0,y),(20,nextImgHeight),(0,0,0),thickness=-1)
    postNextImg = cv2.rectangle(binaryNextImg,(nextImgWidth-20,y),(nextImgWidth,nextImgHeight),(0,0,0),thickness=-1)
    #cv2.imwrite('test1.png',postNextImg)
    contours,_ = cv2.findContours(postNextImg,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    SeparatedCharacters = extractText(contours,postNextImg,x)
    return SeparatedCharacters

def start():
    try:
        boxLocation=pyautogui.locateOnWindow("imgForPositioning/answerBox.png",'MuMu模拟器12',confidence=0.8,grayscale=True)
        problemBox1Location=pyautogui.locateOnWindow("imgForPositioning/problemBox1.png",'MuMu模拟器12',confidence=0.6,grayscale=True)
        middleBoxLocation=pyautogui.locateOnWindow("imgForPositioning/problemBox11.png",'MuMu模拟器12',confidence=0.3,grayscale=True)
        print(boxLocation,problemBox1Location,middleBoxLocation)
        print("成功定位")
    except pyautogui.ImageNotFoundException:
        print("没找到位置")
    templateGroup=[]
    for i in range(10):
        Template = cv2.imread(f'character/character{i}.png')
        templateGroup.append(cv2.cvtColor(Template,cv2.COLOR_BGR2GRAY))
    for i in range(5):
        time1 = time.perf_counter()
        problemImg,nextproblemImg = problemScreenShot(problemBox1Location,middleBoxLocation)
        firstSeparatedCharacters = firstImgProcess(problemImg,middleBoxLocation,problemBox1Location)
        nextSeparatedCharacters = nextImgProcess(nextproblemImg,middleBoxLocation,problemBox1Location)
        firstProblemText = OCR(firstSeparatedCharacters,templateGroup)
        nextProblemText = OCR(nextSeparatedCharacters,templateGroup)
        firstResult = judge(firstProblemText)
        nextResult = judge(nextProblemText)
        time2=time.perf_counter()
        move(firstResult,boxLocation)
        time.sleep(0.15)
        move(nextResult,boxLocation)
        time3=time.perf_counter()
        print(f'识别耗时:{(time2-time1)*1000}ms,总执行耗时:{(time3-time1)*1000}ms')
        time.sleep(0.44)

if __name__== '__main__':
    pyautogui.PAUSE=0.01
    imgPath=f"{os.path.abspath(__file__)}"
    os.chdir(imgPath.strip('\mainV3.py'))
    start()