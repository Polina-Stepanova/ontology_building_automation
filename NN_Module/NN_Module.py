import transformers
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from razdel import sentenize
from razdel import tokenize
import pymorphy2
morph = pymorphy2.MorphAnalyzer()
import pandas as pd
import csv
import sys
from sys import argv

name_t=''
name_csv=''

if(len(sys.argv)>=4):
   for i in range (1,len(sys.argv),2):
     if(sys.argv[i]=="-t"):
        name_t=sys.argv[i+1]
     elif(sys.argv[i]=="-csv"):
        name_csv=sys.argv[i+1]
else:
      print("parameters: -t <file> адрес файла с исходным текстом (text file address), -csv <file> адрес файла результирующей таблицы (table file address)")
      sys.exit()

if((len(name_t)==0)|(len(name_csv)==0)):
      print("parameters: -t <file> адрес файла с исходным текстом (text file address), -csv <file> адрес файла результирующей таблицы (table file address)")
      sys.exit()

#ТЕКСТ В ФОРМАТЕ UTF-8
with open(name_t,'r') as f:
  text = f.readlines()

# Load model and tokenizer
#tokenizer = AutoTokenizer.from_pretrained("Babelscape/mrebel-large", src_lang="en_XX", tgt_lang="tp_XX")
tokenizer = AutoTokenizer.from_pretrained("Babelscape/mrebel-large", src_lang="ru_RU", tgt_lang="tp_XX")
# Here we set English ("en_XX") as source language. To change the source language swap the first token of the input for your desired language or change to supported language. For catalan ("ca_XX") or greek ("el_EL") (not included in mBART pretraining) you need a workaround:
# tokenizer._src_lang = "ca_XX"
# tokenizer.cur_lang_code_id = tokenizer.convert_tokens_to_ids("ca_XX")
# tokenizer.set_src_lang_special_tokens("ca_XX")
model = AutoModelForSeq2SeqLM.from_pretrained("Babelscape/mrebel-large")
gen_kwargs = {
    #"max_length": 256,
    "length_penalty": 0,
    "num_beams": 3,
    "num_return_sequences": 3,
    "forced_bos_token_id": None,
}

#разбиение текста на предложения
model_inputs_razd=[]
for textline in text:
     model_inputs_razd.extend(list(sentenize(textline)))

#получение результатов работы нейросети в виде списка из пар "номер извлечения"+"извлеченная строка в необработанном виде" и исходного предложения после всех извлечений из него
mREBEL_rez_list=[]# множество групп строк по 2*число извлечений +1 (исходное предложение): номер(0)+текст с триплетами, номер(1)+текст с триплетами, номер(2)+текст с триплетами ... и предложение

for substrtext_sent in model_inputs_razd :
  if(len(substrtext_sent.text)>0):
    #три строки из предложенного авторами модели mREBEL примера использования
    #model_inputs = tokenizer(substrtext_sent.text, max_length=256, padding=True, truncation=True, return_tensors = 'pt')
    model_inputs = tokenizer(substrtext_sent.text, truncation=True, return_tensors = 'pt')
    # Generate
    generated_tokens = model.generate( model_inputs["input_ids"].to(model.device), attention_mask=model_inputs["attention_mask"].to(model.device), decoder_start_token_id = tokenizer.convert_tokens_to_ids("tp_XX"),  **gen_kwargs,)
    # Extract text
    decoded_preds = tokenizer.batch_decode(generated_tokens, skip_special_tokens=False)

    for idx, sentence in enumerate(decoded_preds):
       mREBEL_rez_list.append(str(idx))
       mREBEL_rez_list.append(sentence)
    mREBEL_rez_list.append(substrtext_sent.text)


