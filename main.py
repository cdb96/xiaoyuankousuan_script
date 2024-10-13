import pyautogui,os,cv2,numpy,time
from PIL import Image
#2560*1440 DPI 640
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

def problemScreenShot(position,middlePos):
    centerPos = list(map(int,middlePos))
    position = list(map(int,position))
    img = pyautogui.screenshot(region=(position[0],centerPos[1],position[2],centerPos[3]))
    return img

def OCR(img,middleBox,problemBox,templateGroup):
    problemBoxPos = list(map(int,problemBox))
    x=(problemBoxPos[2]-middleBox[2])//2
    y=0
    GreyImg = cv2.cvtColor(numpy.asarray(img),cv2.COLOR_RGB2GRAY)
    _,BinaryImg = cv2.threshold(GreyImg,50,255,cv2.THRESH_BINARY_INV)
    postImg = cv2.rectangle(BinaryImg,(x,y),(x+middleBox[2],y+middleBox[3]),(0,0,0),thickness=-1)
    contours,_ = cv2.findContours(postImg,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    SeparatedCharacters = extractText(contours,postImg,x)
    #cv2.imwrite('1.png',postImg)
    result=[[],[]]
    for j in range(2):
        for character in SeparatedCharacters[j]:
            for i in range(0,10):
                #cv2.imwrite('test.png',character)
                template = templateGroup[i]
                mseResult = mse(character,template)
                print(f'数字{i},置信度为{mseResult}')
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

def start():
    try:
        boxLocation=pyautogui.locateOnWindow("imgForPositioning/answerBox.png",'MuMu模拟器12',confidence=0.8,grayscale=True)
        problemBox1Location=pyautogui.locateOnWindow("imgForPositioning/problemBox1.png",'MuMu模拟器12',confidence=0.3,grayscale=True)
        middleBoxLocation=pyautogui.locateOnWindow("imgForPositioning/problemBox11.png",'MuMu模拟器12',confidence=0.3,grayscale=True)
        print(boxLocation,problemBox1Location,middleBoxLocation)
        print("成功定位")
    except pyautogui.ImageNotFoundException:
        print("没找到位置")
    templateGroup=[]
    for i in range(10):
        Template=cv2.imread(f'character/character{i}.png')
        templateGroup.append(cv2.cvtColor(Template,cv2.COLOR_BGR2GRAY))
    for _ in range(10):
        time1=time.perf_counter()
        problemImg=problemScreenShot(problemBox1Location,middleBoxLocation)
        problemText=OCR(problemImg,middleBoxLocation,problemBox1Location,templateGroup)
        result=judge(problemText)
        time2=time.perf_counter()
        move(result,boxLocation)
        time3=time.perf_counter()
        print(f'识别耗时:{(time2-time1)*1000}ms,总执行耗时:{(time3-time1)*1000}ms')
        time.sleep(0.42)

if __name__== '__main__':
    pyautogui.PAUSE=0.012
    imgPath=f"{os.path.abspath(__file__)}"
    os.chdir(imgPath.strip('\main.py'))
    start()