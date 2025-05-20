import json
import os
import re
from global_func_and_v import Msg, read_chattingContact, is_valid_MSG, read_message

def new_write_json(filename,content_list,force_me_first=False):
    """
    input: filename, 输出文件名; content_list, 聊天记录列表; force_me_first, 是否强制把“我”放在第一条消息前面
    output: None
    单轮写入，每次来回写成一段；如果force_me_first为True，则强制把“我”放在第一条消息前面
    """
    #下面情况需要减去头部：1.必须我先但不是我先；2.必须别人先但我先
    if (force_me_first and content_list[0][0] != "我") or (not force_me_first and content_list[0][0]  == "我"):
        content_list = content_list[1:]

    #由于内容nameset导致对象划分出现问题，或者纯粹内容太短，则不写入直接结束
    if len(content_list) <2:return

    with open(filename, 'a', encoding='utf-8') as file:
        # 处理每一对话
        for i in range(0, len(content_list) - 1, 2):  # 步长为2，确保每对话是成对的
            conversation = [
                {"role": "user", "content": re.sub(r'[，;,；]{2,}', ',', content_list[i][1])},
                {"role": "assistant", "content": re.sub(r'[，;,；]{2,}', ',', content_list[i+1][1])}
            ]
            json.dump({"conversations": conversation}, file, ensure_ascii=False)
            file.write("\n")
 
def read_chattingRecord(file,output_name,me_first=True):
    """
    input: file object,文件对象; output_name,输出文件名;me_first,是否强制把“我”放在第一条消息前面
    output: bool,是否成功读取文件
    主读取函数，读取QQ聊天记录，将聊天记录转换为JSON(L)格式并写入文件
    """
    with open(file, 'r', encoding='utf-8') as f:
        content_list = []

        #读取联系人名，简单判断是否符合格式
        contact = read_chattingContact(f)
        if not contact: return False

        # 读取第一条有效消息,确保正确开始读取聊天
        while True:
            last_msg = read_message(f,contact)
            if is_valid_MSG(last_msg):break

        while True:
            cur_msg = read_message(f,contact)

            #读不到新消息，结束读取，最后写入json
            if cur_msg is None:
                content_list.append((last_msg.role, last_msg.message))
                if len(content_list) >= 2:
                    new_write_json(output_name,content_list,me_first)
                content_list = []
                break
            # 跳过无效消息
            if not is_valid_MSG(cur_msg) or not cur_msg.role:continue

            #读取逻辑：1.间隔大，视为新话题 2.角色相同，合并消息 3.角色不同，写入json（l），清空列表
            if abs((cur_msg.time - last_msg.time).total_seconds()) > 6*3600:   #时间间隔超过12小时，写入json，清空列表
                content_list.append((last_msg.role, last_msg.message))
                if len(content_list) >= 2:
                    new_write_json(output_name,content_list,me_first)
                content_list = []
            elif cur_msg.role == last_msg.role:     #角色相同，合并上一条消息并更新时间内容
                cur_msg = Msg(cur_msg.time, last_msg.role, last_msg.message +cur_msg.message)
            else:
                content_list.append((last_msg.role, last_msg.message))
            #更新上一条消息
            last_msg = cur_msg
    #print(f'{os.path.basename(file)} DONE')
    return True

def handle_dirRecords(dir,ouput_filepath,robot_me = True):
    """
    input: dir,目录路径;robot_other，表示得到的是否是以别人为“我”，默认为true表示还是以自己为“我”
    ouput: int,成功处理的文件数
    文件处理入口，负责一个个处理txt文件，将原始数据进行对象分类、清洗、转化，输出为jsonl格式
    """
    #设置是否强制把“我”放在前面
    if_me_first = robot_me


    #先清空文件,避免叠加写入
    if os.path.exists(ouput_filepath):os.remove(ouput_filepath)

    #result_rsp用于记录成功处理的文件数，如果为0表示可能全部提供的文件都有问题
    result_rsp = 0

    #ouput_filepath = output_name
    for filename in os.listdir(dir):
        if filename.endswith(".txt"):
            filepath = os.path.join(dir, filename)
            result_rsp += read_chattingRecord(filepath,ouput_filepath,if_me_first)
            
    print(f'DONE output to {ouput_filepath}')
    return result_rsp


