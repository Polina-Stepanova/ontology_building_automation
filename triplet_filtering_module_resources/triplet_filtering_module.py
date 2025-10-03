from razdel import tokenize
import pymorphy2
import pandas as pd

def adjective_subterm_selection(reltype,csv_tbl_src,csv_tbl_selected,morph):
  """Отбор триплетов из таблицы (pandas DataFrame) csv_tbl_src в csv_tbl_selected определенного вида отношения reltype с подчиненным термином, выраженным прилагательными. morph - экземпляр pymorphy2.MorphAnalyzer"""
  rel_table=csv_tbl_src[(csv_tbl_src['SubRole']==reltype)]
  for index, row in rel_table.iterrows():
    subterm_split=[w.text for w in list(tokenize(row['SubTerm'].strip()))]
    adj_flag=True
    for w in subterm_split:
       p=morph.parse(w)[0]
       if ((p.tag.POS!='ADJF')&(p.tag.POS!='ADJS')&(p.tag.POS!= 'PRTF')&(p.tag.POS!= 'PRTS')): #причастие или прилагательное, полное или краткое
         adj_flag=False
         break
    if(adj_flag):
      csv_tbl_selected.loc[len(csv_tbl_selected)]=[row['MainTerm'],row['SubRole'],row['SubTerm']+' '+row['MainTerm']]#без сохранения исходных индексов

def adjective_subterm_no_adj_main_selection(reltype,csv_tbl_src,csv_tbl_selected,morph):
  """Отбор триплетов из таблицы (pandas DataFrame) csv_tbl_src в csv_tbl_selected определенного вида отношения reltype с подчиненным термином, выраженным прилагательными, в которых главный термин НЕ выражен прилагательными. morph - экземпляр pymorphy2.MorphAnalyzer"""
  rel_table=csv_tbl_src[csv_tbl_src['SubRole']==reltype]
  for index, row in rel_table.iterrows():
    subterm_split=[w.text for w in list(tokenize(row['SubTerm'].strip()))]
    adj_flag_sub=True
    for w in subterm_split:
        p=morph.parse(w)[0]
        if ((p.tag.POS!='ADJF')&(p.tag.POS!='ADJS')&(p.tag.POS!= 'PRTF')&(p.tag.POS!= 'PRTS')): #причастие или прилагательное, полное или краткое
          adj_flag_sub=False
          break
    mainterm_split=[w.text for w in list(tokenize(row['MainTerm'].strip()))]
    adj_flag_main=True
    for w in mainterm_split:
        p=morph.parse(w)[0]
        if ((p.tag.POS!='ADJF')&(p.tag.POS!='ADJS')&(p.tag.POS!= 'PRTF')&(p.tag.POS!= 'PRTS')):
          adj_flag_main=False
          break
    if((adj_flag_sub)&(not adj_flag_main)):
      csv_tbl_selected.loc[len(csv_tbl_selected)]=[row['MainTerm'],row['SubRole'],row['SubTerm']+' '+row['MainTerm']]#без сохранения исходных индексов

def mainterm_in_subterm_with_adj_selection(reltype,csv_tbl_src,csv_tbl_selected,morph):
  """Отбор триплетов из таблицы (pandas DataFrame) csv_tbl_src в csv_tbl_selected определенного вида отношения reltype с подчиненным термином, выраженным сочетанием главного термина с прилагательными. morph - экземпляр pymorphy2.MorphAnalyzer"""
  rel_table=csv_tbl_src[csv_tbl_src['SubRole']==reltype]
  for index, row in rel_table.iterrows():
    if (row['SubRole']==reltype):
       if (row['SubTerm'].endswith(row['MainTerm'])):
          #проверка состава остальной части подчиненного термина из прилагательных/причастий (описательность)
          subterm_tail=row['SubTerm'][:row['SubTerm'].rfind(row['MainTerm'])]
          subterm_tail_split=[w.text for w in list(tokenize(subterm_tail.strip()))]
          adj_flag=True
          for w in subterm_tail_split:
            p=morph.parse(w)[0]
            if ((p.tag.POS!='ADJF')&(p.tag.POS!='ADJS')&(p.tag.POS!= 'PRTF')&(p.tag.POS!= 'PRTS')):
               adj_flag=False
               break
          if(adj_flag):
             csv_tbl_selected.loc[len(csv_tbl_selected)]=[row['MainTerm'],row['SubRole'],row['SubTerm']]#без сохранения исходных индексов

