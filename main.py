import os
import random
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from verify.verify_cap import split_and_verify_img

current_path = os.getcwd()
download_directory = os.path.join(current_path, 'verify_img')
options = webdriver.ChromeOptions()
options.add_argument('--disable-gpu')  # 禁用GPU加速
options.add_argument('--disable-software-rasterizer')
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36')
options.add_experimental_option('excludeSwitches', ['enable-automation'])
prefs = {"download.default_directory": download_directory}
options.add_experimental_option("prefs", prefs)


# 创建一个Chrome浏览器实例
driver = webdriver.Chrome(options=options)
driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
    'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
})
try:
    your_vote_url = 'https://gtop100.com/topsites/MapleStory/sitedetails/WingsMS--GMS-v083--101352?vote=1&pingUsername=yourUsername'
    # 打开网页
    driver.get(your_vote_url)

    # 等待按钮可点击
    button_vote = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="votebutton"]'))
    )
    time.sleep(1)
    button_vote.click()  

    # 切换到iframe
    iframe_element = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[title='Verification challenge']"))
    )
    driver.switch_to.frame(iframe_element)


    iframe_id = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.ID, "game-core-frame"))
    )

    driver.switch_to.frame(iframe_id)

    # 等待按钮可点击
    button_question = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="root"]/div/div[1]/button'))
    )
    time.sleep(1)
    button_question.click() 

    # 查找验证码图片
    image_element = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/div/div[1]/div/div/div[2]/div[1]/img'))
    )

    # 获取 style 属性
    style = image_element.get_attribute('style')

    print("提取的 style 属性:", style)

    # 使用正则表达式匹配 blob URL
    match = re.search('background-image:\s*url\("([^"]+)"\)', style)
    if match:
        blob_url = match.group(1)
        print("提取的 blob URL:", blob_url)
        # 使用 JavaScript 下载 blob URL 指向的内容
        download_script = f"""
        var a = document.createElement('a');
        a.href = '{blob_url}';
        a.download = 'downloaded_file.png';  // 设置文件名
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        """
        driver.execute_script(download_script)

    # 等待下载完成，视网络情况放大或缩小等待时间
    time.sleep(5)

    # 获取需要移动到验证图片位置
    swith_num = split_and_verify_img(os.path.join(download_directory, 'downloaded_file.png'))

    # 切换图片
    button_swith = driver.find_element(By.XPATH, '//*[@id="root"]/div/div[1]/div/div/div[2]/div[1]/a[2]')
    time.sleep(1)
    if swith_num == 0:
        button_swith.click()
    else:
        for i in range(swith_num):
            time.sleep(random.uniform(0.3, 0.5))
            button_swith.click()
    
    # 提交
    button_submit = driver.find_element(By.XPATH, '//*[@id="root"]/div/div[1]/div/button')
    time.sleep(random.uniform(0.5, 1))
    button_submit.click()

    # 等待页面跳转
    WebDriverWait(driver, 30).until(EC.url_changes(your_vote_url))
    time.sleep(random.uniform(1.5, 2))
    # 获取新的 URL
    new_url = driver.current_url
    if new_url != your_vote_url:
        print("页面已跳转，投票成功")
    else:
        print("投票失败") 
    
    time.sleep(5)
except Exception as e:
    print(f"发生错误: {e}")
finally:
    # 关闭浏览器
    driver.quit()
    # 删除下载的验证码图片
    os.remove(os.path.join(download_directory, 'downloaded_file.png'))