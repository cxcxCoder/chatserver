from collections import namedtuple
import re
from datetime import datetime

#MYNAME集合来存储自己的QQ名称，方便识别对话双方
MYNAME = {}
#保存信息记录
Msg = namedtuple('Message', ['time', 'role', 'message'])

def init_MYNAME(nameset):
    """
    input: set, 自己的QQ名称集合
    外部接口，用于修改全局的MYNAME集合
    """
    global MYNAME
    MYNAME = nameset

def read_chattingContact(file):
    """
    input: file object
    output: str, 联系人名称
    读取聊天记录头，获取联系人名称返回并跳到正式聊天记录前
    """
    count = 0
    contact =  None
    while count<=10:
        count += 1
        line = file.readline().strip()
        if line.startswith("消息对象:"):
            contact = line.split(":")[1].strip()

        if check_nextline(file):break   #读到开始有消息
    return contact


def is_valid_MSG(msg:Msg):
    """
    input: Msg, 聊天记录信息
    output: bool, 是否有效的聊天记录
    分别检查角色名和消息内容，避免无效的系统消息、撤回消息、纯图片等
    """
    #role check
    valid_name = bool(msg.role)

    #message check
    invalid_set = set(["[自动回复]",
                      "对方已成功接收了你发送的离线文件",
                      "撤回了一条消息",
                      "给你发送了一个窗口抖动。",
                      "[戳一戳]"
                      ])
    valid_message =  not any(word in msg.message for word in invalid_set) and bool(re.sub(r'[，;,；]', '', msg.message).strip())

    return valid_message and valid_name

def extract_datetime_and_name(input_str):
    """
    input: str, 单条聊天头
    output: datetime, str, 聊天记录时间和名称
    提取单条聊天的时间和讲话人名称分下面情况：
    1.正确提取时间和名字
    2.系统的撤回、接收文件等消息，只有时间没有名字，返回时间和空名字
    3.读到最后一行了，返回两个none，说明文件结束了
    """
    # 正则表达式匹配时间和名字
    pattern = r"(\d{4}-\d{2}-\d{2} \d{1,2}:\d{2}:\d{2})\s*(.*)"
    match = re.match(pattern, input_str, flags=re.UNICODE)
    
    if match:
        # 提取时间和名字
        time_str = match.group(1)
        name = match.group(2).strip()  # 如果名字为空则返回空字符串
        # 将时间字符串转换为 datetime 对象
        try:
            time_obj = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            #print(f"时间格式错误: {time_str}")
            return None, None
        
        return time_obj, name
    else:
        #print("无法匹配输入格式，文件可能结束...")
        return None, None

def check_nextline(file):
    """
    input: file object,文件对象
    output: bool, 是否是新的开始
    向下一行内容试探，用于判断下一行是否以聊天记录头开始，是就说明到新的聊天记录返回真，否则返回假
    """
    current_pos = file.tell()
    next_line = file.readline().strip()

    nl_pos = file.tell()
    if nl_pos == current_pos:return True    #如果是文件末尾也需要返回真，表明这一段结束了

    file.seek(current_pos)
    if re.match(r"\d{4}-\d{2}-\d{2} \d{1,2}:\d{2}:\d{2}", next_line):
        return True
    return False

def read_message(file,contact):
    """
    input: file object,文件对象; contact,联系人名称
    output: Msg, 聊天记录信息，记录时间、角色、消息内容
    读取当天聊天记录，返回Msg对象
    """
    #读取时间和角色名称
    time_obj, name = extract_datetime_and_name(file.readline().strip())
    if time_obj is None and name is None: return None   #文件终止

    #读取消息内容
    message = ""
    #合并多行消息
    while True:
        line = file.readline().strip()
        if check_nextline(file):break  # 如果下一行是新的开始，结束读取
        if line:
            message += line + ";"

    name = name if name not in MYNAME else '我' #不在MYNAMES集合的为对方，否则为自己
    #print(f"[{name}] {message}")
    return Msg(time_obj, name, re.sub(r"\[图片\]|\[表情\]", ",", message.strip()))
