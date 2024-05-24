import pandas as pd
import types
from owlready2 import *

name_csv=''
name_owl=''

if(len(sys.argv)>=4):
   for i in range (1,len(sys.argv),2):
     if(sys.argv[i]=="-csv"):
        name_csv=sys.argv[i+1]
     elif(sys.argv[i]=="-owl"):
        name_owl=sys.argv[i+1]
     elif(sys.argv[i]=="-h"):
        print("parameters: -csv <file> : table file address, -owl <file> : ontology file address")
        sys.exit()
else:
      print("parameters: -csv <file> : table file address, -owl <file> : ontology file address")
      sys.exit()

if((len(name_owl)==0)|(len(name_csv)==0)):
      print("parameters: -csv <file> : table file address, -owl <file> : ontology file address")
      sys.exit()


csv_table=pd.read_csv(name_csv)
csv_table=csv_table.drop_duplicates(subset=['MainTerm', 'SubRole','SubTerm'])
#create or load ontology (file name becomes iri) (if ontology with that name already exists adds to it instead of overwriting regardless of if get_ontology or get_ontology(..).load() was used )
onto=get_ontology(name_owl)

reltypes=set(list(csv_table['SubRole']))
reltypes.discard('вид')
reltypes.discard('экземпляр')

tclasses=set(list(csv_table['MainTerm']))
tclasses.update(list(csv_table['SubTerm']))#множество терминов, являющихся кандидатами в классы (все термины)

s1_instance=csv_table[(csv_table['SubRole']=="экземпляр")]
tinstances=set(list(s1_instance['SubTerm']))#множество терминов, являющихся экземплярами (подчиненные в отношениях "экземпляр")

#проверка наличия у кандидатов в экземпляры отношений "род-вид" или других отношений "класс-экземпляр" где они являются классами, а не экземплярами (экземпляр не имеет родовидовых отношений или собственных экземпляров)
#в случае наличия недопустимых отношений - рассматривается как класс, в случае отсутствия - как экземпляр 
for i in tinstances:
  trelations_of_instance=csv_table[(csv_table['MainTerm']==i) |  ((csv_table['SubTerm']==i)&(csv_table['SubRole']!="экземпляр"))]
  roi_relations=set(list(trelations_of_instance['SubRole']))
  if (("вид" in roi_relations) | ("экземпляр" in roi_relations)):
     tinstances.discard(i)
  else:
     roi_classes=set(list(trelations_of_instance['MainTerm']))
     roi_classes.update(list(trelations_of_instance['SubTerm']))
     roi_classes.discard(i)
     can_i_be_instance=1
     for c_or_i in roi_classes:
         if (c_or_i not in tinstances):
            tinstances.discard(i) #не может быть экземпляром
            t_roi_whose_instance=csv_table[(csv_table['SubTerm']==i)&(csv_table['SubRole']=="экземпляр")]
            roi_whose_instance=set(list(s1_instance['MainTerm']))
            for mt in roi_whose_instance:
                csv_table.loc[len(csv_table)]=[mt,"вид",i]
            can_i_be_instance=0
            break
     if (can_i_be_instance):
        tclasses.discard(i) #точно экземпляр


with onto:
  #шаг 1 - все классы добавляются в онтологию без указания надклассов, для получения всех соотвествующих объектов
  for cl in list(tclasses):
    types.new_class(cl.replace(' ','_'), (Thing,))#без указания надкласса не сохраняется, поэтому на этом шаге для всех классов указывается единственный общий надкласс Thing

  for cl in list(tclasses):
    #шаг 2 - для каждого класса получение списка надклассов
    s1_subclass=csv_table[(csv_table['SubTerm']==cl)&(csv_table['SubRole']=="вид")]
    cl_superclasses=list( set(list(s1_subclass['MainTerm'])) )

    #=для каждого класса получение списка объектов-надклассов по именам
    cl_superclass_onto=[]
    for supercl in  cl_superclasses:
       cl_superclass_onto.append(onto[supercl.replace(' ','_')])
    #пересоздание класса с тем же именем, но с указанием всех прямых надклассов
    types.new_class(cl.replace(' ','_'), tuple(cl_superclass_onto))

    #шаг 3 - для каждого класса получение списка прочих отношений помимо род-вид и класс-экземпляр, в которых этот класс является главным термином
    s1_rel=csv_table[(csv_table['MainTerm']==cl)&(csv_table['SubRole']!="вид")&(csv_table['SubRole']!="экземпляр")] 
    for subterm_rel in zip(s1_rel['SubTerm'],s1_rel['SubRole']):
       #добавление для каждого экземпляра отношения отдельного особого вида свойства в онтологии по схеме <данный главный класс-термин>+"имеет"+<роль - вид отношения>+<подчиненный класс-термин>
       spec_rel= types.new_class(cl.replace(' ','_')+'_имеет_'+subterm_rel[1].replace(' ','_')+'_'+subterm_rel[0].replace(' ','_'),(ObjectProperty,) )
       spec_rel.set_domain([onto[cl.replace(' ','_')]])
       spec_rel.set_range([onto[subterm_rel[0].replace(' ','_')]])

  for inst in list(tinstances):
     t_whose_instance=csv_table[(csv_table['SubTerm']==inst)&(csv_table['SubRole']=="экземпляр")]
     whose_instance=(list(set(list(t_whose_instance['MainTerm']))))
     for cl_whose_inst in  whose_instance:
        #шаг 4 добавление каждого экземпляра как объекта соответствующего класса по конструктору(класса-элемента онтологии). При множественном наследовании добавляется несколько раз для каждого класса, автоматически объединяется в результирующем элементе онтологии
        whose_instance_onto=onto[cl_whose_inst.replace(' ','_')]
        whose_instance_onto(inst.replace(' ','_'))


  #шаг 5 - для каждого экземпляра - получение списка прочих отношений помимо "класс-экземпляр" и добавление аналогично отношениям классов
  for inst in list(tinstances):
     inst1_rel=csv_table[(csv_table['MainTerm']==inst)&(csv_table['SubRole']!="вид")&(csv_table['SubRole']!="экземпляр")] 
     for subinst_rel in zip(inst1_rel['SubTerm'],inst1_rel['SubRole']):
       spec_rel= types.new_class(inst.replace(' ','_')+'_имеет_'+subinst_rel[1].replace(' ','_')+'_'+subinst_rel[0].replace(' ','_'),(ObjectProperty,) ) 
       spec_rel.set_domain([onto[inst.replace(' ','_')]])
       spec_rel.set_range([onto[subinst_rel[0].replace(' ','_')]])
       getattr(onto[inst.replace(' ','_')],spec_rel.name).append(onto[subinst_rel[0].replace(' ','_')])


onto.save(file = name_owl, format = "rdfxml")