def normalize_NP(np_src,py2_morph): # исправлено имя локальной переменной в соответствии с именем параметра
  ind=0
  ind2=0
  taggen=''
  for ind  in range(len(np_src)):
       p2=py2_morph.parse(np_src[ind])[0]
       if  ((p2.tag.POS=='ADJF')|(p2.tag.POS=='ADJS')|(p2.tag.POS== 'PRTF')|(p2.tag.POS== 'PRTS')):#прилагательное или причастие, полное/краткое
           np_src[ind]=p2.inflect({'sing', 'nomn'}).word
       elif  (p2.tag.POS=='NPRO'):
           if (p2.tag.person==None):
             tempword = p2.inflect({'sing', 'nomn'})
             if (not (tempword==None)):
                np_src[ind]=tempword.word
             else:
                np_src[ind]=py2_morph.normal_forms(p2.word)[0]
       elif (p2.tag.POS=='NOUN'):
           taggen=p2.tag.gender
           ind2=ind
           tempword=p2.inflect({'sing', 'nomn'})
           if (not (tempword==None)):
             np_src[ind]=tempword.word
           break
       else: np_src[ind]= py2_morph.normal_forms(p2.word)[0]

  if ((taggen=='masc')|(taggen=='femn')|(taggen=='neut')):
    for ind in range(0,ind2):
      p2=py2_morph.parse(np_src[ind])[0]
      if  ((p2.tag.POS=='ADJF')|(p2.tag.POS=='ADJS')|(p2.tag.POS== 'PRTF')|(p2.tag.POS== 'PRTS')):
        tempword=p2.inflect({taggen, 'sing', 'nomn'}).word
        if (not (tempword==None)):
          np_src[ind]=tempword
    tail_only_adj=0
    for ind in range(ind2+1,len(np_src)):
      p2=py2_morph.parse(np_src[ind])[0] # исправлена отсутствовавшая строка
      if ((p2.tag.POS!='ADJF')&(p2.tag.POS!='ADJS')&(p2.tag.POS!= 'PRTF')&(p2.tag.POS!= 'PRTS')):
        tail_only_adj=1
        break
    if (tail_only_adj==0):#если это "лилия белая"
        for ind in range(ind2,len(np_src)):
               p2=py2_morph.parse(np_src[ind])[0]
               if  ((p2.tag.POS=='ADJF')|(p2.tag.POS=='ADJS')|(p2.tag.POS== 'PRTF')|(p2.tag.POS== 'PRTS')):
                  tempword=p2.inflect({taggen, 'sing', 'nomn'}).word
                  if (not (tempword==None)):
                      np_src[ind]= tempword

  return np_src


roles = dict({'instance of':'экземпляр','parent taxon':'вид','subclass of':'вид','part of':'часть','facet of':'аспект', 
              #в видах отношений в строке выше в результатах работы mREBEL главный термин стоит вторым, исправление порядка терминов для них выполняется в функции extract_triplets_typed, адаптированные имена ролей выбраны для правильного порядка терминов
              'has cause':'следствие','has quality':'параметр','use':'использование','used by':'использующее','item operated':'используемый объект',
              'opposite of':'противоположность','different from':'различие',
              'described by source':'источник описания','main subject':'описываемый объект','main regulatory text':'нормативный текст','standards body':'стандартизирующий орган',
              'made from material':'материал','manufacturer':'изготовитель','fabrication method':'метод изготовления',
              'connects with':'соединение с', 'contains':'содержимое', 'location':'местоположение',
              'studies':'объект исследования','influenced by':'источник влияния','industry':'отрасль','field of this occupation':'область профессии'      })

relations_with_reversed_order=["part of","subclass of","instance of","parent taxon","facet of"]#виды отношений, для которых нужно исправлять порядок главного и подчиненного терминов


def separate_word_normalize(word_list_src,pm2_morph): # новая функция получения по списку слов списка их нормальных форм
  word_list_norm=[]
  for ind  in range(len(word_list_src)):
    word_list_norm.append(pm2_morph.parse(word_list_src[ind])[0].normal_form)  # [0] - первый вариант морфологического разбора от морф. анализатора
  return word_list_norm

