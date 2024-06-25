# import pandas as pd
# from prompt_ad_utils import read_input_text_len_control, read_input_no_len_control
# import os
import numpy as np
from pathlib import Path
path='./data/'
# df=pd.read_csv(path+'utterance_data_adrc.csv')
# print(df.head(1))
baseline_root="./output/mlm/"
root="./output/"
switchprompt_root="./output/switchprompt/"
# baseline_bert_test=['bert-base-uncased_epoch10_optimadamw_pre0_bs16_joint_lr1e-05_cvFalse_last',
#                'bert-base-uncased_epoch10_optimadamw_pre0_bs16_joint_lr1e-05_cvFalse_last3rd',
#                'bert-base-uncased_epoch10_optimadamw_pre0_bs16_joint_lr1e-05_cvFalse_last2']
# baseline_roberta_test=['roberta-base_epoch10_optimadamw_pre0_bs16_joint_lr1e-05_cvFalse_last',
#                'roberta-base_epoch10_optimadamw_pre0_bs16_joint_lr1e-05_cvFalse_last3rd',
#                'roberta-base_epoch10_optimadamw_pre0_bs16_joint_lr1e-05_cvFalse_last2']
extended=['bert-base-uncased_16_10_binary_extended_True',
          'bert-base-uncased_16_10_ex_ins_extended_True',
          'bert-base-uncased_16_10_multi_extended_True',
          'emilyalsentzer/Bio_ClinicalBERT_16_10_multi_extended_True'

          ]
forum_undersample=['bert-base-uncased_16_10_binary_forum_undersample_True',
                   'bert-base-uncased_16_10_ex_ins_forum_undersample_True',
                   'bert-base-uncased_16_10_multi_forum_undersample_True',

                   'emilyalsentzer/Bio_ClinicalBERT_16_10_multi_forum_undersample_True',]
augment=[
# 'bert-base-uncased_16_10_ex_ins_extended_augmented_flant5-xl_pvi_perintent_True',
#          'bert-base-uncased_16_10_binary_extended_augmented_flant5-xl_pvi_perintent_True',
         'bert-base-uncased_16_10_multi_extended_augmented_flant5-xl_pvi_perintent_True',
         # 'bert-base-uncased_16_10_multi_extended_augmented_flant5-xl_pvi_avrg_True',
         # 'emilyalsentzer/Bio_ClinicalBERT_16_10_multi_extended_augmented_flant5-xl_pvi_perintent_True'
         ]
# bert-base-uncased_tempmanual49_verbmanual_epoch10_optimadamw_stk0_100_domain2_bs16_prlr0.5_joint_tuneTrue_cvTrue_mFalse
def print_result(result,metric):
    print(metric)
    print('mean %0.5f'%(np.mean(np.array(result[metric]))))
    print(' std %0.5f' % (np.std(np.array(result[metric]))))
    print(' max %0.5f' % (np.max(np.array(result[metric]))))
def process_result(file_path,modelname):
    my_file = Path("./output/"+file_path+'/checkpoint/'+modelname+"_result.txt")
    if my_file.is_file():
        file = open("./output/"+file_path+'/checkpoint/'+modelname+"_result.txt", 'r')
    else:
        print('problem')
        print(file_path)
        return
    result={'acc':[],'f1':[],'prec':[],'rec':[]}
    id=-1
    if file:
        count=0
        while True:
            next_line = file.readline()
            if count<2:
                count+=1
                continue
            # print(next_line)
            if not next_line:
                break
            values=next_line.split('\t')
            if len(values)<5:
                continue
            print(values)
            # if values[1]==id:
            #     continue
            id=values[0]
            result['acc'].append(float(values[1]))
            result['prec'].append(float(values[2]))
            result['rec'].append(float(values[3]))
            result['f1'].append(float(values[4]))
        print(result)
        print('test summary')
        print(file_path)
        print_result(result,'acc')
        print_result(result, 'prec')
        print_result(result, 'rec')
        print_result(result, 'f1')

        file.close()
def save_file(df,name):
    # df=pd.DataFrame(data)
    df.to_pickle('./output/'+name+'.pickle')
    df.to_csv('./output/'+name+'.csv',index=False)
    print('done')
