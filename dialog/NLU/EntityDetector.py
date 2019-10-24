"""
命名实体识别：识别知识库中的业务名称
"""
from dialog.NLU.NLUDetectors import NLU
import re
import dialog.config as cfg


class EntityDetector(NLU):
    def __init__(self):
        super().__init__()

    def get_ER_results(self, user_utter):
        """
        找到句中的业务实体，并进行去词汇化处理
        返回 (业务实体结果，处理后句子)
        :param user_utter: 输入语句
        :return: tuple
        """
        self.entity_detected = []
        self.type_detected = []
        user_utter_tmp = user_utter
        for k in self.entity_price:
            for p in self.entity_price[k]:
                if '%s%d元' % (k, p) in user_utter_tmp:
                    user_utter_tmp = user_utter_tmp.replace('%s%d元档' % (k, p), 'subjectname')
                    user_utter_tmp = user_utter_tmp.replace('%s%d元' % (k, p), 'subjectname')
                    self.entity_detected.append('%s%d元档' % (k, p))
        for entity in self.entity_no_price:
            entity_list = [entity] + self.entity_no_price[entity]
            for ent in entity_list:
                # if ent in user_utter and ent not in cfg.entity_type:
                if ent in user_utter and ent not in cfg.entity_type_ambigu:
                    self.entity_detected.append(entity)
                    user_utter = user_utter.replace(ent, 'subjectname')
                # elif ent in user_utter and ent in cfg.entity_type:
                elif ent in user_utter and ent in cfg.entity_type_ambigu:
                    self.type_detected.append(entity)
                    user_utter = user_utter.replace(ent, 'subjectname')
        return (self.entity_detected, self.type_detected, self.wordseg(user_utter))

    def close(self):
        pass

if __name__ == '__main__':
    ED = EntityDetector()
    while True:
        user_utter = input('输入:')
        print(ED.get_ER_results(user_utter))