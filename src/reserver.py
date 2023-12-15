import time
import datetime
import cv2
import numpy as np
import base64
import re
from typing import Tuple
from playwright.sync_api import Playwright, sync_playwright


class Reserver():
    def __init__(self, **kwargs) -> None:
        self._username = kwargs["username"]
        self._password = kwargs["password"]
        self._daytime = kwargs["daytime"]
        self._location = kwargs["location"]
        self._date = kwargs["date"]
        self._wait_time = kwargs["wait_time"]
        self._getnow = kwargs["getnow"]
        self._get_time = "07:00"
    

    #获取日期
    def _get_day(self) -> Tuple[str, bool]:
        week_list = ["星期一","星期二","星期三","星期四","星期五","星期六","星期日"]
        today = datetime.date.today()
        if self._date == "":
            reserve_day = today + datetime.timedelta(days=2)
        else:
            try:
               reserve_day =  datetime.datetime.strptime(self._date, "%Y-%m-%d")
            except ValueError as e:
                print(f"错误: {e}")
        next_button = True if (today.weekday()>=5 and reserve_day.weekday()<3) else False
        day_str = reserve_day.strftime("%Y-%m-%d") + week_list[reserve_day.weekday()]
        return day_str, next_button
    

    #找到图像缺口左边那条线的值
    def _get_left_line(self, img) -> int:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 特定像素值
        lower = (192, 192, 192)  
        upper = (192, 192, 192)
        mask = cv2.inRange(img, lower, upper)

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        leftmost = tuple(contours[0][contours[0][:,:,0].argmin()][0])
        topmost = tuple(contours[0][contours[0][:,:,1].argmin()][0])
        left_line = min(leftmost[0], topmost[0])

        return left_line


    #渐进移动
    def _get_track(self, distance) -> list:
        track = []
        current = 0
        mid = distance * 4 / 5
        t, v = 0.5, 1
        while current < distance:
            a = 3 if current < mid else -4
            v0 = v
            v = v0 + a * t
            move = v0 * t + 1 / 2 * a * t * t
            if current + move < distance:
                track.append(round(move))
            else:
                track.append(distance-current)
            current+=move
        return track
    

    def run(self) -> None:
        with sync_playwright() as p:
            browser_type = p.chromium
            browser = browser_type.launch(headless=False)
            page = browser.new_page()
            page.goto('https://uis.fudan.edu.cn/authserver/login?service=https%3A%2F%2Felife.fudan.edu.cn%2Flogin2.action')
            page.fill('//*[@id="username"]',self._username)
            page.fill('//*[@id="password"]',self._password)
            page.click('//*[@id="idcheckloginbtn"]')
            print('登陆成功')
            with page.expect_popup() as popup_info:
                page.get_by_role("listitem").filter(has_text="场馆预约").get_by_role("link").first.click()
            page1=popup_info.value
            iframe = page1.frame_locator("iframe[name=\"contentIframe\"]")


            #   这段代码是找指定项目的，该页没找到就点击下一页，直到没有下一页按钮
            sport_str = re.compile(f"服务项目： {self._location} .* 立即预订")
            while True:
                try:
                    iframe.get_by_role("cell", name=sport_str).get_by_role("link", name="立即预订").click(timeout=7000)
                    break
                except Exception as e:
                    pass
                next_page_button = iframe.get_by_role("link", name="下一页")
                next_str = iframe.get_by_text(re.compile("页次:\d/\d页.*")).inner_text()
                if next_str[4] == next_str[6]:
                    print("没找到指定项目，其检查参数是否正确")
                    raise Exception("No next page button found.")
                next_page_button.click()
                print("Clicked on the next page button.")


            day, next = self._get_day()
            if next:
                iframe.locator(".right").click()     # 点击下一周
            if self._getnow == False:
                while True:
                    if (datetime.datetime.now().strftime("%H:%M")==self._get_time):break
            time.sleep(self._wait_time)
            iframe.get_by_text(day).click()
            while(True):
                if (iframe.get_by_text(day).get_attribute('class')=='hover'):        #跳到目标日期后再执行下步
                    break
            time_str = str(self._daytime).zfill(2)+(':00 ')+str(self._daytime+1).zfill(2)+(':00')
            iframe.get_by_role("row", name=re.compile(time_str+" "+ self._location)).get_by_role("img").click()
            # print("场次选择完毕")
            iframe.locator('//*[@id="verify_button"]').click()
            captcha_data = iframe.locator('//*[@id="scream"]').get_attribute('src')
            captcha_data = captcha_data.replace('data:image/jpg;base64,', '')
            missing_padding = 4 - len(captcha_data) % 4
            if missing_padding:
                captcha_data += '=' * missing_padding
            img_arr = np.frombuffer(base64.b64decode(captcha_data), np.uint8)
            captcha_img = cv2.imdecode(img_arr,cv2.COLOR_RGB2BGR)
            left = self._get_left_line(captcha_img)
            w = captcha_img.shape[1]
            pixel_distance=int(left * 270 / w - 4)
            box = iframe.locator('//*[@id="imgVer"]/div[2]/div[2]').bounding_box()
            

            print("开始滑动验证码")
            page1.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
            page1.mouse.down()
            x = box["x"] + box["width"] / 2
            tracks = self._get_track(pixel_distance)
            for track in tracks:
                page1.mouse.move(x + track, 0,steps=2)
                x += track
            page1.mouse.up()
            page1.frame_locator("iframe[name=\"contentIframe\"]").locator('//*[@id="btn_sub"]').click()


            browser.close()
            print('预约成功')