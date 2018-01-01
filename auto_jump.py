import os
import cv2
import numpy as np
import time
from PIL import Image, ImageDraw

# 使用的Python库及对应版本：
# python 3.6
# opencv-python 3.3.0
# numpy 1.13.3
# 用到了opencv库中的模板匹配和边缘检测功能


def get_screenshot(i):
    name = '{:05d}_{}'.format(i,int(time.time()))
    os.system('adb shell screencap -p /sdcard/{}.png'.format(name))
    os.system('adb pull /sdcard/{}.png images/{}.png'.format(name,name))
    return os.path.join('images',name+'.png')


def jump(distance):
    # 这个参数还需要针对屏幕分辨率进行优化
    press_time = int(distance * 1.35)
    cmd = 'adb shell input swipe 320 410 320 410 ' + str(press_time)
    os.system(cmd)

def find_center(img1):

  H,W = img1.shape
  img1 = cv2.GaussianBlur(img1, (5, 5), 0)
  canny_img = cv2.Canny(img1, 1, 10)
  cv2.imwrite('test.png',canny_img)
  for row in range(300,H):
    for col in range(W//8,W):
      if canny_img[row,col] !=0 :
        return row, col
      
      
      
if __name__ == '__main__':
  # 第一次跳跃的距离是固定的
  jump(530)
  time.sleep(1)
  
  # 匹配小跳棋的模板
  temp1 = cv2.imread('temp_player.jpg', 0)
  w1, h1 = temp1.shape[::-1]
  # 匹配游戏结束画面的模板
  temp_end = cv2.imread('temp_end.jpg', 0)
  # 匹配中心小圆点的模板
  temp_white_circle = cv2.imread('temp_white_circle.jpg', 0)
  w2, h2 = temp_white_circle.shape[::-1]
  
  # 循环直到游戏失败结束
  for i in range(10000):
      name = get_screenshot(i)
      img_rgb = cv2.imread(name)
      img_gray = cv2.cvtColor(img_rgb,cv2.COLOR_BGR2GRAY)
  
      # 如果在游戏截图中匹配到带"再玩一局"字样的模板，则循环中止
      res_end = cv2.matchTemplate(img_gray, temp_end, cv2.TM_CCOEFF_NORMED)
      if (cv2.minMaxLoc(res_end)[1] > 0.95):
          print('Game over!')
          break
  
      # 模板匹配截图中小跳棋的位置
      res1 = cv2.matchTemplate(img_gray, temp1, cv2.TM_CCOEFF_NORMED)
      min_val1, max_val1, min_loc1, max_loc1 = cv2.minMaxLoc(res1)
      center1_loc = (max_loc1[0] + 39, max_loc1[1] + 189)
      x1 = max_loc1[0] + 39
      y1 = max_loc1[1] + 189
      # 先尝试匹配截图中的中心原点，
      # 如果匹配值没有达到0.95，则使用边缘检测匹配物块上沿
      res2 = cv2.matchTemplate(img_gray, temp_white_circle, cv2.TM_CCOEFF_NORMED)
      min_val2, max_val2, min_loc2, max_loc2 = cv2.minMaxLoc(res2)
      if max_val2 > 0.95:
          print('found white circle!')
          x, y = max_loc2[0] + w2 // 2, max_loc2[1] + h2 // 2
      else:
          img_gray[int(max_loc1[1]-2):int(max_loc1[1]+189),int(max_loc1[0]-2):int(max_loc1[0]+77)] =0
          row, x = find_center(img_gray)
          
          y = y1 - np.sqrt(3)/3 * np.abs(x1 -x)
      # 将图片输出以供调试
      img_rgb = cv2.circle(img_gray, (int(x), int(y)), 10, 255, -1)
      # cv2.rectangle(canny_img, max_loc1, center1_loc, 255, 2)
      cv2.imwrite('last.png', img_gray)
  
      distance = (center1_loc[0] - x) ** 2 + (center1_loc[1] - y) ** 2
      distance = distance ** 0.5
      jump(distance)
      time.sleep(1.3)
