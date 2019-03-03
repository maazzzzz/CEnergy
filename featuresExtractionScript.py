import os
import re
from collections import Iterable
import sys
import csv


class Node:
    def __init__(self):
        self.id=-1
        self.pred=[]
        self.succ=[]
        self.startline=-2
        self.endline=-2
        self.executed=0
        self.predicate=0
        self.decision=0
    def display(self):
        print self.id, "pred:",self.pred,"-----succ:",self.succ,"-----start:",self.startline,"-----end:",self.endline
    def getStr(self):
        predstr= ','.join(map(str, self.pred))
        succstr=','.join(map(str, self.succ))
        temp="ID:"+str(self.id)+"|succ:"+succstr+"|pred:"+predstr+"|start:"+str(self.startline)+"|End:"+str(self.endline)+"\n"
        return temp
class Loop:
    def __init__(self):
        self.id=-2
        self.header=-2
        self.latch=[]
        self.depth=-2
        self.outer=-2
        self.nodeIds=[]
        
class Graph:
    def __init__(self):
        self.nodes=[]
        self.func=None
        self.file=None
        self.loopcount=-2
        self.loops=[]
    def display(self):
            print self.func
            for x in self.nodes:
                x.display()
    def getStr(self):
        temp="Function: "+self.func+"|"+"Filename: "+self.file+"\n"  
        for x in self.nodes:
            temp+=x.getStr()
        return temp

def flatten(lis):
    for item in lis:
        if isinstance(item, Iterable) and not isinstance(item, basestring):
            for x in flatten(item):
                yield x
        else:
            yield item


def getfiles(path, types):
    """Get list of files available at a given path
      types: a list of possible files to extract, it can be any type.
      Example: getfiles('/tmp/',['.txt','.cpp','.m']); 
    
    """
    check_path(path)
    imlist = []
    for filename in os.listdir(path):
        if os.path.splitext(filename)[1].lower() in types:
            imlist.append(os.path.join(path, filename))

    return imlist


def check_path(fname, message=''):
    """ Function check for the validity of path (existence of file or directory path),
    if not found raise exception"""
    if len(message) == 0:
        message = 'path ' + fname + ' Not found'
    if not os.path.exists(fname):
        print message
        raise ValueError(message)


def get_dirs(path='./'):
    directories=os.listdir(path)
    directories=sorted(directories)

    dirs=[]

    for dir in directories:
        if(dir.find('.py')>0 or dir.find('.csv')>0 or dir.find('_blowfish_d')>0) :
            pass
        else:
            dirs.append(dir)

    return dirs




def writeGraphToFile(fileGraphArray):
    f=open(fileGraphArray[0].file+".static.txt",'w')
    for g in fileGraphArray:
        f.write(g.getStr())
    f.close()
    
def readGraphFromFile(filename):
    f=open(filename+".static.txt",'r').read().rsplit('\n')
    

def extractGraphs(cfgFileName,path):
    sfile=(open(path+cfgFileName,'r')).read()
    lines=sfile.rsplit('\n')
    for x in lines:
        if  x==";; ":
            lines.remove(x)

    fname=cfgFileName.rsplit('.011')[0]
    
    k=len(lines)
    i=0
    skip=False
    graphs=[]
    currentGraph=None
    while i<k:
        if "Function" in lines[i]:
            if "<unset-asm-name>" not in lines[i] and "GLOBAL" not in lines[i] and " atoi " not in lines[i] and " atof " not in lines[i]:#condition for rooting out library functions
#                 print 'Ok'
                temp=lines[i].rsplit(" ")
                currentGraph=Graph()
                currentGraph.file=fname
                currentGraph.func=temp[2]
                graphs.append(currentGraph)
                i+=1
                skip=False
            else:
                skip=True

        if skip !=True and 'Removing'  not in lines[i] and "Merging" not in lines[i] and currentGraph!=None:

            if "loops found" in lines[i]:
                temp=lines[i].rsplit(' ')
                currentGraph.loopcount=int(temp[1])
                i+=2
                j=0
                while j<currentGraph.loopcount :
                    if "Loop" in lines[i]:
                        temp=lines[i].rsplit(' ')
                        tempLoop=Loop()
                        tempLoop.id=temp[2]# loop id
                        i+=1
                        temp=lines[i].rsplit(" ")
                        tempLoop.header=temp[3]# loop header
                        if 'multiple' not in temp:
                            tempLoop.latch.append(temp[5])
                        else:
                            tempLoop.latch=temp[6:]
