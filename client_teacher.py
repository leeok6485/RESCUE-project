import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
import time
from PyQt5.QtCore import *
from socket import *

form_class = uic.loadUiType("교사용.ui")[0]
sock = socket(AF_INET, SOCK_STREAM)
sock.connect(('', 7500))


class Window(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # 버튼 기능
        self.q_upload_btn.clicked.connect(self.move_q_upload_page)
        self.q_upload_btn.setText("문제출제하기")
        self.chat_btn.clicked.connect(self.move_chat_page)
        self.chat_btn.setText("실시간 상담")
        self.qna_btn.clicked.connect(self.move_qna_page)
        self.qna_btn.clicked.connect(self.qna_view)
        self.qna_btn.setText("QnA 게시판")
        self.s_info_btn.clicked.connect(self.move_info_page)
        self.s_info_btn.setText("학생정보열람")
        self.upload_back_btn.clicked.connect(self.move_start_page)
        self.upload_back_btn.setText("뒤로가기")
        self.info_back_btn.clicked.connect(self.move_start_page)
        self.info_back_btn.setText("뒤로가기")
        self.qna_back_btn.clicked.connect(self.move_start_page)
        self.qna_back_btn.setText("뒤로가기")
        self.chat_back_btn.clicked.connect(self.move_start_page)
        self.chat_back_btn.setText("뒤로가기")
        # 문제출제창 설정
        # 리스트위젯을 써서 현재 존재하는 모든 문제를 출력
        # 입력칸을 만들어서 문제를 입력할까?
        self.q_list.resize(900, 450)
        self.q_upload.resize(900, 50)
        self.q_upload.returnPressed.connect(self.append_question)
        self.rcv = Receive()
        self.rcv.chat.connect(self.recv_chat)
        self.rcv.chat2.connect(self.recv_chat2)
        self.rcv.start()


        # 학생정보열람창 설정
        # self.s_info_browser
        # 학생의 이름을 입력 했을 때 DB내의 그 학생의 값을 전부 출력할 부분
        # 학생이름을 그냥 입력 받을곳
        self.s_info_browser.resize(900, 450)
        self.s_info_inputname.resize(900, 50)
        self.s_info_inputname.returnPressed.connect(self.info_check)


        # Q&A창 설정
        self.qna_list.resize(1100, 500)
        self.qna_list.setColumnCount(3)
        header1 = self.qna_list.horizontalHeader()
        header1.resizeSection(0, 80)
        header2 = self.qna_list.horizontalHeader()
        header2.resizeSection(1, 300)
        header3 = self.qna_list.horizontalHeader()
        header3.resizeSection(2, 600)
        self.qna_list.currentCellChanged.connect(self.cellchanged_event)
        # 실시간 상담(체팅기능)
        self.chat_input.returnPressed.connect(self.send_chat)
        self.chat_window.resize(900, 450)
        self.chat_input.resize(900, 50)
        # self.rcv = Receive()
        # self.rcv.chat.connect(self.recv_chat)
        #
        # self.rcv.start()


    def move_start_page(self):
        self.stackedWidget.setCurrentWidget(self.start_page)

    def move_q_upload_page(self):
        self.stackedWidget.setCurrentWidget(self.q_upload_page)

    def move_info_page(self):
        self.stackedWidget.setCurrentWidget(self.s_info_page)

    def move_qna_page(self):
        self.stackedWidget.setCurrentWidget(self.qna_page)

    def move_chat_page(self):
        self.stackedWidget.setCurrentWidget(self.chat_page)

    # 서버에게 특수문자+문제 를 붙여서 메시지 전송하면 서버가 문제출제 저장요청으로 인식
    def append_question(self):
        question = "@문제 "+self.q_upload.text()
        sock.send(question.encode())
        print("문제 보냄 : ", question)
        self.q_upload.clear()


    # 서버에게 특수문자+학생이름 을 붙여서 메시지 전송하면 서버가 학생정보 요청으로 인식
    def info_check(self):
        s_name = "@학생이름 "+self.s_info_inputname.text()
        sock.send(s_name.encode())
        print("학생이름 보냄 :", s_name)
        self.s_info_inputname.clear()

    def qna_view(self):
        rows = []
        student = ""
        question = ""
        answer = ""
        # 전부 갱신받으면서 답변은 따로 입력한 값으로 전송
        # 혹은 기존처럼 그 칸에 직접 변경하고 내가 저장함
        QnA = [student, question, answer]
        for i in range(10):
            rows.append(QnA[:])
        i = 0
        for row in range(len(rows)):
            self.qna_list.setRowCount((i + 1))
            QnA_data = rows[row]
            self.qna_list.setItem(i, 0, QTableWidgetItem(QnA_data[0]))
            self.qna_list.setItem(i, 1, QTableWidgetItem(QnA_data[1]))
            self.qna_list.setItem(i, 2, QTableWidgetItem(QnA_data[2]))
            i += 1

    def cellchanged_event(self, row, col):
        qna_change = self.qna_list.item(row, col)
        print(f"{row}열 {col}행 변경 : ", qna_change)

    # 체팅은 그냥 클라이언트끼리니 서버는 구분없이 그냥 사이 중계만 하면 될 듯
    def send_chat(self):
        msg = self.chat_input.text()
        sock.send(msg.encode())
        self.chat_window.append(msg)
        self.chat_input.clear()

    @pyqtSlot(str)
    def recv_chat(self, msg):
        print("메세지 수신", msg)
        self.chat_window.append(msg)

    @pyqtSlot(str)
    def recv_chat2(self, msg):
        print("메세지 수신", msg)
        self.q_list.addItem(msg)


class Receive(QThread):
    chat = pyqtSignal(str)
    chat2 = pyqtSignal(str)
    print("큐쓰레드 수신")

    def run(self):
        while True:
            msg = sock.recv(1024)
            data = msg.decode()
            print("큐쓰레드 메시지 수신됨 ", data)
            self.chat.emit(f"학생 : {data}")
            self.chat2.emit(data)
        self.sock.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWindow = Window()
    myWindow.show()
    app.exec_()