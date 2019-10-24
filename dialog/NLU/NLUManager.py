"""
自然语言理解模块：基于当前用户输入和上一轮系统动作识别新信息
包括用户动作、提及实体、实体关系、属性取值限制的识别
"""
import re, pprint
import dialog.config as cfg
from .UserActDetector import UserActDetector
from .EntityDetector import EntityDetector as SubjectDetector
from .SlotValueDetector import ValueDetector as ObjectDetector
from .SlotValueDetector import AttrDetector as RelationDetector
from .infoattr_template import Match_Cost_Time_Data

infoattr_value2num = cfg.infoattr_value2num
scope = cfg.scope
req_more_less = cfg.req_more_less

class NLUManager(object):
    def __init__(self, save_dirs):
        self.entity_price = cfg.entity_price
        self.SubjectDetector = SubjectDetector()
        self.UserActDetector = UserActDetector(save_dirs['useract'])
        self.ObjectDetector = ObjectDetector(save_dirs['object'])
        self.RelationDetector = RelationDetector(save_dirs['relation'])
        self.result = {}

    def match_relations(self, sent):
        request_attrs = cfg.requestable_attrs.copy()
        request_attrs.remove('流量')
        request_attrs.remove('费用')
        request_attrs.remove('通话时长')
        for r in cfg.matching_attrs+request_attrs:
            if r in sent:
                self.result['relations'][r] = 1.0
                self.result['user_act'] = ('问询', 1.0)

    def get_objects(self, object_str, object_num, last_sysact):
        obj_sys_asked = last_sysact.act.get('问询', None)
        tacked_obj_info = last_sysact.entity_info
        #优先匹配数值型value
        #匹配出单一数值对应的扩充范围
        output = {'流量': {'interval':[], 'confidence': 0},
                  '费用': {'interval':[], 'confidence': 0},
                  '通话时长': {'interval':[], 'confidence': 0}}
        if object_num:
            for k in object_num:
                output[k]['confidence'] = 1.0
                if object_num[k][0] == object_num[k][1]:
                    output[k]['interval'].append(max(0, object_num[k][0]-scope[k]))
                    output[k]['interval'].append(object_num[k][0]+scope[k])
                else:
                    output[k]['interval'].extend(object_num[k])
        elif object_str and not obj_sys_asked:
            # 用户一轮就说出了 属性 和 值
            for k in ['费用','流量','通话时长']:
                if k in self.result['relations'].keys():
                    if object_str[0] in ['少', '中', '多', '任意']:
                        output[k]['interval'] = infoattr_value2num[k][object_str[0]]
                        output[k]['confidence'] = object_str[1]
                    elif object_str[0] == '更多': # 更多  更少
                        if tacked_obj_info.get(k, None): # 查找上一轮套餐的属性值
                            output[k]['interval'].append(tacked_obj_info.get(k, None) + 1)
                            output[k]['interval'].append(tacked_obj_info.get(k, None) + req_more_less[k])
                            output[k]['confidence'] = object_str[1]
                        else:
                            output[k]['interval'] = infoattr_value2num[k]['多']
                            output[k]['confidence'] = object_str[1]
                    elif object_str[0] == '更少': # 更多  更少
                        if tacked_obj_info.get(k, None): # 查找上一轮套餐的属性值
                            output[k]['interval'].append(max(tacked_obj_info.get(k, None)
                                                             - req_more_less[k], 0))
                            output[k]['interval'].append(max(tacked_obj_info.get(k, None) - 1,0))
                            output[k]['confidence'] = object_str[1]
                        else:
                            output[k]['interval'] = infoattr_value2num[k]['少']
                            output[k]['confidence'] = object_str[1]
        elif object_str and obj_sys_asked:
            k = obj_sys_asked
            if object_str[0] in ['少', '中', '多', '任意']:
                output[k]['interval'] = infoattr_value2num[k][object_str[0]]
                output[k]['confidence'] = object_str[1]
            elif object_str[0] == '更多':  # 更多  更少
                if tacked_obj_info.get(k, None):  # 查找上一轮套餐的属性值
                    output[k]['interval'].append(tacked_obj_info.get(k, None) + 1)
                    output[k]['interval'].append(tacked_obj_info.get(k, None) + req_more_less[k])
                    output[k]['confidence'] = object_str[1]
                else:
                    output[k]['interval'] = infoattr_value2num[k]['多']
                    output[k]['confidence'] = object_str[1]
            elif object_str[0] == '更少':  # 更多  更少
                if tacked_obj_info.get(k, None):  # 查找上一轮套餐的属性值
                    output[k]['interval'].append(max(tacked_obj_info.get(k, None)
                                                     - req_more_less[k], 0))
                    output[k]['interval'].append(max(tacked_obj_info.get(k, None) - 1, 0))
                    output[k]['confidence'] = object_str[1]
                else:
                    output[k]['interval'] = infoattr_value2num[k]['少']
                    output[k]['confidence'] = object_str[1]
        return output



    def get_NLU_results(self, user_utter, last_sysact):
        self.result = {}
        ent_list, type_list, _user_utter = \
            self.SubjectDetector.get_ER_results(user_utter)
        self.result['user_utter'] = _user_utter
        self.result['parent_mention'] = type_list
        self.result['entity_mentioned'] = ent_list

        # TODO: 添加直接识别用户动作的规则
        self.result['user_act'] = self.UserActDetector.get_user_act_results(user_utter)
        if re.search('finish|再见|结束|拜拜|谢谢', user_utter) or \
            (user_utter in ['不了','不用了', '没了','够了','不'] and '问询更多' in last_sysact.act):
            self.result['user_act'] =  ('结束对话', 1.0)
        if re.search('restart|重新开始|重[启置](对话)?', user_utter):
            self.result['user_act'] = ('重启对话', 1.0)

        # 匹配属性
        self.result['relations'] = self.RelationDetector.get_attr_results(user_utter)
        # print('NLU relations:', self.result['relations'])
        # 匹配实体业务 和 具体的档位
        object_str = self.ObjectDetector.get_value_results(user_utter)
        # print('NLU object_str:', object_str)
        infoattr_num_results = Match_Cost_Time_Data(user_utter)
        if len(infoattr_num_results) > 0:
            object_num = infoattr_num_results
            self.result['user_act'] = ('告知', 1.0)
            # 如果用户直接或间接提到某个套餐某个档，匹配出entity
            if '费用' in object_num and object_num['费用'][0]\
                    == object_num['费用'][1]:
                price = object_num['费用'][0]
                for ent in self.result['parent_mention']:
                    if ent in self.entity_price and price in self.entity_price[ent]:
                        self.result['entity_mentioned'].append('%s%d元档'%(ent, price))

                if not ent_list:
                    ent = last_sysact.parent_mention
                    if ent and ent in self.entity_price and price in self.entity_price[ent]:
                        self.result['entity_mentioned'].append('%s%d元档' % (ent, price))
                    self.result['parent_mention'] = [last_sysact.parent_mention]
        else:
            object_num = None
        self.result['object'] = self.get_objects(object_str, object_num, last_sysact)

        # 某些直接规则匹配的属性
        self.match_relations(user_utter)
        # pprint.pprint(self.result, width=300)
        return self.result

    def close(self):
        self.SubjectDetector.close()
        self.UserActDetector.close()
        self.ObjectDetector.close()
        self.RelationDetector.close()

if __name__ == '__main__':
    save_dirs = {
        'useract': './train/ActDetector_BOW',
        'relation': './train/AttrDetector_BOW',
        'object': './train/ValueDetector_EDST'
    }
    print('prepare nlu models ... ')
    nlu = NLUManager(save_dirs)
    import pprint
    last_sysact = {'流量':200, '费用':20, '通话时长':100, '主业务类': ['畅享套餐']}
    while True:
        s = input('输入：')
        pprint.pprint(nlu.get_NLU_results(s, last_sysact))