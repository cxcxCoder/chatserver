import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit, QLabel, QFileDialog, QListWidget, QMessageBox, QHBoxLayout, QCheckBox,QListWidgetItem
from PyQt5.QtCore import Qt

from gettingNameset import auto_getMYNAME
from handlingRecords import handle_dirRecords
from global_func_and_v import init_MYNAME

# 主界面
class FileConverterApp(QWidget):
    def __init__(self):
        """
        UI界面初始化，设置初始化的字体、框体等，并且把UI事件与函数进行连接
        """
        super().__init__()

        self.setFixedSize(1000, 800)
        self.setWindowTitle("文件转换器")
        self.setStyleSheet("""
            QWidget {
                font-family: '微软雅黑';
                font-size: 18px;
            }
            QListWidget {
                background: #fff;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            QPushButton {
                min-height: 30px;
                padding: 5px 15px;
            }
        """)

        # 初始化UI
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(20, 20, 20, 20)  # 设置外围边距

        # 选择目录部分
        self.dir_line_edit = QLineEdit(self)
        self.dir_line_edit.setPlaceholderText("选择一个目录")
        self.dir_line_edit.setFixedHeight(40)  # 固定高度
        self.layout.addWidget(self.dir_line_edit)

        self.select_dir_button = QPushButton("选择目录", self)
        self.select_dir_button.clicked.connect(self.select_directory)
        self.layout.addWidget(self.select_dir_button)

        # 昵称展示部分
        self.names_list_widget = QListWidget(self)
        self.layout.addWidget(self.names_list_widget)

        #复选框
        self.train_self_check = QCheckBox("训练自己", self)
        self.train_self_check.setChecked(True)  # 默认勾选
        self.layout.addWidget(self.train_self_check)

        # 确认按钮
        self.convert_button = QPushButton("确认开始转换", self)
        self.convert_button.clicked.connect(self.start_conversion)
        self.layout.addWidget(self.convert_button)

        # 结果展示标签
        self.result_label = QLabel("", self)
        self.layout.addWidget(self.result_label)

        # 目录路径和昵称集合初始化
        self.directory = ""
        self.nameset = set()

        # 设置布局
        self.setLayout(self.layout)

    def select_directory(self):
        """
        选择目录并获取昵称集合：用户点击选择目录来选择存储聊天记录的文件，并且自动从文件识别可能的昵称，触发展示
        """
        folder_path = QFileDialog.getExistingDirectory(self, "选择目录")
        print(folder_path)
        if folder_path:
            self.dir_line_edit.setText(folder_path)
            self.directory = folder_path

            self.nameset = auto_getMYNAME(folder_path)  # 获取新目录下的昵称集合

            print(f'-----------------------\ncandidate nameset:\n{self.nameset}\n--------------------------')

            self.update_names_list()    #触发列表展示

    def update_names_list(self):
        """
        昵称列表展示，负责展示根据文件夹内对应文件得到的候选昵称，然后用户自行筛选昵称进行删除
        如果没有识别到正确数据，则显示提示信息
        """
        self.names_list_widget.clear()  #重新触发时清理原列表

        if self.nameset:
            # 设置列表的间距和边距
            self.names_list_widget.setSpacing(5)  # 项间距
            self.names_list_widget.setStyleSheet("""
                QListWidget::item { 
                    border-bottom: 1px solid #eee;
                }
                QListWidget::item:hover {
                    background-color: #f5f5f5;  /* 新增悬停背景色 */
                }
            """)
            
            for name in sorted(self.nameset):  # 按字母排序更美观
                # 创建自定义项控件
                item_widget = QWidget()
                item_layout = QHBoxLayout(item_widget)
                item_layout.setContentsMargins(10, 5, 10, 5)  # 减少边距
                
                # 昵称标签（左侧）
                name_label = QLabel(name)
                name_label.setStyleSheet("""
                    QLabel {
                        color: #333;
                        font-size: 22px;
                        font-weight:1000;
                        qproperty-alignment: AlignCenter;
                        min-width: 120px;
                    }
                """)
                
                # 删除按钮（右侧）
                del_btn = QPushButton("X")
                del_btn.setFocusPolicy(Qt.NoFocus)
                del_btn.setToolTip("删除昵称")
                del_btn.setStyleSheet("""
                    QPushButton {
                        background: #ff4444;
                        color: white;
                        border-radius: 15px;
                        min-width: 30px;
                        max-width: 30px;
                        min-height: 30px;
                        max-height: 30px;
                        font-size: 20px;
                    }
                    QPushButton:hover {
                        background: #ff6666;
                    }
                """)
                del_btn.clicked.connect(lambda _, n=name: self.remove_name(n))  #绑定删除按钮的删除事件
                
                # 布局管理
                item_layout.addStretch()  # 左边弹性空间
                item_layout.addWidget(name_label)
                item_layout.addStretch()  # 添加弹性空间
                item_layout.addWidget(del_btn)
                
                # 创建列表项
                list_item = QListWidgetItem()
                list_item.setSizeHint(item_widget.sizeHint())  # 关键：设置尺寸提示
                self.names_list_widget.addItem(list_item)
                self.names_list_widget.setItemWidget(list_item, item_widget)
        else:
            warning_label = QLabel("未识别到正确数据，请检查文件\文件夹或重新选择文件夹")
            warning_label.setStyleSheet("""
                QLabel {
                    color: red;
                    padding: 10px;
                    font-size: 22px;
                    font-weight:1000;
                    qproperty-alignment: AlignCenter;
                    min-width: 120px;
                }
            """)

            warning_item_widget = QWidget()
            layout = QHBoxLayout(warning_item_widget)
            layout.setContentsMargins(0, 10, 0, 10)
            layout.addWidget(warning_label)

            list_item = QListWidgetItem()
            list_item.setSizeHint(warning_item_widget.sizeHint())
            self.names_list_widget.addItem(list_item)
            self.names_list_widget.setItemWidget(list_item, warning_item_widget)


    def remove_name(self, name):
        """删除选中的昵称"""
        if name in self.nameset:
            self.nameset.remove(name)
            self.update_names_list()  # 更新显示列表

    def start_conversion(self):
        """开始转化过程"""
        if not self.directory:
            self.show_error_message("请选择一个目录")
            return

        if not self.nameset:
            self.show_error_message("请至少提供一个昵称进行转换")
            return
        
        init_MYNAME(self.nameset)   #转化前确定最后的nameset
        robot_me = self.train_self_check.isChecked()  # 确定是否训练自己

        print(f'*****************{self.nameset}\nrobot_me:{robot_me}*****************')
        # 调用处理函数
        #文件名转化

        output_name = f'{os.path.basename(self.directory)}.jsonl'
        ouput_filepath = os.path.join(self.directory,output_name)

        handle_dirRecords(self.directory,ouput_filepath,robot_me)

        # 展示转化完成的消息
        self.result_label.setText(f"转化完成，文件保存到 {ouput_filepath}")

    def show_error_message(self, message):
        """显示错误消息框"""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("错误")
        msg.setText(message)
        msg.exec_()

#pyinstaller --onefile --windowed main_ui.py
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileConverterApp()
    window.show()
    sys.exit(app.exec_())