#                             print temp
                        i+=1
                        temp=lines[i].rsplit(' ')
                        tempLoop.depth=temp[3]
                        tempLoop.outer=temp[5]
                        i+=1
                        temp=lines[i].rsplit(" ")
                        tempLoop.nodeIDs=temp[3:]
                        i+=2

                    currentGraph.loops.append(tempLoop)
                    j+=1
            if "basic block" in lines[i]:
                tempNode=Node()
                temp=lines[i].rsplit(' ')
                tempNode.id=temp[5]
                currentGraph.nodes.append(tempNode)
                i+=1
                if "pred" in lines[i] :
                    temp=lines[i].rsplit(' ')
                    i+=1
                    tempNode.pred.append(temp[11])# first pred
                    while("starting" not in lines[i] and len(lines[i].rsplit(' ')) ==17   ):# extra pred
                            temp=lines[i].rsplit(' ')
                            tempNode.pred.append(temp[16])
                            i+=1
                if("starting" in lines[i]):           
                    temp=lines[i].rsplit(' ')
                    tempNode.startline=temp[6]
                i+=1
                while ('succ' not in lines[i]):
                    i+=1

                temp=lines[i].rsplit(' ')
                if len(temp)==12:
                    tempNode.succ.append(temp[11])# first succ
                else:
                    tempNode.succ.append("ERROR")
                tempIdx=i
                i+=1
                while(';;' in lines[i] and len(lines[i].rsplit(' '))==17):# extra succ
                    temp=lines[i].rsplit(' ')
                    tempNode.succ.append(temp[16])
                    i+=1
                while(currentGraph.file not in lines[tempIdx]):
                    tempIdx-=1
                temp=lines[tempIdx].rsplit(':')
                tempNode.endline=temp[1]
                if(" if " in lines[tempIdx]): #predicate node
                    tempNode.predicate=1
                if len(tempNode.succ)>1: #decision node
                    tempNode.decision=1
        i+=1
    return graphs

#One graph obj=One Function of cfg
def cfg_to_gcov(graphs,gcov1): 
    gcov_graphs=[]
    for graph in graphs:
        temp_graph=Graph()
        temp_node=Node()
        print "Graph: ",graph.func
        i=0
        for i in range(0,len(graph.nodes),1): 
            node=graph.nodes[i]
            sl=node.startline
            el=node.endline
            if(type(sl)==int and sl<0):
                pass
            elif(sl.find('-')==-1):
                sl=sl.replace(',','')
                el=el.replace(',','')
                sl=" "+sl
                el=" "+el
                idx_start=gcov1.find(str(sl)+':')
                idx_fin=gcov1.find(str(el)+':')
                if(int(idx_fin)==int(idx_start)):
                    run_count=gcov1[int(idx_start)-4:int(idx_start)-3]
                    if(run_count.isdigit()):
                        # print "ID: ",node.id
                        run_count=int(run_count)
                        temp_node.id=node.id
                        temp_node.succ=node.succ
                        temp_node.pred=node.pred
                        temp_node.startline=sl
                        temp_node.endline=el
                        temp_node.executed=1
                        temp_node.predicate=node.predicate
                        temp_node.decision=node.decision
                        temp_graph.nodes.append(temp_node)
                        temp_node=Node()
                else:
                    s=gcov1[int(idx_start)-5:int(idx_fin)+5]
                    lines=s.split('\n')
                #     print lines
                    start=int(sl)  #Starting Line Number of Node
                    for line in lines:
                        idx=line.find(" "+str(start))
                        if((line[idx-4:idx-3]).isdigit()):
                            # print "ID: ",node.id
                            temp_node.id=node.id
                            temp_node.succ=node.succ
                            temp_node.pred=node.pred
                            temp_node.startline=sl
                            temp_node.endline=el
                            temp_node.executed=1
                            temp_node.predicate=node.predicate
                            temp_node.decision=node.decision
                            temp_graph.nodes.append(temp_node)
                            temp_node=Node()
                            break
                        start+=1
        temp_graph.func=graph.func
        
        
        #Loops
        cnt=0
        temp_loop=Loop()
        for loop in graph.loops:
            cnt=0
            if(loop.id!='0'):
                for node in temp_graph.nodes:
                    if(node.id==loop.header):
                        cnt+=1
                    if(node.id.replace(',','') in loop.latch):
                        cnt+=1
            if(cnt==len(loop.latch)+1):
                temp_loop=loop
                temp_graph.loops.append(temp_loop)    
               
        gcov_graphs.append(temp_graph)
    return gcov_graphs
