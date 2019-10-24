"""
策略管理模块：基于当前对话状态生成系统动作
"""
from .policy_rules import CMCCRulePolicy


class SystemAct(object):
    def __init__(self):
        self.act = {}
        self.entity = None
        self.entity_way = None   #[None, 'mention', 'inherit', 'KG', personal']
        self.entity_info = {}
        self.personal = False
        self.parent_mention = None
        self.only_parent = False

    def __str__(self):
        return '----------------- SYSTEM ACTION -------------------\n'+ \
                    ' - system act: '+str(self.act)+ '\n'+\
                    ' - entity tracked: "%s"  source: %s\n'%(str(self.entity), str(self.entity_way))+\
                    ' - entity information: ' + str(self.entity_info)+'\n'+\
                    ' - parent mentioned: ' + str(self.parent_mention) + '\n'+\
                    ' - personal query: ' + str(self.personal) + '\n'+\
                    ' - only parent nodes mentioned: ' + str(self.only_parent)


class PolicyManager(object):
    def __init__(self, policy_type, DBoperator):
        self.policy_type = policy_type
        if self.policy_type == 'rule':
            self.policy = CMCCRulePolicy(DBoperator, SystemAct)
        else:
            raise ValueError('无效的策略类型')

    def get_next_action(self, state):
        self.next_sys_act = self.policy.get_system_action(state)
        return self.next_sys_act

    def close(self):
        return

