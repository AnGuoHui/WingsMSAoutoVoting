import random
import cv2
from paddleocr import PaddleOCR
from ultralytics import YOLO

# 加载图片识别模型-yolov10
model = YOLO('verify/best.pt')
# 加载ocr文字识别模型
ocr = PaddleOCR(use_angle_cls=True, lang='en')  # use_angle_cls=True 可选启用文本方向分类

# 识别图片中需要验证的数字
def get_verify_num(image_path):
    list_num = []
    # 进行文字识别
    result = ocr.ocr(image_path, cls=True)

    # 输出识别结果
    for line in result:
        for word_info in line:
            list_num.append(word_info[1][0])  # 保存识别到的数字
    if len(list_num) == 0:
        return 0
    elif len(list_num) > 1:
        return 0
    else:
        if list_num[0].isdigit():
            return int(list_num[0])
        else:
            return 0

def split_and_verify_img(img_path):
    # 识别到的图片位置，没有识别到返回随机数
    exact_num = random.randint(0, 5)
    # 读取图像
    image = cv2.imread(img_path)

    # 设置切割的行数和列数
    rows = 2  # 设置为切割为几行
    cols = 6  # 设置为切割为几列

    # 获取图像的高度和宽度
    height, width, _ = image.shape

    # 计算每个小图像的高度和宽度
    tile_height = height // rows
    tile_width = width // cols

    # 循环切割图像-倒序，先拿到最后一行需要识别数量的数字
    for i in reversed(range(rows)):
        for j in range(cols):
            # 丢弃第二行第一列以后的图像
            if i == 0 or j == 0:
                # 计算小图像的边界
                start_y = i * tile_height
                start_x = j * tile_width
                end_y = (i + 1) * tile_height if (i + 1) < rows else height
                end_x = (j + 1) * tile_width if (j + 1) < cols else width
                
                # 切割图像
                after_split_img = image[start_y:end_y, start_x:end_x]
                # 第一列是需要识别的图片
                if i == 0 :
                    if match_captcha_num(captcha_num,after_split_img):
                        print(f"在第{j+1}张图片找到对应的验证数量")
                        exact_num = j
                        return exact_num
                if i==1 and j==0:
                    # 第二列第一行是需要识别的数量
                    captcha_num = get_verify_num(after_split_img)
                    if captcha_num == 0 or captcha_num > 6:
                        print("验证码数字识别失败,使用随机数")
                        return exact_num
    return exact_num

def match_captcha_num(captcha_num, after_split_img):
    # 使用模型进行推理
    results = model(after_split_img)

    # 获取识别结果
    detections = results[0].boxes

    rock_num = len(detections)
    print(f"识别到{rock_num}个目标")
    # 在原图上绘制检测到的目标
    # for box in detections:
    #     # 获取边界框坐标和置信度
    #     x1, y1, x2, y2 = map(int, box.xyxy[0])  # 左上角和右下角的坐标
    #     conf = box.conf[0]  # 置信度
    #     cls = int(box.cls[0])  # 类别索引（如果有分类，需要根据需要映射到类别名称）
    #     # 在图像上绘制边界框
    #     cv2.rectangle(after_split_img, (x1, y1), (x2, y2), (0, 255, 0), 2)  # 用绿色绘制边界框
    #     # 在边界框上方显示置信度和类别
    #     cv2.putText(after_split_img, f'Class: {cls}, Conf: {conf:.2f}', (x1, y1 - 10),
    #                 cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

    # # 显示结果
    # cv2.imshow('Detection Result', after_split_img)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    if rock_num == captcha_num:
        print("获取到验证图片")
        return True
    else:
        print("未获取到验证图片，继续识别")
        return False


if __name__ == '__main__':
    split_and_verify_img('verify_img/downloaded_file.png')