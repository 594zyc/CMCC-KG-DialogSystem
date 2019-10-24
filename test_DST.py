import os
import sys,pprint
from dialog.DST.DialogStateTracker import DialogStateTracker
from dialog.NLU.NLUManager import NLUManager
save_dirs = {
        'useract': 'D:/workspace/project/dialogue/CMCC_dialogue/DialogSystem_svn/CMCC-Dialog-kg/train/ActDetector_BOW',
        'relation': 'D:/workspace/project/dialogue/CMCC_dialogue/DialogSystem_svn/CMCC-Dialog-kg/train/AttrDetector_BOW',
        'object': 'D:/workspace/project/dialogue/CMCC_dialogue/DialogSystem_svn/CMCC-Dialog-kg/train/ValueDetector_EDST'
    }

nlu = NLUManager(save_dirs)
dst = DialogStateTracker()
last_sysact = {'流量': 200, '费用': 20, '通话时长': 100, '主业务类': ['畅享套餐']}

while True:
    s = input('用户:')
    nlu_results = nlu.get_NLU_results(s, last_sysact)
    pprint.pprint(nlu_results)
    print(dst.state_update(nlu_results, last_sysact))


# init_state =dst.DialogState.CMCCDialogState()
# DBO = db.DBoperator.DBOperator('../dialog/DB/ontology/CMCC_DB.db')
# dst = dst.DialogStateTracker.CMCCDialogStateTracker(init_state, DBO)
# NLU_results = {
# 'scenarios': ('套餐', 0.67),
# 'user_intent': ('问询',  0.99),
# 'informed_slots': {"功能费": (500, 700)},
# 'requested_slots': ['套餐内容', '产品介绍'],
# 'entity_mentioned': ['188元畅享套餐'],
# 'sentiment':None,
# 'user_utter': '畅享套餐，188元那个，介绍一下'
# }
# NLU_results2 = {
# 'scenarios': ('套餐', 0.17),
# 'user_intent': ('问询',  0.89),
# 'informed_slots': {"功能费": (100, 400)},
# 'requested_slots': ['套餐内容'],
# 'entity_mentioned': [],
# 'sentiment':None,
# 'user_utter': 'hhhhhhhh'
# }
# NLU_results3 = {
# 'scenarios': ('套餐', 0.19),
# 'user_intent': ('比较',  0.44),
# 'informed_slots': {"功能费": (90, 150)},
# 'requested_slots': ['套餐内容'],
# 'entity_mentioned': ['88元畅享套餐', '288元畅享套餐'],
# 'sentiment':None,
# 'user_utter': 'hhhhhhhh'
# }
# dst.state_update(NLU_results, 1)
# print(dst.log)
# print(dst.state)
# dst.state_update(NLU_results2, 2)
# print(dst.log)
# print(dst.state)
# dst.state_update(NLU_results3, 3)
# print(dst.log)
# print(dst.state)


