"""
基于规则的对话策略
"""
import random, re
from copy import deepcopy
import dialog.config as cfg


# TODO: 继承一个抽象基类class "policy "
class CMCCRulePolicy(object):
    def __init__(self, DBoperator, system_act_class):
        self.DBoperator = DBoperator
        self.all_sys_act = cfg.sys_acts
        self.sys_act = system_act_class()
        self.sys_act_class = system_act_class

    def get_system_action(self, state):
        """
        外部调用生成系统动作的接口
        input: 对话状态 (dict type)
        return: 系统动作 （system_act_class的实例）
        """
        self.last_sysact = deepcopy(self.sys_act)
        self.sys_act = self.sys_act_class()
        self.sys_act.personal = state.asking_personal
        self.sys_act.only_parent = state.only_mention_parent

        if state.asking_personal:
            ps_info = self.DBoperator.personal_info
            self.sys_act.act['告知'] = self.inform_personal(state.relations)
            self.sys_act.act['问询更多'] = []
            if '当前主套餐' in state.relations:
                self.sys_act.entity = ps_info['当前主套餐']
                self.sys_act.entity_way = 'personal'
                self.sys_act.act['告知']['基本信息'] = self.inform(self.sys_act.entity,
                                                                        ['费用', '流量', '通话时长'])
        else:
            self._get_system_act(state)

        if self.sys_act.entity:
            inform_attr = self.DBoperator.KGQueryProperty(self.sys_act.entity,
                                    ['费用', '流量', '通话时长'])
            for k,v in inform_attr.items():
                try:
                    self.sys_act.entity_info[k] = int(re.search(r'[\d]+', v).group())
                except:
                    continue

        return self.sys_act


    def inform(self, ent_name, attrs= ['介绍']):
        values = self.DBoperator.KGQueryProperty(ent_name, attrs)
        contents = {}

        for k, v in values.items():
            if k == '介绍':
                ss = ['费用', '流量', '通话时长']
                intro = self.DBoperator.KGQueryProperty(ent_name, ss)
                for s, sv in intro.items():
                    if sv:
                        contents[s] = sv
            if v:
                contents[k] = v
            else:
                # 该实体应该有这个属性，但图谱中缺失了
                should_include = False
                if k == '介绍':
                    ent_type = self.DBoperator.KGQueryType(ent_name)
                    if ent_type in cfg.main_plan_type:
                        contents['介绍'] = "%s是一种主套餐，按月收费，包含一定"\
                                                            "的数据流量和免费通话时长"%ent_type
                    elif ent_type in cfg.data_plan_type:
                        contents['介绍'] = "%s是一种流量包"%ent_type
                    else:
                        contents['介绍'] = None
                    continue
                elif k in cfg.attr_should_in_entities:
                    valid_ent_list = cfg.attr_should_in_entities[k]
                    for ve in valid_ent_list:
                        if ve in ent_name:
                            contents[k] = None
                            should_include = True
                            break
                    if should_include:
                        continue
                elif k == '互斥业务':
                    continue

                # 该实体中本来就不该有此属性
                if not self.sys_act.act.get('找不到属性'):
                    self.sys_act.act['找不到属性'] = [k]
                else:
                    self.sys_act.act['找不到属性'].append(k)

        # 在告知后问用户还有没有其他需要了解的
        self.sys_act.act['问询更多'] = []
        return contents


    def inform_relation_wo_entity(self, relations):
        contents = {}
        for rel in relations:
            ent_num, value = self.DBoperator.KGQueryPropWoSubj(rel)
            if ent_num == 1:
                contents[rel] = value
        return contents


    def inform_personal(self, relations):
        intro_content = {}
        for r in relations:
            intro_content[r] = self.DBoperator.personal_info[r]
        return intro_content


    def parent_intro(self, parent_mention):
        if parent_mention in cfg.main_plan_type:
            intro_str = "%s是一种主套餐，按月收费，包含一定的数据流量和免费通话时长\n"%parent_mention
        else:
            intro_str = "%s是一种流量包\n"%parent_mention
        prices = cfg.entity_price.get(parent_mention)
        if prices:
            intro_str += parent_mention+'分为：'+'/'.join([str(p) for p in prices])
            intro_str += '（元/月）共%d个档位'%len(prices)
        return {'介绍': intro_str}


    def _get_system_act(self, state):
        """
        通过当前对话状态生成系统动作
        input: 对话状态 (CMCCDialogState object for CMCC)
        return: 系统动作 (dict)
        """
        user_act = state.user_act
        ent_mention = state.entity_mention
        ent_tracked = state.entity_tracked
        ent_parent_men = state.parent_mention
        relations = deepcopy(state.relations)
        if '开通方式' in relations:
            relations.append('互斥业务')
        DBres = deepcopy(state.DBres)
        no_info = True
        for  v in state.info_states.values():
            if v:
                no_info = False
                break


        if user_act == '告知' or user_act == '请求推荐':
            if ent_mention:
                self.sys_act.entity = ent_mention
                self.sys_act.entity_way = 'mention'
                self.sys_act.act['告知'] = self.inform(ent_mention)
                # self.sys_act.act['问询更多'] = []
            elif self.sys_act.only_parent:
                self.sys_act.parent_mention = ent_parent_men
                self.sys_act.act['告知'] = self.parent_intro(ent_parent_men)
                self.sys_act.act['问询档位'] = []
            elif len(DBres) == 0:
                if no_info:
                    self.sys_act.act['系统介绍'] = None
                    self.sys_act.act['问询'] = '费用'
                elif user_act == '告知':
                    self.sys_act.act['找不到实体'] = None
                else:
                    recom_list = ['4G飞享套餐38元档', '全球通畅享套餐88元档', '畅享套餐组合套餐58元档']
                    self.sys_act.entity = random.choice(recom_list)
                    self.sys_act.entity_way = 'KG'
                    self.sys_act.act['告知'] = self.inform(self.sys_act.entity)

            elif len(DBres) <= 3:
                self.sys_act.entity = random.choice(DBres)
                self.sys_act.entity_way = 'KG'
                self.sys_act.act['告知'] = self.inform(self.sys_act.entity)
            else:
                for slot in ['费用', '流量', '通话时长']:
                    if not state.info_states.get(slot):
                        self.sys_act.act['问询'] = slot
                        break
                if '问询' not in self.sys_act.act:
                    self.sys_act.entity = random.choice(DBres)
                    self.sys_act.entity_way = 'KG'
                    self.sys_act.act['告知'] = self.inform(self.sys_act.entity)
                    # self.sys_act.act['问询更多'] = []

        elif user_act == '问询':
            if ent_mention:
                self.sys_act.entity = ent_mention
                self.sys_act.entity_way = 'mention'
                if relations:
                    self.sys_act.act['告知'] = self.inform(ent_mention, relations)
                    # self.sys_act.act['问询更多'] = []
                else:
                    self.sys_act.act['确认'] = {'套餐名称': ent_mention, '问询属性': []}
            elif ent_tracked and not state.parent_change:
                self.sys_act.entity = ent_tracked
                self.sys_act.entity_way = 'inherit'
                if relations:
                    self.sys_act.act['告知'] = self.inform(ent_tracked, relations)
                else:
                    self.sys_act.act['告知'] = self.inform(ent_tracked)
                    # self.sys_act.act['确认'] = {'问询属性': []}
            elif self.sys_act.only_parent:
                self.sys_act.parent_mention = ent_parent_men
                self.sys_act.act['告知'] = self.parent_intro(ent_parent_men)
                self.sys_act.act['问询档位'] = []
            elif relations:
                contents = self.inform_relation_wo_entity(relations)
                if not contents:
                    self.sys_act.act['确认'] = {'套餐名称': [], '问询属性': relations}
                else:
                    self.sys_act.act['告知'] = contents
            else:
                self.sys_act.act['确认'] = {}

        elif user_act == '更换':
            if ent_tracked in DBres:
                DBres.remove(ent_tracked)
                if not DBres:
                    self.sys_act.entity = ent_tracked
                    self.sys_act.entity_way = 'inherit'
                    self.sys_act.act['找不到实体'] = '无法更换'
                else:
                    self.sys_act.entity = random.choice(DBres)
                    self.sys_act.entity_way = 'KG'
                    self.sys_act.act['告知'] = self.inform(self.sys_act.entity)
                    # self.sys_act.act['问询更多'] = []
            else:
                self.sys_act.act['确认'] = {}

        elif user_act == '表达肯定':
            if '问询' not in self.last_sysact.act:
                self.sys_act.act['确认'] = {}
            else:
                entity = ent_tracked if not ent_mention else ent_mention
                if entity:
                    self.sys_act.entity = entity
                    self.sys_act.entity_way = 'inherit'
                    self.sys_act.act['告知'] = self.inform(ent_tracked, relations)
                else:
                    self.sys_act.act['确认'] = {'套餐名称': []}

        elif user_act == '表达否定':
            self.sys_act.act['确认'] = {}

        elif user_act == '闲聊':
            self.sys_act.act['闲聊'] = None

        elif user_act == '重启对话':
            self.sys_act.act['重启对话'] = None

        elif user_act == '结束对话':
            self.sys_act.act['结束对话'] = None
        else:
            raise TypeError('未定义的用户意图: '+user_act)