def mainterm_in_subterm_as_main_selection(reltype,csv_tbl_src,csv_tbl_selected):
  """Отбор триплетов из таблицы (pandas DataFrame) csv_tbl_src в csv_tbl_selected определенного вида отношения reltype, в которых главный термин содержится в подчиненном в неизменном виде."""
  rel_table=csv_tbl_src[csv_tbl_src['SubRole']==reltype]
  for index, row in rel_table.iterrows():
      subterm_split=[w.text for w in list(tokenize(row['SubTerm'].strip()))]
      mainterm_split=[w.text for w in list(tokenize(row['MainTerm'].strip()))]#main внутри sub
      subterm_recollect=' '.join(subterm_split)
      mainterm_recollect=' '.join(mainterm_split)
      if (mainterm_recollect in subterm_recollect):
         csv_tbl_selected.loc[len(csv_tbl_selected)]=[row['MainTerm'],row['SubRole'],row['SubTerm']]#без сохранения исходных индексов
      
def mainterm_in_subterm_exact_line_selection(reltype,csv_tbl_src,csv_tbl_selected):
  """Отбор триплетов из таблицы (pandas DataFrame) csv_tbl_src в csv_tbl_selected определенного вида отношения reltype, в которых главный термин содержится в подчиненном в неизменном виде (упрощенное исполнение)."""
  rel_table=csv_tbl_src[csv_tbl_src['SubRole']==reltype]
  for index, row in rel_table.iterrows():
    if (row['MainTerm'] in row['SubTerm']):
      csv_tbl_selected.loc[len(csv_tbl_selected)]=[row['MainTerm'],row['SubRole'],row['SubTerm']]
    
def mainterm_in_subterm_selection(reltype,csv_tbl_src,csv_tbl_selected,morph):
  """Отбор триплетов из таблицы (pandas DataFrame) csv_tbl_src в csv_tbl_selected определенного вида отношения reltype, в которых главный термин содержится в подчиненном в любом виде (возможно и как главная часть, и как подчиненная часть именного словосочетания подчиненного термина). morph - экземпляр pymorphy2.MorphAnalyzer"""
  rel_table=csv_tbl_src[csv_tbl_src['SubRole']==reltype]
  for index, row in rel_table.iterrows():
      subterm_split=[morph.normal_forms(w.text)[0] for w in list(tokenize(row['SubTerm'].strip()))]
      mainterm_split=[morph.normal_forms(w.text)[0] for w in list(tokenize(row['MainTerm'].strip()))]#main внутри sub
      subterm_recollect=' '.join(subterm_split)
      mainterm_recollect=' '.join(mainterm_split)
      if (mainterm_recollect in subterm_recollect):
         csv_tbl_selected.loc[len(csv_tbl_selected)]=[row['MainTerm'],row['SubRole'],row['SubTerm']]#без сохранения исходных индексов

def first_variant_in_sentence(reltype,csv_tbl_src,csv_tbl_selected):
  """Отбор триплетов из таблицы (pandas DataFrame) csv_tbl_src в csv_tbl_selected определенного вида отношения reltype, которые являлись первым (0) вариантом извлечения для своего предложения."""
  rel_table=csv_tbl_src[csv_tbl_src['SubRole']==reltype]
  for index, row in rel_table.iterrows():
       for n in row['ExtractedSeqNum'].split(';_;'):#в случае если 0 может встречаться как часть других номеров извлечений, например 10
        if (n.strip()=='0'):
          csv_tbl_selected.loc[len(csv_tbl_selected)]=[row['MainTerm'],row['SubRole'],row['SubTerm']]
          break

