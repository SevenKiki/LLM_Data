from glob import glob
import json
import csv
import re
import os

def convert_english_comma_to_chinese(text):
    """将文本中的英文逗号转换为中文逗号"""
    if text:
        return text.replace(',', '，')
    return text

def parse_json_to_csv(input_file, output_file, index_counter):
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    file_exists = os.path.isfile(output_file)

    with open(output_file, 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['index', 'pureTitle', 'caption', 'tagList', 'audioUrl', 'videoUrl']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # 如果文件不存在，写入表头
        if not file_exists:
            writer.writeheader()

        # 遍历 mixFeeds 数组
        for item in data.get('mixFeeds', []):
            feed = item.get('feed', {})
            
            # 判断是否存在 pureTitle 字段，如果没有则跳过
            pure_title = feed.get('pureTitle', '')
            if not pure_title:
                continue

            caption = feed.get('caption', '')
            
            # 使用正则表达式提取以 # 开头、空格结尾的标签
            tag_list = re.findall(r'#\S+', caption)
            
            audio_url = feed.get('soundTrack', {}).get('audioUrls', [{}])[0].get('url', '')
            
            # 处理 adaptationSet 为列表的情况
            adaptation_set = feed.get('streamManifest', {}).get('adaptationSet', [])
            video_url = ''
            if isinstance(adaptation_set, list) and len(adaptation_set) > 0:
                representation = adaptation_set[0].get('representation', [])
                if isinstance(representation, list) and len(representation) > 0:
                    video_url = representation[0].get('url', '')

            # 将文本中的英文逗号转换为中文逗号
            pure_title = convert_english_comma_to_chinese(pure_title)
            caption = convert_english_comma_to_chinese(caption)
            tag_list = [convert_english_comma_to_chinese(tag) for tag in tag_list]
            audio_url = convert_english_comma_to_chinese(audio_url)
            video_url = convert_english_comma_to_chinese(video_url)

            # 写入一行数据到 CSV
            writer.writerow({
                'index': index_counter,
                'pureTitle': pure_title,
                'caption': caption,
                'tagList': ' | '.join(tag_list),  # 用 | 分隔 tagList
                'audioUrl': audio_url,
                'videoUrl': video_url
            })

            # 增加 index_counter 以保证索引递增
            index_counter += 1
            
    return index_counter

# 获取所有 JSON 文件
for ii in range(1, 21):
    input_json_files = glob(f'FeedJson/Hot{ii}/*.json')  # 替换为你的 JSON 文件路径
    output_csv_file = f'HotData/Hot{ii}.csv'  # 替换为你希望生成的 CSV 文件路径

    # 初始化 index_counter 从 0 开始
    index_counter = 0

    # 处理每个 JSON 文件
    for input_json_file in input_json_files:
        index_counter = parse_json_to_csv(input_json_file, output_csv_file, index_counter)

    print(f"解析完成！数据已保存到 {output_csv_file}")
