#!/bin/bash

# 输入文件名
INPUT_FILE="boxartfront_err.txt"

# 检查输入文件是否存在
if [ ! -f "$INPUT_FILE" ]; then
    echo "错误：文件 $INPUT_FILE 不存在！"
    exit 1
fi

# 创建下载日志文件
LOG_FILE="download_log.txt"
> "$LOG_FILE"

# 开始处理每一行
while IFS= read -r url; do
    # 去除首尾空白字符
    url=$(echo "$url" | xargs)

    # 忽略空行
    if [ -z "$url" ]; then
        continue
    fi

    # 提取路径部分（去掉域名后的路径）
    path=$(echo "$url" | sed -E 's|https?://[^/]+/(.*)|\1|')

    # 构造本地文件夹和文件名
    dir=$(dirname "$path")
    filename=$(basename "$path")

    # 创建目标目录
    mkdir -p "$dir"

    # 下载图片并保存为 .png
    output_path="$dir/$filename".png
    echo "正在下载：$url -> $output_path"
    wget -O "$output_path" "$url" >> "$LOG_FILE" 2>&1

    if [ $? -eq 0 ]; then
        echo "✅ 成功：$url -> $output_path"
    else
        echo "❌ 失败：无法下载 $url"
    fi

done < "$INPUT_FILE"

echo "下载完成。详细日志请查看：$LOG_FILE"