def nth_variant_in_sentence(reltype,csv_tbl_src,csv_tbl_selected,nth):
  """Отбор триплетов из таблицы (pandas DataFrame) csv_tbl_src в csv_tbl_selected определенного вида отношения reltype, которые являлись некоторым определенным (nth) вариантом извлечения для своего предложения."""
  rel_table=csv_tbl_src[csv_tbl_src['SubRole']==reltype]
  for index, row in rel_table.iterrows():
       for n in row['ExtractedSeqNum'].split(';_;'):#в случае если 0 может встречаться как часть других номеров извлечений
        if (n.strip()==str(nth)):
          csv_tbl_selected.loc[len(csv_tbl_selected)]=[row['MainTerm'],row['SubRole'],row['SubTerm']]
          break

def symmetrical_only_one(reltype,csv_tbl_src,csv_tbl_selected):
  """Отбор из таблицы (pandas DataFrame) csv_tbl_src в csv_tbl_selected для определенного вида отношения reltype, являющегося симметричным, только одного (первого) варианта триплетов, отличающихся только порядком терминов."""
  rel_table=csv_tbl_src[csv_tbl_src['SubRole']==reltype]
  indexes_of_symm=[] #запоминание индексов триплетов, являющихся вариантами (симметричными, с другим порядком терминов) уже рассмотренных
  for index, row in rel_table.iterrows():
     if (index not in indexes_of_symm):#первый раз встречаем такую пару терминов
       csv_tbl_selected.loc[len(csv_tbl_selected)]=[row['MainTerm'],row['SubRole'],row['SubTerm']]
       symm_versions_table=rel_table[(((rel_table['MainTerm']==row['MainTerm'])&(rel_table['SubTerm']==row['SubTerm']))|((rel_table['MainTerm']==row['SubTerm'])&(rel_table['SubTerm']==row['MainTerm'])))]
       #все копии и симметричные копии (включая себя)
       indexes_of_symm.extend(list(symm_versions_table.index.values))
       #их индексы, чтобы потом пропускать их

def NN_patterns_match(reltype,csv_tbl_NN,csv_tbl_patterns,csv_tbl_selected):
  """Отбор для определенного вида отношения reltype из таблицы извлечений нейросети mREBEL csv_tbl_NN (pandas DataFrame) в csv_tbl_selected триплетов, совпадающих по виду отношения, главному термину и исходному текстовому фрагменту с извлечением шаблонов (csv_tbl_patterns)."""
  rel_table_NN=csv_tbl_NN[csv_tbl_NN['SubRole']==reltype]
  rel_table_pat=csv_tbl_patterns[csv_tbl_patterns['SubRole']==reltype]
  for index_p, row_p in rel_table_pat.iterrows():
    for index_nn, row_nn in rel_table_NN.iterrows():
      if ((row_nn['SubRole']==row_p['SubRole'])&(row_nn['MainTerm']==row_p['MainTerm'])&(row_p['SrcFragment'] in row_nn['SrcFragment'])):
        csv_tbl_selected.loc[len(csv_tbl_selected)]=[row_nn['MainTerm'],row_nn['SubRole'],row_nn['SubTerm']]
        #извлечения шаблонов отбираются все для определенных видов отношений, реализуется другой функцией

