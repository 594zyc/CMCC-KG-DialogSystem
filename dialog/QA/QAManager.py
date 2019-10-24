"""
QA管理
提供获取QA答案的接口
"""
import re
import json
from pprint import pprint

class QAManager(object):
    def __init__(self, QA_save_dir):
        self.QA_save_dir = QA_save_dir
        with open(QA_save_dir, 'r') as f:
            self.QAs = json.load(f)
        self.q_templates = list(self.QAs.keys())
        # self.qt_compiled = {}
        # for qt in self.q_templates:
        #     self.qt_compiled[qt] = re.compile(qt)
        self.next_QA_response = None
        # pprint(self.q_templates)

    def get_next_QA_response(self, user_utter):
        for tmpl in self.q_templates:
            if re.match(tmpl, user_utter):
                self.next_QA_response = self.QAs[tmpl]['answer']
                return self.next_QA_response
            else:
                self.next_QA_response = None
        return self.next_QA_response

    # def restart(self):
    #     self.__init__(QA_save_dir = self.QA_save_dir)

    def close(self):
        pass

if __name__ == '__main__':
    qam = QAManager('./QAs.json')
    # pprint(qam.QAs)
    # pprint(qam.q_templates)
    while True:
        user_utter = input('输入：')
        print(user_utter)
        print(qam.get_next_QA_response(user_utter))