def feats2(graphs):
    pred=0
    dec=0
    for graph in graphs:
        for x in graph.nodes:
            if(x.predicate==1):
                pred+=1
            if(x.decision==1):
                dec+=1
    return pred,dec        

def feats(graphs):
    edges=[]
    nodes=[]
    exits=[]
    cc=[]
    loop_count=0
    for graph in graphs:
        nodes.append(len(graph.nodes))
#         print graph.func,len(graph.nodes)
        tsucc=[]
        for node in graph.nodes:
            succ=node.succ
            tsucc.append(succ)
        edges.append(list(flatten(tsucc)))
        loop_count+=len(graph.loops)
        
    edge_count=0
    for edge in edges:
        exit_count=0
        for val in edge:
            if(val=='EXIT'):
                exit_count+=1
            edge_count+=1
        exits.append(exit_count)
    
        
    i=0
    
    for i in range(0,len(nodes),1):
        temp=len(edges[i])-nodes[i]+(2*exits[i]) #Edges-Nodes+2*ExitNodes
        cc.append(temp)
    
#     print "Nodes: ",sum(nodes)
#     print "Edges: ",edge_count
#     print "Loops: ",loop_count
#     print "-------------------"
    return sum(nodes),edge_count,sum(cc)/len(cc),loop_count







def main():
    name='data_features2.csv'
    ofile=open(name,'w')
    ofile.write('Name;Iter;Decision;Predicates\n')
    
    names=open(sys.argv[1])
    for line in names:
        l=line.split(',')

    print l
    for fname in l: #Every folder
        cfg_graphs=[]
        #Generating graphs from cfgs
        cfgs=getfiles(fname,['.cfg'])
        names=[]
        
        for cfg in cfgs:
    #         print "INDEX: ",cfg,index
            cfg=cfg.split('/')
            cfg_graphs.append(extractGraphs(cfg[1],cfg[0]+'/'))
            temp=cfg[1].split('.')
            names.append(temp[0]+'.'+temp[1])
            
        
        if(fname=='security_blowfish_d'):
            iters=get_dirs(fname+'/Data_d')
        else:
            iters=get_dirs(fname+'/Data')
        for it in iters:
            if(fname=='security_blowfish_d'):
	            gcovs=getfiles(fname+'/Data_d/'+it,['.gcov'])
            else:
                gcovs=getfiles(fname+'/Data/'+it,['.gcov'])
            gcov_graphs=[] #Gcov Graphs of one iteraion
            for gcov in gcovs:
                gn=gcov.split('/')[3]
    #             print gcov
                try:
                    idx=names.index(gn.split('.gcov')[0])
    #                 print idx
                    gcov1=(open(gcov,'r')).read()
                    gcov_graphs.append(cfg_to_gcov(cfg_graphs[idx],gcov1))
                except:
                    pass
            
            #Features of Gcov graphs of one iteraion
            print "Iter: ",it
            predC=0
            decC=0
            nodes=0
            edges=0
            compl=0 
            loops=0
            index=0
            for graph in gcov_graphs:
                nc,ecount,cc,lc=feats(graph)
                nodes+=nc
                edges+=ecount
                compl+=cc
                loops+=lc
                index+=1
                pc,dc=feats2(graph)
                predC+=pc
                decC+=dc
                
            
            
            write=fname+";"+it+";"+str(decC)+";"+str(predC)+"\n"
            ofile.write(write)
            print fname    
            print decC,predC
            print "________________________________________"

    ofile.close()


main()