def hyponimy_from_opposite_different(reltype_symm,reltype_base,csv_tbl_src,csv_tbl_selected):
  """Отбор для определенного вида отношения reltype_base из таблицы (pandas DataFrame) csv_tbl_src пар триплетов, главные термины которых одинаковы, а пара зависимых также состоит в определенном симметричном отношении reltype_symm. 
  Добавление для отношения reltype_base, в случае наличия триплета, подчиненный термин которого состоит в определенном симметричном отношении reltype_symm с некоторым другим термином, 
  у которого нет данного отношения reltype_base с данным главным термином, но который при этом содержит в себе этот главный термин, 
  триплета отношения reltype_base между данным главным термином и не имевшим связи с ним вторым в симметричном отношении reltype_symm термином."""
   diff_t=csv_tbl_src[csv_tbl_src['SubRole']==reltype_symm]#отношения "противоположность" и "различие" имеют альт. имена "противоположнОЕ" и "различие С",  в магистерской использована сокращенная версия
   for index_d, row_d in diff_t.iterrows():#если для триплета(пары терминов) в симметричном есть нужного отношения триплеты с обоими (и совпадающие по главному) то отбираются оба
     base_t_symm_main=csv_tbl_src[(csv_tbl_src['SubRole']==reltype_base)&(csv_tbl_src['SubTerm']==row_d['MainTerm'])]
     base_t_symm_sub=csv_tbl_src[(csv_tbl_src['SubRole']==reltype_base)&(csv_tbl_src['SubTerm']==row_d['SubTerm'])]
     base_t_symm_main_mainset=list(set(list(base_t_symm_main['MainTerm'])))#множество главных терминов в нужном base-отношении с термином из симметричного отношения, который стоит первым
     base_t_symm_sub_mainset=list(set(list(base_t_symm_sub['MainTerm'])))#множество главных терминов в нужном base-отношении с термином из симметричного отношения, который стоит вторым
     for maint in base_t_symm_main_mainset:#с какими главными у первого в паре в симметричном есть отношения: каких из них нет с вторым в паре => если главный в base-отношении для первого при этом содержится в втором из симметричного отношения  - добавить для второго
        if (maint in base_t_symm_sub_mainset):#вид отношения, главный термин для обоих и оба варианта зависимых по симметричному отношению зафиксированы, можно напрямую добавить ряды из этих элементов
           csv_tbl_selected.loc[len(csv_tbl_selected)]=[maint,reltype_base,row_d['MainTerm']]
           csv_tbl_selected.loc[len(csv_tbl_selected)]=[maint,reltype_base,row_d['SubTerm']]
        else:
          subterm_split=[w.text for w in list(tokenize(row_d['MainTerm'].strip()))]#по какому из терминов в симметричном произошло совпадение
          mainterm_split=[w.text for w in list(tokenize(maint.strip()))]#main внутри sub
          subterm_recollect=' '.join(subterm_split)
          mainterm_recollect=' '.join(mainterm_split)
          if (mainterm_recollect in subterm_recollect):
             csv_tbl_selected.loc[len(csv_tbl_selected)]=[maint,reltype_base,row_d['SubTerm']]
     for maint in base_t_symm_sub_mainset:
      if (maint not in base_t_symm_main_mainset):
          subterm_split=[w.text for w in list(tokenize(row_d['SubTerm'].strip()))]
          mainterm_split=[w.text for w in list(tokenize(maint.strip()))]#main внутри sub
          subterm_recollect=' '.join(subterm_split)
          mainterm_recollect=' '.join(mainterm_split)
          if (mainterm_recollect in subterm_recollect):
             csv_tbl_selected.loc[len(csv_tbl_selected)]=[maint,reltype_base,row_d['SubTerm']]#если нашлось отношение для второго в симметричном, для которого нет отношения с первым, и главный термин которого входит в первый термин в симметричном - то добавить такое отношение для первого в симметричном

#В данной реализации использует другую функцию (whole_relation) для отбора всех экземпляров "главного" отношения, но может использоваться без строчки с вызовом этой функции в случае только отбора несовпадающих с "главным" извлечений "вторичного" отношения
def general_vs_specific_relation(rel_main,rel_sec,csv_tbl_src,csv_tbl_selected):
  """Для двух определенных видов отношений, одно из которых считается приоритетным ("главным", rel_main) а второе  - "вторичным" (rel_sec) между которыми возникают пересечения (извлечение триплетов обоих отношений для одних и тех же терминов), 
  отбор из таблицы (pandas DataFrame) csv_tbl_src в csv_tbl_selected только триплетов "вторичного" отношения, не имеющих соответствующего аналога с приоритетным отношением. Использует функцию whole_relation."""
  #отбираются только несовпадающие из "вторичного" и просто все из "главного"
  sec_rel_t=csv_tbl_src[csv_tbl_src['SubRole']==rel_sec]
  main_rel_t=csv_tbl_src[csv_tbl_src['SubRole']==rel_main]
  for index, row in sec_rel_t.iterrows():
    match_list=list(main_rel_t[((main_rel_t['MainTerm']==row['MainTerm'])&(main_rel_t['SubTerm']==row['SubTerm']))].index.values)
    if(len(match_list)==0): # пустой список = нет совпадающего предпочтительного отношения = можно добавить в таблицу
       csv_tbl_selected.loc[len(csv_tbl_selected)]=[row['MainTerm'],rel_sec,row['SubTerm']]
  whole_relation(rel_main,csv_tbl_src,csv_tbl_selected)

