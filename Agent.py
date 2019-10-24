# -*- coding: utf-8 -*-
"""
结合各模块 Manager,实现text-in text-out的交互式 agent 接口
"""
import os
import time
import argparse
from dialog.DialogManager import DialogManager
from dialog.NLU.NLUManager import NLUManager
from dialog.NLG.NLGManager import NLGManager
from dialog.QA.QAManager import QAManager
from utils.logger import create_logger

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--print', type=int, default=1, help='print details')
FLAGS= parser.parse_args()
FLAGS.print = FLAGS.print==1

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

SAVE_DIRS = {
    'useract': os.path.join(ROOT_DIR, 'train/ActDetector_BOW'),
    'relation': os.path.join(ROOT_DIR, 'train/AttrDetector_BOW'),
    'object': os.path.join(ROOT_DIR, 'train/ValueDetector_EDST'),
    'QA': os.path.join(ROOT_DIR, 'dialog/QA/QAs.json'),
    'KG': os.path.join(ROOT_DIR, 'dialog/DB/ontology/mobile-ontology-5.2.ttl'),
}

class CMCCDialogAgent(object):
    def __init__(self):
        self.record_savedir = None
        self.log_savedir = None
        self.logger = None
        self.user = self.create_user(user_exist = True)
        self.nlu_manager = NLUManager(SAVE_DIRS)
        self.QA_manager = QAManager(SAVE_DIRS['QA'])
        self.dialog_manager = DialogManager(SAVE_DIRS['KG'],
                                                                       policy_type = 'rule',
                                                                       logger = self.logger,
                                                                       print_details = FLAGS.print)
        self.nlg_manager = NLGManager(NLG_type = 'rule')
        self.turns = 1
        self.greeting = self.nlg_manager.greeting
        self.recordings = [self.greeting]


    def create_user(self, user_exist = False):
        user_name = 'test' if user_exist else input("请输入您的用户名：")
        user_path = os.path.join(ROOT_DIR, 'logs', user_name)
        log_path = os.path.join(user_path, 'log')
        if not os.path.exists(user_path):
            os.mkdir(user_path)
            os.mkdir(log_path)
        self.record_savedir = os.path.join(ROOT_DIR, user_path, 'dialogs.txt')
        log_name = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
        self.log_savedir = log_path +'/' + log_name + '.log'
        self.logger = create_logger(self.log_savedir, FLAGS.print)
        return user_name


    def interact_one_turn(self):
        user_utter = input("用户输入：")
        while not user_utter:
            user_utter = input("用户输入：")
        if not FLAGS.print: print('')
        with open(self.log_savedir, 'a', encoding='gbk') as f:
            f.write('-------------- Turn ' + str(self.turns) + '--------------\n')
            f.write('用户：' + user_utter + '\n')
        self.recordings.append('用户：' + user_utter)
        qa_response = self.QA_manager.get_next_QA_response(user_utter)
        if False:
            self.logger.info('***匹配到QA标准问题，使用QA回答***\n')
            response = qa_response
        else:
            last_sysact = self.dialog_manager.get_system_act()
            nlu_results = self.nlu_manager.get_NLU_results(user_utter, last_sysact)
            system_act = self.dialog_manager.dialog_manage(nlu_results)
            if FLAGS.print: self.logger.info(str(system_act)+'\n')
            if self.dialog_manager.dialog_restart:
                return
            response = self.nlg_manager.get_next_response(system_act)
        if response:
            self.logger.info('系统:' + response + '\n')
            self.recordings.append('系统：' + response)
        else:
            self.logger.info('系统: 感谢您的使用，再见！\n')
            self.recordings.append('系统: 感谢您的使用，再见！')

    def start_dialog(self):
        self.logger.info('对话记录时间：'+time.strftime("%Y-%m-%d %H:%M:%S",
                                 time.localtime()))
        self.logger.info('用户：%s'%self.user)
        try:
            self.logger.info(self.greeting)
            while True:
                self.interact_one_turn()
                if self.dialog_manager.dialog_restart:
                    self.record_dialog()
                    self.restart()
                if self.dialog_manager.dialog_end:
                    confirm_end = self.finish_dialog()
                    if confirm_end != '是':
                        break
                    else:
                        self.dialog_manager.dialog_end = False
                        self.restart()
                self.turns += 1
            return False

        except KeyboardInterrupt:
            self.finish_dialog()


    def finish_dialog(self):
        self.logger.info('对话结束，记录对话信息')
        self.logger.info('对话轮数：%s'%self.turns)
        self.record_dialog()
        self.logger.info('是否重新开始对话？')
        user_utter = input("请输入[是/否]：")
        while user_utter not in ['是', '否']:
            user_utter = input("请输入[是/否]：")
        return user_utter


    def record_dialog(self):
        with open(self.record_savedir, 'a') as f:
            f.write('对话记录时间：')
            f.write(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+'\n')
            f.write('用户：%s\n'%self.user)
            f.write('对话轮数：%s\n\n'%self.turns)
            for dialog in self.recordings:
                dialog = '\n'.join(dialog.split())
                f.write(dialog+'\n\n')
            f.write('————————————————————————————————\n')
        self.logger.info('对话记录成功')
        self.recordings = []


    def restart(self):
        self.turns = 0
        self.dialog_manager.restart()
        self.logger.info('\n系统：系统已重启，请重新开始对话')
        self.logger.info(self.greeting)


    def close(self):
        self.nlu_manager.close()
        self.dialog_manager.close()
        self.nlg_manager.close()


if __name__ == '__main__':
    agent = CMCCDialogAgent()
    agent.start_dialog()

    # 崩溃保护
    # flag = True
    # while flag:
    #     try:
    #         flag = agent.start_dialog()
    #     except:
    #         agent.dialog_manager.restart()
    #         agent.turns = 0

















