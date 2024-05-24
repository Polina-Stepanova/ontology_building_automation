import sys
from sys import argv
import subprocess
import lxml
from lxml import etree
import pandas as pd
import re
import csv


flag_csv=False
name_csv=""
flag_t=False
name_t=""
flag_s=False
flag_u=False
flag_i=False
flag_p=False


if(len(sys.argv)>1):  #[0]=имя программы
    prog_args = [] 
    for i in range (1,len(sys.argv),2):
        if(sys.argv[i]=="-u"):
            flag_u = True
            if(len(sys.argv)-1>i):
              prog_args.append(sys.argv[i+1])
        elif (sys.argv[i]=="-h"):
          print('''necessary parameters:
   -u <.exe file> адрес исполняемого файла утилиты LSPL (lspl-find.exe address)
   -p <file> адрес файла с LSPL-шаблонами (LSPL patterns file address)
   -s <file> адрес файла с списком целевых LSPL-шаблонов (LSPL utility's target patterns list file address)
   -i <file> адрес файла исходного текста (LSPL utility's text input file address)
   -t <file> адрес файла вывода шаблонов с текстовым выводом (LSPL utility's text output file address (output for patterns with text transformation))
   -e <file> адрес файла ошибок (LSPL utility's error output file address)
   -b <file> адрес файла результирующей csv-таблицы (resulting csv table file address)
optional parameters:
   -o <file> адрес файла вывода всех шаблонов (LSPL utility's output file for all patterns)
   -r <file> адрес файла вывода шаблонов с выводом в виде шаблонов (LSPL utility's output file for patterns with pattern transformation)
   -c <enc> кодировка текста (file encryption (windows-1251 default))\n''')
          sys.exit()
        elif(sys.argv[i]=="-b"):
            flag_csv = True
            if(len(sys.argv)-1>i):
                name_csv=sys.argv[i+1]
        elif (sys.argv[i] == "-t"):
            flag_t = True
            prog_args.append(sys.argv[i])
            if (len(sys.argv) - 1 > i):
                prog_args.append(sys.argv[i+1])
                name_t=sys.argv[i+1]
        elif (sys.argv[i] == "-s"):
            flag_s = True
            prog_args.append(sys.argv[i])
            if (len(sys.argv) - 1 > i):
                prog_args.append(sys.argv[i+1])
        elif (sys.argv[i] == "-p"):
            flag_p = True
            prog_args.append(sys.argv[i])
            if (len(sys.argv) - 1 > i):
                prog_args.append(sys.argv[i+1])
        elif (sys.argv[i] == "-i"):
            flag_i = True
            prog_args.append(sys.argv[i])
            if (len(sys.argv) - 1 > i):
                prog_args.append(sys.argv[i+1])
        elif ((len(sys.argv[i])==2)&(sys.argv[i][0]=='-')):# любой параметр из остальных (все флаги из одной буквы)
            prog_args.append(sys.argv[i])
            if (len(sys.argv) - 1 > i):
                prog_args.append(sys.argv[i+1])



    if (not flag_u):
        print("-u <.exe file> : адрес исполняемого файла утилиты LSPL не указан (adress of the executable of the underlying utility not specified) (help: -h)\n")
        sys.exit()
    if (not flag_i):
        print("-s <file> : адрес файла с списком целевых LSPL-шаблонов не указан (file with the input text for the underlying utility not specified) (help: -h)\n")
        sys.exit()
    if (not flag_t):
        print("-t <file> : адрес файла вывода шаблонов с текстовым выводом не указан (text output file for the underlying utility not specified) (help: -h)\n")
        sys.exit()
    if (not flag_p):
        print("-p <file> : адрес файла с LSPL-шаблонами не указан (file with a list of patterns for the underlying utility not specified) (help: -h)\n")
        sys.exit()
    if (not flag_s):
        print("-s <file> : адрес файла с списком целевых LSPL-шаблонов не указан (все = *, либо список имен шаблонов по 1 в строке) (file with a list of patterns of interest for the underlying utility not specified ( * if all patterns or a list of pattern names one per line)) (help: -h)\n")
        sys.exit()
    if (not flag_csv):
        print("-b <file> : адрес файла результирующей csv-таблицы не указан (output file for csv results not specified) (help: -h)\n")
        sys.exit()

