import os
import sys
from dialog.NLU.NLUManager import NLUManager
from dialog.NLU.EntityDetector import EntityDetector as SubjectDetector
from dialog.NLU.SlotValueDetector import ValueDetector as ObjectDetector
from dialog.NLU.SlotValueDetector import AttrDetector as RelationDetector

save_dirs = {
        'useract': './train/ActDetector_BOW',
        'relation': './train/AttrDetector_BOW',
        'object': './train/ValueDetector_EDST'
    }


print('prepare nlu models ... ')
nlu = NLUManager(save_dirs)
import pprint
while True:
    s = input('输入：')
    pprint.pprint(nlu.get_NLU_results(s, {}))


# MODEL_SAVE_DIR = {
#     'useract': 'train/ActDetector',
#     'relation': 'train/AttrDetector_BOW',
#     'object': 'train/ValueDetector_EDST'
# }

# ig = InputGenerator('../data/tmp')
# user_utter = [
# "来个便宜的套餐",
# "88元畅享套餐都有啥？",
# "我想查一下余额",
# "我要去美国，应该办什么套餐",
# "这个无所谓",
# "不用了，谢谢"]

# # test for ScenariosDetector
# print('\nScenariosDetector测试：')
# SD = ScenariosDetector(MODEL_SAVE_DIR['scenarios'], ig)
# for usr_input in user_utter:
#     print(usr_input)
#     print(SD.get_scenarios_results(usr_input))
# SD.close()

# # test for UserIntentDetector
# print('\nUserIntentDetector测试：')
# UID = UserActDetector(MODEL_SAVE_DIR['userintent'], ig)
# for usr_input in user_utter:
#     print(usr_input)
#     print(UID.get_user_act_results(usr_input))
# # while True:
# #     usr_input = input("请输入：")
# #     print(UID.get_user_intent_results(usr_input, ig))
# UID.close()

# # test for SlotValueDetector
# print('\nSlotValueDetector测试：')
# SVD = SlotValueDetector(MODEL_SAVE_DIR['slotfilling'], ig)
# for usr_input in user_utter:
#     print(usr_input)
#     if not usr_input == '这个无所谓':
#         infoslot = SVD.get_infor_slots_results(usr_input, {})
#     else:
#         infoslot = SVD.get_infor_slots_results(usr_input, {'request':['功能费']})
#     print(infoslot)
#     SlotValueDetector.informable_slot_to_num(infoslot)
#     print(infoslot)
#     print(SVD.get_req_slots_results(usr_input, {'request':['功能费']}))
# while True:
#     usr_input = input("请输入：")
#     reqtype = input("system_request: 1功能费 2流量 3通话 4无\n")
#     if reqtype == '1':
#         print(SVD.get_infor_slots_results(usr_input, {'request':['功能费']}))
#         print(SVD.get_req_slots_results(usr_input, {'request':['功能费']}))
#     elif reqtype == '2':
#         print(SVD.get_infor_slots_results(usr_input, {'request':['套餐内容_国内流量']}))
#         print(SVD.get_req_slots_results(usr_input, {'request':['套餐内容_国内流量']}))
#     elif reqtype == '3':
#         print(SVD.get_infor_slots_results(usr_input, {'request':['套餐内容_国内主叫']}))
#         print(SVD.get_req_slots_results(usr_input, {'request':['套餐内容_国内主叫']}))
#     else:
#         print(SVD.get_infor_slots_results(usr_input, {}))
#         print(SVD.get_req_slots_results(usr_input, {}))

# SVD.close()

# # test for EntityDetector
# print('\nEntityDetector测试：')
# ED = EntityDetector(MODEL_SAVE_DIR['entity'])
# for usr_input in user_utter:
#     print(usr_input)
#     print(ED.get_ER_results(usr_input))
# ED.close()

# # test for NLUManager
# init_state =dst.DialogState.CMCCDialogState()
# print('\nNLUManager测试：')
# NLUM = NLUManager(MODEL_SAVE_DIR)
# for usr_input in user_utter:
#     print(usr_input)
#     result = NLUM.get_NLU_results(usr_input, init_state)
#     pprint.pprint(result)
# NLUM.close()