def check_for_nonexistent_words(wordsplit1, wordsplit2, substrtext_sent, py2_morph): # новая функция проверки наличия искажений в извлеченных моделью терминах (извлечение слова, которого не было в исходном тексте), возвращающая true/false
  no_nonexistent_words_flag=True
  substrtext_sent_split=[_.text.strip() for _ in list(tokenize(substrtext_sent.strip()))]

  for ws1_w in wordsplit1:  # проверка первого термина на искажения
    if ws1_w not in substrtext_sent_split:
      no_nonexistent_words_flag=False
      break

  if no_nonexistent_words_flag: # если нет искажений в первом - проверка второго термина
    for ws2_w in wordsplit2:
      if ws2_w not in substrtext_sent_split:
        no_nonexistent_words_flag=False
        break

  wordsplit1_byword=separate_word_normalize(wordsplit1,py2_morph) # получение списков слов в начальной форме
  wordsplit2_byword=separate_word_normalize(wordsplit2,py2_morph)

  if not no_nonexistent_words_flag: # если искажения - уточнение, не просто ли это различие формы слова при генерации моделью выходного текста
    no_nonexistent_words_flag=True
    substrtext_sent_split = separate_word_normalize(substrtext_sent_split,py2_morph)

    for ws1_w in wordsplit1_byword:  # проверка первого термина (после пословной нормализации) на искажения
      if ws1_w not in substrtext_sent_split:
        no_nonexistent_words_flag=False
        break

    if no_nonexistent_words_flag: # если нет искажений в первом - проверка второго термина (после пословной нормализации)
      for ws2_w in wordsplit2_byword:
        if ws2_w not in substrtext_sent_split:
          no_nonexistent_words_flag=False
          break

  return no_nonexistent_words_flag # флаг будет False только при нахождении искажений при обеих проверках.