else:
  print('''necessary parameters:
   -u <.exe file> адрес исполняемого файла утилиты LSPL (lspl-find.exe address)
   -p <file> адрес файла с LSPL-шаблонами (LSPL patterns file address)
   -s <file> адрес файла с списком целевых LSPL-шаблонов (LSPL utility's target patterns list file address)
   -i <file> адрес файла исходного текста (LSPL utility's text input file address)
   -t <file> адрес файла вывода шаблонов с текстовым выводом (LSPL utility's text output file address (output for patterns with text transformation))
   -e <file> адрес файла ошибок (LSPL utility's error output file address)
   -b <file> адрес файла результирующей csv-таблицы (resulting csv table file address)
optional parameters:
   -o <file> адрес файла вывода всех шаблонов (LSPL utility's output file for all patterns)
   -r <file> адрес файла вывода шаблонов с выводом в виде шаблонов (LSPL utility's output file for patterns with pattern transformation)
   -c <enc> кодировка текста (file encryption (windows-1251 default))\n''')
  sys.exit()

subprocess.run(prog_args)

def crop_output(match_term):#очистка запятых и других лишних знаков и пустот в выходном тексте шаблонов
    for separators1, separators2 in (" ,", ","), (",,", ","),(" ;", ";"),(";;", ";"), (", /", " /"),   (", )", ")"),("; ]", "]")  ,("\n", " "),("  ", " "),   ("( ","("),(" )",")"),("[ ","["),(" ]","]"):
        rez = match_term.replace(separators1, separators2)
        while (rez != match_term):
            match_term = rez
            rez = match_term.replace(separators1, separators2)
    return rez


with open(name_t, 'rb') as f:
   eof_check=f.readline()
if(eof_check==b''):
    sys.exit()

with open(name_t,'rb') as f:
   tree = etree.parse(f)

df_csv = pd.DataFrame(columns=['Pattern','MainRole','MainTerm','SubRole','SubTerm','SrcFragment'])

rextext='([ \-\w]+)\((.+)\) *- *([ \-\w]*)\((.+)\)' # использованные шаблоны имеют формат извлечения: MainRole(MainTerm,MainTerm,...)-SubRole(SubTerm,SubTerm,...)
rexmulterm='\[(.+)\]\[(.+)\]' # термин с рядом зависимых прилагательных извлекается специальным шаблоном как [ГлавноеСлово][Прилагательное;Прилагательное;...]

