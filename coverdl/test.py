from PIL import Image
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

# 损坏文件记录文件
CORRUPTED_LOG = "boxartsm_err.txt"

def check_image_integrity(image_path):
    try:
        with Image.open(image_path) as img:
            img.verify()  # 快速验证文件头
            # 加载整个图像数据以进一步验证
            img = Image.open(image_path)
            img.load()
        return True  # 图像正常
    except (IOError, SyntaxError) as e:
        print(f'图像 {image_path} 损坏或无法读取: {e}')
        return False  # 返回 False 表示损坏

def log_corrupted_file(file_path):
    """线程安全地记录损坏的文件"""
    with open(CORRUPTED_LOG, "a", encoding="utf-8") as f:
        f.write(file_path + "\n")

def process_files_in_batch(file_list, batch_size=10):
    with ThreadPoolExecutor(max_workers=batch_size) as executor:
        future_to_img = {executor.submit(check_image_integrity, img): img for img in file_list}
        for future in as_completed(future_to_img):
            img = future_to_img[future]
            try:
                is_valid = future.result()
                if not is_valid:
                    log_corrupted_file(img)
            except Exception as exc:
                print(f'{img} 执行时发生异常: {exc}')
                log_corrupted_file(img)

def batch_generator(directory, batch_size=10):
    images = [os.path.join(directory, f) for f in os.listdir(directory) if f.lower().endswith(('png', 'jpg', 'jpeg', 'bmp', 'gif'))]
    for i in range(0, len(images), batch_size):
        yield images[i:i + batch_size]

# 设置扫描目录和批次大小
directory = 'boxartsm'
batch_size = 5  # 根据内存调整

# 清空旧的日志文件（可选）
if os.path.exists(CORRUPTED_LOG):
    os.remove(CORRUPTED_LOG)

# 开始处理
for batch in batch_generator(directory, batch_size):
    process_files_in_batch(batch, batch_size)

print(f"处理完成，损坏文件列表已保存至：{CORRUPTED_LOG}")