#Парная функции general_vs_specific_relation - результат - только пересечения, для "главного" отношения
def general_vs_specific_relation_matches(rel_main,rel_sec,csv_tbl_src,csv_tbl_selected):
  """Для двух определенных видов отношений, одно из которых считается приоритетным ("главным", rel_main) а второе  - "вторичным" (rel_sec), в случае наличия для одной и той же пары терминов триплетов обоих видов отношений - отбор из таблицы (pandas DataFrame) csv_tbl_src в csv_tbl_selected только триплета приоритетного отношения"""
  sec_rel_t=csv_tbl_src[csv_tbl_src['SubRole']==rel_sec]
  main_rel_t=csv_tbl_src[csv_tbl_src['SubRole']==rel_main]
  for index, row in sec_rel_t.iterrows():
    match_list=list(main_rel_t[((main_rel_t['MainTerm']==row['MainTerm'])&(main_rel_t['SubTerm']==row['SubTerm']))].index.values)
    if(len(match_list)>0):
       csv_tbl_selected.loc[len(csv_tbl_selected)]=[row['MainTerm'],rel_main,row['SubTerm']]

def whole_relation(reltype,csv_tbl_src,csv_tbl_selected):
  """Отбор из таблицы (pandas DataFrame) csv_tbl_src в csv_tbl_selected всех триплетов для определенного вида отношения reltype"""
  rel_table=csv_tbl_src[csv_tbl_src['SubRole']==reltype]
  for index, row in rel_table.iterrows():
     csv_tbl_selected.loc[len(csv_tbl_selected)]=[row['MainTerm'],row['SubRole'],row['SubTerm']]

def both_order_pairs_deletion(reltype,csv_tbl_src,csv_tbl_selected):
  """Отбор из таблицы (pandas DataFrame) csv_tbl_src в csv_tbl_selected для определенного вида отношения reltype (не являющегося симметричным) всех триплетов, КРОМЕ триплетов из таких пар терминов Т1 и Т2, которые встречаются в этих триплетах и в прямом (субъект Т1, объект Т2), и в обратном (субъект Т2, объект Т1) порядке одновременно."""
  rel_table=csv_tbl_src[csv_tbl_src['SubRole']==reltype]# отбор всех триплетов нужного отношения
  indexes_to_skip=[] #запоминание индексов триплетов, для которых найден хоть один с обратным порядком, индексов всех его дубликатов и индексов всех обратных ему триплетов
  for index, row in rel_table.iterrows():
     if (index not in indexes_to_skip):#первый раз встречаем такую пару терминов
       reverse_versions_table=rel_table[((rel_table['MainTerm']==row['SubTerm'])&(rel_table['SubTerm']==row['MainTerm']))] # триплеты с обратным порядком
       dup_versions_table=rel_table[((rel_table['MainTerm']==row['MainTerm'])&(rel_table['SubTerm']==row['SubTerm']))] # дубликаты для пропуска при дальнейшем просмотре таблицы
       indexes_to_skip.extend(list(dup_versions_table.index.values)) # нужно и если есть обратные данному триплеты, и если нет - тогда это просто фильтр дубликатов
       if (len(reverse_versions_table)>0) :
         indexes_to_skip.extend(list(reverse_versions_table.index.values)) # обратные триплеты в оставшейся части просматриваемой таблицы убираются из дальнейшего просмотра
       else:
        csv_tbl_selected.loc[len(csv_tbl_selected)]=[row['MainTerm'],row['SubRole'],row['SubTerm']] # текущий триплет отбирается (в единственном экземпляре) только при отсутствии обратных
