from global_func_and_v import Msg,init_MYNAME,read_chattingContact, is_valid_MSG, read_message
from collections import Counter
import os

def single_file_nameset(filename):
    """
    input:filename，单个聊天记录文件名
    output:nameset，可能的昵称集合
    从单个txt中获取“我”可能的昵称集合，并且统计每个昵称的频次
    """
    name_dict = {}
    with open(filename, 'r', encoding='utf-8') as f:
        contact = read_chattingContact(f)
        if not contact: return None

        # 读取第一条有效消息,确保正确开始读取聊天
        while True:
            last_msg = read_message(f,contact)
            if is_valid_MSG(last_msg):break
        #开始正式读取
        while True:
            cur_msg = read_message(f,contact)

            #读不到新消息，结束读取
            if cur_msg is None:
                if not (last_msg.role in contact or contact in last_msg.role):
                    name_dict[last_msg.role] = name_dict.get(last_msg.role, 0) + 1
                break
            # 跳过无效消息以及系统消息
            if not is_valid_MSG(cur_msg):continue
            #角色变化，且旧昵称不是备注，统计
            if cur_msg.role != last_msg.role and not (last_msg.role in contact or contact in last_msg.role):
                name_dict[last_msg.role] = name_dict.get(last_msg.role, 0) + 1
            #更新上一条消息
            last_msg = cur_msg
        return name_dict
        
def auto_getMYNAME(directory,preset_NAME=None):
    """
    input:directory，聊天记录文件夹路径；preset_NAME，预设的名称集合，方便调试
    output:nameset，可能的昵称集合
    函数读取txt聊天记录，调用当个读取功能，统计可能的昵称集合，返回
    """
    #如果有预设的名称集合，直接使用返回
    if preset_NAME:
        init_MYNAME(preset_NAME)
        return 
    #没有指定，则通过非聊天记录频次获取可能的昵称供选择
    name_dict = {}
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            filepath = os.path.join(directory, filename)

            new_dict = single_file_nameset(filepath)
            if new_dict:
                name_dict = dict(Counter(name_dict)+Counter(new_dict))
    
    if not name_dict: return None
    #print(nameset)
    return set(name_dict.keys())
    








