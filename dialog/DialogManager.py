"""
对话管理模块：完成多轮信息的整合，对话状态更新，生成系统动作
"""
from .DB.DBoperator import DBOperator
from .DST.DialogStateTracker import DialogStateTracker, DialogState
from .policy.PolicyManager import PolicyManager, SystemAct


class DialogManager(object):
    def __init__(self, db_savedir, policy_type = 'rule', logger = None,
                       print_details = True):
        self.db_savedir = db_savedir
        self.DBoperator = DBOperator(db_savedir)
        self.dialog_state = DialogState()
        self.DST = DialogStateTracker(self.DBoperator)
        self.policy_type = policy_type
        self.PolicyManager = PolicyManager(policy_type, self.DBoperator)
        self.system_act = SystemAct()
        self.print_details = print_details
        self.logger = logger
        self.printf = logger.info if logger else print
        self.dialog_restart = False
        self.dialog_end = False

    def dialog_manage(self, NLU_results):
        """
        输入NLU识别结果，更新对话状态，生成本轮系统动作
        :param NLU_results: dict
        """

        # 对话状态更新
        pv_sysact = self.system_act
        self.dialog_state = self.DST.state_update(NLU_results, pv_sysact)
        # if self.print_details: self.printf(self.DST.log)

        # 生成系统动作并更新对话状态
        self.system_act = self.PolicyManager.get_next_action(self.DST.state)
        self.dialog_state.entity_tracked = self.system_act.entity

        # 打印对话状态
        if self.print_details: self.printf(self.dialog_state)

        # 找不到实体时，清空informed slots状态
        if '找不到实体' in self.system_act.act:
            self.dialog_state.info_states = {'费用': None, '流量': None, '通话时长': None}
            if self.print_details: self.printf('\ninform state已重置\n')

        if '重启对话' in self.system_act.act:
            self.dialog_restart = True

        if '结束对话' in self.system_act.act:
            self.dialog_end = True

        return self.system_act

    def get_system_act(self):
        return self.system_act

    def restart(self):
        self.__init__(self.db_savedir,
                           policy_type = self.policy_type,
                           logger = self.logger,
                           print_details = self.print_details)

    def close(self):
        self.DST.close()
        self.PolicyManager.close()

