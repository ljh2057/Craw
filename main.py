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


if __name__ == '__main__':
   plugin_dir='/Users/macbookair/Plugin_project/plugins'
   plgs=getAllPlugin(plugin_dir)
   print(plgs)
   newfilepath,newpropath='F:\\newfilepath','E:\\newpropath'
   plg_info=call_plugin(plgs[0],'getParameters',filepath=newfilepath,propath=newpropath)
   print(plg_info)


   # cnki = Cnki.Craw_cnki('c:\\1','stop','none')
   # print(cnki.getParameters())
   # from threading import Thread, Lock
   # # 创建一个互斥锁
   # mutex1 = Lock()
   # mutex2 = Lock()
   # mutex3 = Lock()
   # def fun1():
   #      mutex1.acquire()# 阻塞
   #      print("线程1 执行")
   #      mutex2.release()# 释放锁2，让线程2继续执行
   # def fun2():
   #      mutex2.acquire()# 阻塞
   #      print("线程2 执行")
   #      mutex3.release()# 释放锁3，让线程3继续执行
   # def fun3():
   #      mutex3.acquire()# 阻塞
   #      print("线程3 执行")
   #      mutex1.release()# 释放锁1，让线程1继续执行
   # # 创建一个线程对象
   # t1 = Thread(target=fun1)
   # t2 = Thread(target=fun2)
   # t3 = Thread(target=fun3)
   # mutex2.acquire()
   # mutex3.acquire()
   # t1.start()
   # t2.start()
   # t3.start()
   # t1.join()
   # t2.join()
   # t3.join()