def process_result_cv(file_path):
    if 'last' in file_path:
        file = open('./output/mlm/' + file_path + "/result.txt", 'r')
    else:
        # file = open('./output/'+file_path+"/result.txt", 'r')
        file = open('./output/' + file_path + "/result_ad.txt", 'r')
    result={}
    result_final = {'acc':[],'acc_std':[],'f1':[],'f1_std':[]}
    id=-1
    print(file_path)
    while True:
        next_line = file.readline()

        if not next_line:
            break

        values=next_line.split(" ")
        if int(values[1])==0 :
            continue
        if int(values[1]) in result:
            # print(values)
            # print(result)
            if int(values[0]) in result[int(values[1])]['fold']:
                # print('ekhane')
                # print(result)
                continue
            else:
                # frst elem in line is fold num, second is seed
                # print('fold num')
                # print(int(values[0]))
                result[int(values[1])]['fold'].append(int(values[0]))
                result[int(values[1])]['acc'].append(float(values[2])) #acc
                result[int(values[1])]['f1'].append(float(values[5]))#f1
        else:
            #initialize
            result[int(values[1])]={'acc':[],'f1':[],'fold':[]}
            # print('fold num')
            # print(int(values[0]))
            result[int(values[1])]['fold'].append(int(values[0]))
            result[int(values[1])]['acc'].append(float(values[2]))  # acc
            result[int(values[1])]['f1'].append(float(values[5]))  # f1
    print(result)
    process_cv_result_folsd_across_run(result)
    # save_file(pd.DataFrame(result),'result_cv_man')
    for key in result:
        result_final['acc'].append(np.mean(np.array(result[key]['acc'])))
        result_final['acc_std'].append(np.std(np.array(result[key]['acc'])))
        result_final['f1'].append(np.mean(np.array(result[key]['f1'])))
        result_final['f1_std'].append(np.std(np.array(result[key]['f1'])))
    print(result_final)
    print('cv summary')
    print(file_path)

    print('acc mean %0.5f'%(np.mean(np.array(result_final['acc']))))
    print('acc std %0.5f' % (np.mean(np.array(result_final['acc_std']))))
    # print('acc max %0.5f' % (np.max(np.array(result['acc']))))
    print('f1 mean %0.5f' % (np.mean(np.array(result_final['f1']))))
    print('f1 std %0.5f' % (np.mean(np.array(result_final['f1_std']))))

    file.close()
#for stat analysis, each fold result will be mean across runs
#output: {acc:[a1,a2,a3,a4,a5],f1:[f1,f2,f3,f4,f5]}, each acc averaged acrosss 3 runs
def process_cv_result_folsd_across_run(result):
    fold_result_across_run_acc={}
    fold_result_across_run_f1 = {}
    for key in result:
        for fld in result[key]['fold']:
            if fld not in fold_result_across_run_acc:
                # print('process_cv')
                # print(fld)
                fold_result_across_run_acc[fld]=[]
                fold_result_across_run_acc[fld].append(result[key]['acc'][fld])
                fold_result_across_run_f1[fld] = []
                fold_result_across_run_f1[fld].append(result[key]['f1'][fld])
            else:


                fold_result_across_run_acc[fld].append(result[key]['acc'][fld])

                fold_result_across_run_f1[fld].append(result[key]['f1'][fld])
    final_acc_f1={'acc':[],'f1':[]}
    for key in fold_result_across_run_acc:
        final_acc_f1['acc'].append(np.mean(np.array(fold_result_across_run_acc[key])))
    for key in fold_result_across_run_f1:
        final_acc_f1['f1'].append(np.mean(np.array(fold_result_across_run_f1[key])))
    print(final_acc_f1)
# for path in roberta_man_test:
#     print(path)
#     process_result(path)
def run_process_result(dataset):
    for path in dataset:
        print(path)
        if 'Bio_ClinicalBERT' in path:
            modelname='Bio_ClinicalBERT'
        else:
            modelname = 'bert-base-uncased'


        process_result(path,modelname)
print('start')
print('augment')
run_process_result(augment)
# print('extended')
# run_process_result(extended)
# print('forum_undersample')
# run_process_result(forum_undersample)


# df=df.loc[df['ncc']!=1]
# df['text']=df['utterance']
# df['ad']=df['label']
# df['filename']=[name.split('_')[0]for name in df['file']]
# df['id']=df['filename']
# df['domain']=['memorable event']*len(df['id'])
# df['domain1']=['a memorable event in early adulthood']*len(df['id'])
# df['domain2']=['an event from memory lane in early adult life']*len(df['id'])
# df=df.drop(['utterance','label','file'],axis=1)
# df.to_csv(path+'adrc.csv')
