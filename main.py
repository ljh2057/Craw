import os
import importlib
from keyword import iskeyword
import threading, queue,time

def call_plugin(p_name,method,state=None,text=None,filepath=None,propath=None):
    #package='plugins.'+p_name 根据路径引入对应的插件模块
    obj = importlib.import_module('.' + p_name, package='plugins.'+p_name)
    c = getattr(obj,p_name)
    obj = c(state,text,filepath,propath) # new class
    mtd = getattr(obj,method)
    return mtd()
def getAllPlugin(filepath):
    plg_ls=[]
    files=os.listdir(filepath)
    for f in files:
        #过滤_开头、关键字模块，且为文件夹
        if not f.startswith('_') and not iskeyword(f) and os.path.isdir(filepath+'/'+f):
            #判断插件主模块是否存在，即插件文件夹名.py文件是否存在
            if os.path.exists(filepath+'/'+f+'/'+f+'.py') and f!='BasePlugin':
                plg_ls.append(f)

    # print(plg_ls)
    # for f in files:
    #     if f.endswith('.py') and not f.startswith('_') and not iskeyword(f):
    #         # print(os.path.splitext(f)[0])
    #         plg_ls.append(os.path.splitext(f)[0])
    # plgs={}.fromkeys(plg_ls)
    # for plugin in plgs:
    #     # obj = __import__(plugin)  # import module (同级目录)
    #     #importlib.import_module导入一个模块。参数 name 指定了以绝对或相对导入方式导入什么模块 (比如要么像这样 pkg.mod 或者这样 ..mod)。如果参数 name 使用相对导入的方式来指定，那么那个参数 packages 必须设置为那个包名，这个包名作为解析这个包名的锚点 (比如 import_module('..mod', 'pkg.subpkg') 将会导入 pkg.mod)。
    #     obj =importlib.import_module('.'+plugin,package='plugins')
    #     c = getattr(obj, plugin)
    #     obj=c()
    #     r=re.compile('(?!__)')#匹配非__开头
    #     plgs[plugin]=list(filter(r.match, dir(obj)))#dir(obj)列出obj所有方法，返回list，python3中filter默认返回filter类
    # return plgs
    return plg_ls
def showInfo(plugin_info):
    pass
nums=3

def fun1(index,locks_list):
   # mutex1.acquire()
   locks_list[index].acquire()
   print("线程1 执行")
   for i in range(100):
       print('线程1%f' % i)
   # mutex2.release()
   if index+1==nums:
       locks_list[0].release()
   else:
       locks_list[index+1].release()


def fun2(index,locks_list):
   # mutex2.acquire()
   locks_list[index].acquire()

   print("线程2 执行")
   for i in range(100):
       print('线程2%f' % i)
   # mutex3.release()  # 释放锁3，让线程3继续执行
   if index+1==nums:
       locks_list[0].release()
   else:
       locks_list[index+1].release()


def fun3(index,locks_list):
   # mutex3.acquire()  # 阻塞
   locks_list[index].acquire()

   print("线程3 执行")
   for i in range(100):
       print('线程3%f' % i)
   if index + 1 == nums:
       locks_list[0].release()
   else:
       locks_list[index + 1].release()

if __name__ == '__main__':
   # plugin_dir='/Users/macbookair/Plugin_project/plugins'
   # plgs=getAllPlugin(plugin_dir)
   # print(plgs)
   # newfilepath,newpropath='F:\\newfilepath','E:\\newpropath'
   # plg_info=call_plugin(plgs[0],'getParameters',filepath=newfilepath,propath=newpropath)
   # print(plg_info)


   # cnki = Cnki.Craw_cnki('c:\\1','stop','none')
   # print(cnki.getParameters())
   from threading import Thread, Lock
   thread_list=[i for i in range(nums)]
   locks_list=[i for i in range(nums)]
   job_list=[fun1,fun2,fun3]
   # job_list.append()



   def initThreadandLock(index, locks_list,thread_list,job_list):
       locks_list[index] = Lock()
       if index:
           locks_list[index].acquire()
       thread_list[index] =Thread(target=job_list[index],args=(index,locks_list))




   # 创建一个互斥锁

   # mutex1 = Lock()
   # mutex2 = Lock()
   # mutex3 = Lock()
   # def fun1():
   #      mutex1.acquire()# 阻塞
   #      print("线程1 执行")
   #      for i in range(100):
   #          print('线程1%f'%i)
   #      mutex2.release()# 释放锁2，让线程2继续执行
   # def fun2():
   #      mutex2.acquire()# 阻塞
   #      print("线程2 执行")
   #      for i in range(100):
   #          print('线程2%f' % i)
   #      mutex3.release()# 释放锁3，让线程3继续执行
   # def fun3():
   #      mutex3.acquire()# 阻塞
   #      print("线程3 执行")
   #      for i in range(100):
   #          print('线程3%f' % i)
   #      mutex1.release()# 释放锁1，让线程1继续执行



   # 创建一个线程对象
   # t1 = Thread(target=fun1)
   # t2 = Thread(target=fun2)
   # t3 = Thread(target=fun3)
   # mutex1.acquire()
   # mutex2.acquire()
   # mutex3.acquire()
   # t1.start()

   # t2.start()
   # mutex3.release()
   # t3.start()
   # mutex1.release()

   # t1.join()
   # t2.join()
   # t3.join()
   for index in range(nums):
       initThreadandLock(index, locks_list, thread_list, job_list)
   # t1.join()
   print(locks_list)
   print(thread_list)
   print(job_list)

   for i in range(nums):
       thread_list[i].start()
   for i in range(nums):
       thread_list[i].join()