#основано на предоставленной авторами модели mREBEL функции, преобразующей строку на выходе нейросети в словарь элементов-результатов (https://huggingface.co/Babelscape/mrebel-large)
def extract_triplets_typed(text,substrtext_sent,df_csv_receiver_table,extracted_seq_num,py2_morph): # добавлен параметр, соответствующий морфологическому анализатору
    relation = ''
    text = text.strip()
    current = 'x'
    subject, relation, object_, object_type, subject_type = '','','','',''

    for token in text.replace("<s>", "").replace("<pad>", "").replace("</s>", "").replace("tp_XX", "").replace("__en__", "").replace("__ru__", "").split():
        if token == "<triplet>" or token == "<relation>":
            current = 't'
            if relation != '':
                #начало дополнения
                wordsplit1=[_.text.strip() for _ in list(tokenize(subject.strip()))]
                wordsplit2=[_.text.strip() for _ in list(tokenize(object_.strip()))]

                if (check_for_nonexistent_words(wordsplit1, wordsplit2, substrtext_sent, py2_morph)): # проверка на наличие искажений в терминах при извлечении моделью. True при отсутствии искажений.

                  wordsplit1=normalize_NP(wordsplit1,py2_morph)
                  s1=' '.join(wordsplit1)
                  wordsplit2=normalize_NP(wordsplit2,py2_morph)
                  s2=' '.join(wordsplit2)

                  relnamesrc= relation.strip()
                  #if((relnamesrc=="part of")|(relnamesrc=="subclass of")|(relnamesrc=="instance of")|(relnamesrc=="parent taxon")|(relnamesrc=="facet of")): #определенные виды отношений, требующие изменения порядка терминов
                  if (relnamesrc in relations_with_reversed_order):
                    role2= roles.get(relnamesrc,relnamesrc)
                    s1,s2=s2,s1
                  else: role2= roles.get(relnamesrc,relnamesrc) #если для данного вида отношения нет адаптированной на русский роли, то оно не переименовывается

                  checkrepeats=df_csv_receiver_table[( df_csv_receiver_table['SubRole']==role2 )&(df_csv_receiver_table['MainTerm']==s1)&( df_csv_receiver_table['SubTerm']==s2)]
                  if not(checkrepeats.empty):
                    df_csv_receiver_table['SrcFragment'][list(checkrepeats.index.values)[0]]=df_csv_receiver_table['SrcFragment'][list(checkrepeats.index.values)[0]]+';_; '+substrtext_sent
                    df_csv_receiver_table['ExtractedSeqNum'][list(checkrepeats.index.values)[0]]=df_csv_receiver_table['ExtractedSeqNum'][list(checkrepeats.index.values)[0]]+';_; '+extracted_seq_num
                  else:
                    if((s1.upper().isupper())&(s2.upper().isupper())&(s1!=s2)):#результаты с терминами, не содержащими букв, и с отношениям между двумя одинаковыми терминами (а - отношение - а) отбрасываются
                      df_csv_receiver_table.loc[len(df_csv_receiver_table)]=[s1,role2,s2,substrtext_sent,extracted_seq_num]
                #конец дополнения

                relation = ''
            subject = ''
        elif token.startswith("<") and token.endswith(">"):
            if current == 't' or current == 'o':
                current = 's'
                #if relation != '':
                    #triplets.append({'head': subject.strip(), 'head_type': subject_type, 'type': relation.strip(),'tail': object_.strip(), 'tail_type': object_type})
                object_ = ''
                subject_type = token[1:-1]
            else:
                current = 'o'
                object_type = token[1:-1]
                relation = ''
        else:
            if current == 't':
                subject += ' ' + token
            elif current == 's':
                object_ += ' ' + token
            elif current == 'o':
                relation += ' ' + token
    if subject != '' and relation != '' and object_ != '' and object_type != '' and subject_type != '':
        #начало дополнения
        wordsplit1=[_.text.strip() for _ in list(tokenize(subject.strip()))]
        wordsplit2=[_.text.strip() for _ in list(tokenize(object_.strip()))]

        if (check_for_nonexistent_words(wordsplit1, wordsplit2, substrtext_sent, py2_morph)): # проверка на наличие искажений в терминах при извлечении моделью. True при отсутствии искажений.

          wordsplit1=normalize_NP(wordsplit1,py2_morph)
          s1=' '.join(wordsplit1)
          wordsplit2=normalize_NP(wordsplit2,py2_morph)
          s2=' '.join(wordsplit2)

          relnamesrc= relation.strip()
          if (relnamesrc in relations_with_reversed_order):
            role2=roles.get(relnamesrc,relnamesrc)
            s1,s2=s2,s1
          else: role2= roles.get(relnamesrc,relnamesrc)

          checkrepeats=df_csv_receiver_table[( df_csv_receiver_table['SubRole']==role2 )&(df_csv_receiver_table['MainTerm']==s1)&( df_csv_receiver_table['SubTerm']==s2)]
          if not(checkrepeats.empty):
            df_csv_receiver_table['SrcFragment'][list(checkrepeats.index.values)[0]]=df_csv_receiver_table['SrcFragment'][list(checkrepeats.index.values)[0]]+';_; '+substrtext_sent
            df_csv_receiver_table['ExtractedSeqNum'][list(checkrepeats.index.values)[0]]=df_csv_receiver_table['ExtractedSeqNum'][list(checkrepeats.index.values)[0]]+';_; '+extracted_seq_num
          else:
            if((s1.upper().isupper())&(s2.upper().isupper())&(s1!=s2)):
              df_csv_receiver_table.loc[len(df_csv_receiver_table)]=[s1,role2,s2,substrtext_sent,extracted_seq_num]
           #конец дополнения


df_csv = pd.DataFrame(columns=['MainTerm','SubRole','SubTerm','SrcFragment','ExtractedSeqNum'])

#получение из строк-результатов извлечения нейросетью отдельных пар терминов и отношений и занесение в таблицу. Для каждого предложения предполагается ТРИ извлечения. 
#Предполагается структура списка результатов в группах по 7 вида ("номер извлечения(idx)"+"извлечение(sentence)") * 3 + "исходное предложение(orig_line)"
for i in range(0,len(mREBEL_rez_list),7):
  idx=mREBEL_rez_list[i]
  sentence=mREBEL_rez_list[i+1]
  orig_line=mREBEL_rez_list[i+6]
  extract_triplets_typed(sentence,orig_line,df_csv,idx)
  idx=mREBEL_rez_list[i+2]
  sentence=mREBEL_rez_list[i+3]
  extract_triplets_typed(sentence,orig_line,df_csv,idx)
  idx=mREBEL_rez_list[i+4]
  sentence=mREBEL_rez_list[i+5]
  extract_triplets_typed(sentence,orig_line,df_csv,idx)

df_csv.to_csv(name_csv,index=False)

