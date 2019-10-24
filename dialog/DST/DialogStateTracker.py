"""
对话状态跟踪模块：基于NLU识别结果更新对话状态
"""
import dialog.config as cfg
from dialog.NLU.NLUManager import NLUManager
import copy

class DialogState:
    def __init__(self):
        self.turn_num = 0
        self.user_info = None
        self.info_states = {'费用': None, '流量': None, '通话时长': None}
        self.user_act = None
        self.relations = []
        self.entity_mention = None
        self.entity_tracked = None
        self.parent_mention = None
        self.utter = None
        self.DBres = None

        # 状态指示量
        self.asking_personal = False
        self.entity_change = False
        self.parent_change = False
        self.only_mention_parent = False
        self.infostate_change = False

    def __str__(self):
        return '----------------- DIALOGUE STATE -----------------\n'+ \
                ' - info states: '+str(self.info_states)+ '\n'+\
                ' - user act: '+ str(self.user_act) + '\n'+\
                ' - relations: ' + str(self.relations) +'\n'+\
                ' - entity mentioned: ' + str(self.entity_mention)+'\n'+\
                ' - parent nodes mentioned: ' + str(self.parent_mention)+'\n'+\
                ' - KG search results: ' + str(self.DBres)

class DialogStateTracker(object):
    """
    DialogStateTracker为对话状态跟踪器
    根据当前轮的NLU识别结果、上一轮对话状态、上一轮系统动作更新对话状态。
    这里 state 的作用只是对告知属性做个累积
    """
    def __init__(self, DBoperator):
        self.state = DialogState() # 应为DialogState object
        self.DBoperator = DBoperator
        self.log = ''
        self.scenarios_switch_thresh = 0.7 #场景切换的置信阈值
        self.useract_switch_thresh = 0.6

    def state_update(self, NLU_results, last_sysact):
        """
        更新对话状态的主方法
        调用对话状态各个属性的更新函数，完成整个对话状态的更新
        """
        self.prev_state = copy.deepcopy(self.state)  # 复制上一轮的dialog state到prev_turn
        self.state.turn_num += 1
        self.log = "\n--------------- DST CORRECTIONS -----------------\n" # 用于记录基于规则的特殊状态更新
        self.state.utter = NLU_results['user_utter']

        # 优先更新识别准确率较高的user_intent
        self._user_act_update(NLU_results, self.useract_switch_thresh)

        # 更新entity mentioned
        self._mentioned_entity_update(NLU_results, last_sysact)
        # 更新parent mentioned
        self._mentioned_parent_update(NLU_results)


        # 确定是否在说个人场景
        self.state.asking_personal = False
        if self.state.user_act == '问询' and NLU_results['relations']:
            flag = True
            for r in NLU_results['relations'].keys():
                if r not in cfg.requestable_attrs_ps:
                    flag = False
            if flag:
                self.state.asking_personal = True

        # 更新requested 属性
        self._relation_update(NLU_results, last_sysact)

        # 更新informed_slot
        self._info_state_update(NLU_results)

        # KG查询
        self.state.DBres = self.DBoperator.KGQueryByConstraints(
            self.state.info_states)

        if self.log == "\n--------------- DST CORRECTIONS -----------------\n":
            self.log += "无"

        return self.state

    def _user_act_update(self, NLU_results, switch_thresh=0.6):
        if NLU_results['user_act'][1] > switch_thresh:
            self.state.user_act = NLU_results['user_act'][0]
        else:
            if NLU_results['relations']: # 用 attr识别的结果纠正
                self.state.user_act = '问询'
            else:
                self.state.user_act = '告知' # 剩下的就是告知

    def _relation_update(self, NLU_results, last_sysact, threshold=0.6):
        self.state.relations.clear()
        if self.state.user_act != '表达否定' and '确认' in last_sysact.act and \
            last_sysact.act['确认'].get('问询属性'):
            for r in last_sysact.act['确认'].get('问询属性'):
                self.state.relations.append(r)
        elif self.state.user_act == '问询':
            if self.state.asking_personal:
                for r, p in NLU_results['relations'].items():
                    if r in cfg.requestable_attrs_ps and p > threshold:
                        self.state.relations.append(r)
            else:
                for r, p in NLU_results['relations'].items():
                    if r not in cfg.requestable_attrs_ps and p > threshold:
                        self.state.relations.append(r)
        elif not NLU_results['relations'] and self.state.entity_change:
            # 用户上一轮问询了A套餐的属性，本轮直接问：“那B套餐呢？”
            for r in self.prev_state.relations:
                self.state.relations.append(r)
            self.state.user_act = '问询'

    def _info_state_update(self, NLU_results, threshold=0.5):
        if self.state.user_act == '告知':
            for k, info in NLU_results['object'].items():
                if info['interval'] and info['confidence'] > threshold:
                    self.state.info_states[k] = info['interval']
                    self.state.infostate_change = True


    def _mentioned_entity_update(self, NLU_results, last_sysact):
        # 确定实体是否改变, 即提到了新套餐
        self.state.entity_change = False
        self.state.entity_mention = None
        if NLU_results['entity_mentioned'] and \
                NLU_results['entity_mentioned'][0] != self.state.entity_tracked:
            self.state.entity_change = True
            # 只考虑提到一个实体的情况
            self.state.entity_mention = NLU_results['entity_mentioned'][0]
        elif '确认' in last_sysact.act and \
            last_sysact.act['确认'].get('套餐名称', None) \
                and self.state.user_act != '表达否定':
            self.state.entity_mention = last_sysact.act['确认']['套餐名称']
            if self.state.entity_mention != self.state.entity_tracked:
                self.state.entity_change = True

    def _mentioned_parent_update(self, NLU_results):
        # 确定实体是否改变, 即提到了新套餐
        self.state.only_mention_parent = False
        if NLU_results['parent_mention']:
            if NLU_results['parent_mention'][0] != self.state.parent_mention:
                self.state.parent_change = True
                self.state.parent_mention = NLU_results['parent_mention'][0]
        else:
            self.state.parent_change = False
        if self.state.parent_mention and not self.state.entity_mention:
            self.state.only_mention_parent = True

    def close(self):
        pass

if __name__ == '__main__':
    import pprint
    relative_path = 'D:\CMCC\\'
    save_dirs = {
        'useract': relative_path+'CMCC-Dialog-kg/train/ActDetector_BOW',
        'relation': relative_path+'CMCC-Dialog-kg/train/AttrDetector_BOW',
        'object': relative_path+'CMCC-Dialog-kg/train/ValueDetector_EDST'
    }
    nlu = NLUManager(save_dirs)
    dst = DialogStateTracker()
    # TODO: 这里last_sysact的 '流量''费用' '通话时长'，每次出现了 entity
    # TODO 无论是个人还是查找的还是提及的，都需要更新
    # last_sysact = {'流量': 200, '费用': 20, '通话时长': 100, '确认':{}}
    # last_sysact = {'确认': {}, '问询': ["流量"]}
    # last_sysact = {'确认': {'套餐名称': "畅享套餐38元档",
    #                       "问询属性": ["开通方式"]}}
    last_sysact = {'流量': 200, '费用': 20, '通话时长': 100, '主业务类': ['畅享套餐']}
    # last_sysact = {}
    while True:
        s = input('用户:')
        nlu_results = nlu.get_NLU_results(s, last_sysact)
        pprint.pprint(nlu_results)
        print(dst.state_update(nlu_results, last_sysact))