root=tree.getroot()
for text in root:
    for goal in text:
       match_found=False
       curr_pat_name=goal.get("name")
       fpos=0 #начальная граница фрагмента с извлечением
       epos=0 #конечная граница
       best_match=""
       match_fragm=""
       for match in goal:
           if (fpos==0):#самый первый вариант для очередного места текста
               fpos=int(match.get("startPos"))
               epos=int(match.get("endPos"))
               best_match=match[1].text.lower()#что получили
               match_fragm=match[0].text.lower()#откуда
               match_found=True
           else:
               if(( int(match.get("startPos"))==fpos) and (int(match.get("endPos"))>epos)):#нашли более длинный фрагмент для этого шаблона в том же месте (упорядочены как "а аб абс бс с")
                   fpos = int(match.get("startPos"))
                   epos = int(match.get("endPos"))
                   best_match = match[1].text.lower()#что получили
                   match_fragm = match[0].text.lower()#откуда
               else:
                   if (not(( int(match.get("startPos")) >= fpos) and (int(match.get("endPos")) <= epos))): #закончили просматривать остальные, более короткие, варианты в пределах уже найденного максимального фрагмента - это новое начало И конец
                       #сохраняется результат из фрагмента максимальной длины на данный момент по мере просмотра, и новые крайние точки (начальная наименьшая - сохраняется из первого для группы вариантов, а конечная - наиболее отдаленная)
                       rexpmatch = re.search(rextext, crop_output(best_match))
                       if (rexpmatch!=None):
                           role1=rexpmatch.groups()[0]
                           role2=rexpmatch.groups()[2]
                           for s1_1 in rexpmatch.groups()[1].split(','):

                               #получение набора отдельных терминов из сложного с рядом прилагательных (если главный термин таков)
                               s1_mult=[]
                               multermmatch1 = re.search(rexmulterm, s1_1)
                               if(multermmatch1!=None):
                                   for s1_sing in multermmatch1.groups()[1].split(';'): s1_mult.append(s1_sing.strip()+' '+multermmatch1.groups()[0])
                               else: s1_mult=[s1_1]

                               for s1 in s1_mult:

                                  for s2 in rexpmatch.groups()[3].split(','):
                                     t1=s1.strip()
                                     t2=s2.strip()

                                     #получение набора отдельных терминов из сложного с рядом прилагательных (если подчиненный термин таков)
                                     multermmatch = re.search(rexmulterm, s2)
                                     if(multermmatch!=None):
                                        for s in multermmatch.groups()[1].split(';'):
                                          ts=s.strip()
                                          sterm=ts+' '+multermmatch.groups()[0]
                                          checkrepeats=df_csv[(df_csv['MainRole']==role1)&( df_csv['SubRole']==role2 )&(df_csv['MainTerm']==s1)&( df_csv['SubTerm']==sterm)]
                                          if not(checkrepeats.empty): #для триплетов, совпадающих по терминам и виду отношения, сохранение только имени шаблона и исходного фрагмента, дополнением к сответствующим полям строки для первого такого триплета, добавленного в таблицу
                                            #df_csv['Pattern'][list(checkrepeats.index.values)[0]]=df_csv['Pattern'][list(checkrepeats.index.values)[0]]+', '+curr_pat_name
                                            df_csv.loc[list(checkrepeats.index.values)[0],'Pattern']=df_csv['Pattern'][list(checkrepeats.index.values)[0]]+', '+curr_pat_name
                                            #df_csv['SrcFragment'][list(checkrepeats.index.values)[0]]=df_csv['SrcFragment'][list(checkrepeats.index.values)[0]]+';_; '+match_fragm 
                                            df_csv.loc[list(checkrepeats.index.values)[0],'SrcFragment']=df_csv['SrcFragment'][list(checkrepeats.index.values)[0]]+';_; '+match_fragm 
                                          else:
                                            pairrow=[curr_pat_name,role1,s1,role2,sterm ,match_fragm]
                                            df_csv.loc[len(df_csv)]=pairrow 
                                        continue

                                     checkrepeats=df_csv[(df_csv['MainRole']==role1)&( df_csv['SubRole']==role2 )&(df_csv['MainTerm']==t1)&( df_csv['SubTerm']==t2)]
                                     if not(checkrepeats.empty):
                                        #df_csv['Pattern'][list(checkrepeats.index.values)[0]]=df_csv['Pattern'][list(checkrepeats.index.values)[0]]+', '+curr_pat_name
                                        df_csv.loc[list(checkrepeats.index.values)[0],'Pattern']=df_csv['Pattern'][list(checkrepeats.index.values)[0]]+', '+curr_pat_name
                                        #df_csv['SrcFragment'][list(checkrepeats.index.values)[0]]=df_csv['SrcFragment'][list(checkrepeats.index.values)[0]]+';_; '+match_fragm 
                                        df_csv.loc[list(checkrepeats.index.values)[0],'SrcFragment']=df_csv['SrcFragment'][list(checkrepeats.index.values)[0]]+';_; '+match_fragm 
                                     else:
                                        pairrow=[curr_pat_name,role1,t1,role2,t2 ,match_fragm]
                                        df_csv.loc[len(df_csv)]=pairrow 

                       fpos = int(match.get("startPos"))
                       epos = int(match.get("endPos"))
                       best_match = match[1].text.lower()#что получили
                       match_fragm = match[0].text.lower()#откуда
                       match_found=True
       if(match_found):#очередной фрагмент сравнивается и сохраняется только при переходе к рассмотрению новых границ в пределах того же фрагмента, для последнего в группе извлечений из одного фрагмента нужно провести процедуру отдельно
           rexpmatch = re.search(rextext,crop_output(best_match))
           if (rexpmatch!=None):
                 role1=rexpmatch.groups()[0]
                 role2=rexpmatch.groups()[2]
                 for s1_1 in rexpmatch.groups()[1].split(','):

                     #получение набора отдельных терминов из сложного с рядом прилагательных (если главный термин таков)
                     s1_mult=[]
                     multermmatch1 = re.search(rexmulterm, s1_1)
                     if(multermmatch1!=None):
                         for s1_sing in multermmatch1.groups()[1].split(';'): s1_mult.append(s1_sing.strip()+' '+multermmatch1.groups()[0])
                     else: s1_mult=[s1_1]

                     for s1 in s1_mult:

                        for s2 in rexpmatch.groups()[3].split(','):
                           t1=s1.strip()
                           t2=s2.strip()

                           #получение набора отдельных терминов из сложного с рядом прилагательных (если подчиненный термин таков)
                           multermmatch = re.search(rexmulterm, s2)
                           if(multermmatch!=None):
                              for s in multermmatch.groups()[1].split(';'):
                                ts=s.strip()
                                sterm=ts+' '+multermmatch.groups()[0]
                                checkrepeats=df_csv[(df_csv['MainRole']==role1)&( df_csv['SubRole']==role2 )&(df_csv['MainTerm']==s1)&( df_csv['SubTerm']==sterm)]
                                if not(checkrepeats.empty):
                                  #df_csv['Pattern'][list(checkrepeats.index.values)[0]]=df_csv['Pattern'][list(checkrepeats.index.values)[0]]+', '+curr_pat_name
                                  df_csv.loc[list(checkrepeats.index.values)[0],'Pattern']=df_csv['Pattern'][list(checkrepeats.index.values)[0]]+', '+curr_pat_name
                                  #df_csv['SrcFragment'][list(checkrepeats.index.values)[0]]=df_csv['SrcFragment'][list(checkrepeats.index.values)[0]]+';_; '+match_fragm 
                                  df_csv.loc[list(checkrepeats.index.values)[0],'SrcFragment']=df_csv['SrcFragment'][list(checkrepeats.index.values)[0]]+';_; '+match_fragm 
                                else:
                                  pairrow=[curr_pat_name,role1,s1,role2,sterm ,match_fragm]
                                  df_csv.loc[len(df_csv)]=pairrow 
                              continue

                           checkrepeats=df_csv[(df_csv['MainRole']==role1)&( df_csv['SubRole']==role2 )&(df_csv['MainTerm']==t1)&( df_csv['SubTerm']==t2)]
                           if not(checkrepeats.empty):
                              #df_csv['Pattern'][list(checkrepeats.index.values)[0]]=df_csv['Pattern'][list(checkrepeats.index.values)[0]]+', '+curr_pat_name
                              df_csv.loc[list(checkrepeats.index.values)[0],'Pattern']=df_csv['Pattern'][list(checkrepeats.index.values)[0]]+', '+curr_pat_name
                              #df_csv['SrcFragment'][list(checkrepeats.index.values)[0]]=df_csv['SrcFragment'][list(checkrepeats.index.values)[0]]+';_; '+match_fragm 
                              df_csv.loc[list(checkrepeats.index.values)[0],'SrcFragment']=df_csv['SrcFragment'][list(checkrepeats.index.values)[0]]+';_; '+match_fragm 
                           else:
                              pairrow=[curr_pat_name,role1,t1,role2,t2 ,match_fragm]
                              df_csv.loc[len(df_csv)]=pairrow  
 

df_csv.to_csv(name_csv,index=False)
