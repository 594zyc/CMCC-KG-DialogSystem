"""
自然语言生成模块：完成系统动作到自然语言的映射
"""
from .NLG_rules import CMCCRuleNLG


class NLGManager(object):
    def __init__(self, NLG_type = 'rule'):
        self.NLG_type = NLG_type
        if self.NLG_type == 'rule':
            self.nlg = CMCCRuleNLG()
        else:
            raise ValueError('无效的NLG类型')
        self.response = None
        self.greeting = '系统：您好，我是中国移动业务咨询机器人，可以'\
            '帮助您进行套餐推荐或信息查询，请问您需要什么帮助吗？'

    def get_next_response(self, sys_act):
        self.response = self.nlg.sys_act_to_nl(sys_act)
        return self.response

    # def restart(self):
    #     self.__init__(NLG_type = self.NLG_type)

    def close(self):
        pass
