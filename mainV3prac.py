import pyautogui,os,cv2,numpy,time,math
import mss.screenshot
#1440x2560 DPI 640
#PC:2560*1440 125%缩放
#MuMu窗口宽度：711*1306

#centerPos是问题中间那个问号的位置
def problemScreenShot(position,middlePos):
    centerPos = list(map(int,middlePos))
    position = list(map(int,position))
    nextImgLeft = math.floor(position[0])
    nextImgWidth = math.floor(position[2])
    nextImgHeight = math.floor(centerPos[3] * 0.7)
    nextImgTop = centerPos[1]+centerPos[3]
    firstImgRegion = {"left": position[0]+50, "top": centerPos[1]-220, "width": position[2]-53, "height": centerPos[3]}
    nextImgRegion = {"left": position[0]+50, "top": centerPos[1], "width": position[2]-53, "height": centerPos[3]}
    with mss.mss() as screenShot:
        firstImg = screenShot.grab(firstImgRegion)
        nextImg = screenShot.grab(nextImgRegion)
    return firstImg,nextImg

def recognition(SeparatedCharacters,templateGroup):
    if len(SeparatedCharacters[0]) > len(SeparatedCharacters[1]):
        return True
    elif len(SeparatedCharacters[0]) < len(SeparatedCharacters[1]):
        return False
    for i in range(len(SeparatedCharacters[0])):
        leftDigitImg = SeparatedCharacters[0][i]
        rightDigitImg = SeparatedCharacters[1][i]
        leftDigit,leftMinMSE = 0,1
        for sequence,template in enumerate(templateGroup):
            leftMSE = imgDiffCalc(leftDigitImg,template)
            if leftMSE < 0.06:
                leftDigit = sequence
                break
            if leftMSE < leftMinMSE:
                leftDigit,leftMinMSE = sequence,leftMSE
        rightDigit,rightMinMSE = 0,1
        for sequence,template in enumerate(templateGroup):
            rightMSE = imgDiffCalc(rightDigitImg,template)
            if rightMSE < 0.06:
                rightDigit = sequence
                break
            if rightMSE < rightMinMSE:
                rightDigit,rightMinMSE = sequence,rightMSE
        print(f'第{i+1}位,左边数字为{leftDigit},右边数字为{rightDigit}')
        if leftDigit > rightDigit:
            return True
        elif leftDigit < rightDigit:
            return False
    return 'Equal'

def imgDiffCalc(img1,img2):
    #先修正尺寸,然后计算均方误差
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
    return [leftResult,rightResult]

def move(judgeResult,Location):
    boxLocation=pyautogui.center(Location)
    pyautogui.moveTo(boxLocation)
    if judgeResult == True:
        pyautogui.middleClick()
    elif judgeResult == 'Equal':
        pyautogui.press('space')
        time.sleep(0.095)
    else:
        pyautogui.rightClick()
    
def firstImgProcess(img,middleBox,problemBoxPos):
    x = (problemBoxPos[2]-middleBox[2])//2
    y = 0
    GreyImg = cv2.cvtColor(numpy.asarray(img),cv2.COLOR_RGB2GRAY)
    _,BinaryImg = cv2.threshold(GreyImg,50,255,cv2.THRESH_BINARY_INV)
    postImg = cv2.rectangle(BinaryImg,(x-30,y),(x+middleBox[2]-20,y+middleBox[3]),(0,0,0),thickness=-1)
    #cv2.imwrite('test2.png',postImg)
    contours,_ = cv2.findContours(postImg,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    SeparatedCharacters = extractText(contours,postImg,x)
    return SeparatedCharacters

#problemBox是整个问题框,centerPos是问题中间那个问号的位置,接着给问号涂掉防止识别错误 
def nextImgProcess(nextImg,centerPos,problemBoxPos):
    #nextImgLeft = math.floor(problemBoxPos[0])
    #nextImgWidth = math.floor(problemBoxPos[2])
    nextImgHeight = math.floor(centerPos[3] * 0.7)
    #nextImgTop = centerPos[1]+centerPos[3]
    blackBoxWidth = math.floor(centerPos[2] * 0.5)
    x = (problemBoxPos[2] - centerPos[2] ) // 2 + 50
    y = 0
    nextGreyImg = cv2.cvtColor(numpy.asarray(nextImg),cv2.COLOR_RGB2GRAY)
    _,binaryNextImg = cv2.threshold(nextGreyImg,150,255,cv2.THRESH_BINARY_INV)
    postNextImg = cv2.rectangle(binaryNextImg,(x,y),(x+blackBoxWidth-60,nextImgHeight),(0,0,0),thickness=-1)
    postNextImg = cv2.rectangle(binaryNextImg,(0,y),(20,nextImgHeight),(0,0,0),thickness=-1)
    #postNextImg = cv2.rectangle(binaryNextImg,(nextImgWidth-50,y),(nextImgWidth-25,nextImgHeight),(0,0,0),thickness=-1)
    #cv2.imwrite('test1.png',postNextImg)
    contours,_ = cv2.findContours(postNextImg,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    SeparatedCharacters = extractText(contours,postNextImg,x)
    return SeparatedCharacters

def start():
    try:
        boxLocation=pyautogui.locateOnWindow("imgForPositioning/box3.png",'MuMu模拟器12',confidence=0.6,grayscale=False)
        problemBox1Location=pyautogui.locateOnWindow("imgForPositioning/box5.png",'MuMu模拟器12',confidence=0.7,grayscale=False)
        middleBoxLocation=pyautogui.locateOnWindow("imgForPositioning/box4.png",'MuMu模拟器12',confidence=0.7,grayscale=False)
        print(boxLocation,problemBox1Location,middleBoxLocation)
        print("成功定位")
    except pyautogui.ImageNotFoundException:
        print("没找到位置")
    templateGroup=[]
    for i in range(10):
        Template = cv2.imread(f'character/character{i}.png')
        templateGroup.append(cv2.cvtColor(Template,cv2.COLOR_BGR2GRAY))
    while 1:
        for i in range(5) :
            time1 = time.perf_counter()
            problemImg,nextproblemImg = problemScreenShot(problemBox1Location,middleBoxLocation)
            timeShot = time.perf_counter()
            firstSeparatedCharacters = firstImgProcess(problemImg,middleBoxLocation,problemBox1Location)
            firstResult = recognition(firstSeparatedCharacters,templateGroup)
            time2 = time.perf_counter()
            move(firstResult,boxLocation)
            print('进入下一题预处理')
            nextSeparatedCharacters = nextImgProcess(nextproblemImg,middleBoxLocation,problemBox1Location)
            nextResult = recognition(nextSeparatedCharacters,templateGroup)
            time.sleep(0.36)
            move(nextResult,boxLocation)
            time3=time.perf_counter()
            print(f'截图耗时:{(timeShot-time1)*1000}ms,识别耗时:{(time2-timeShot)*1000}ms,总执行耗时:{(time3-time1)*1000}ms')
            time.sleep(0.42)
        input('按任意键重开')

if __name__== '__main__':
    pyautogui.PAUSE=0.01
    imgPath=f"{os.path.abspath(__file__)}"
    os.chdir(imgPath.strip(os.path.basename(__file__)))
    start()