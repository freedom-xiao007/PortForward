# TCP 端口转发--远程调试
***
## 简单介绍
&ensp;&ensp;&ensp;&ensp;刚开始使用SSH端口转发时，非常不顺利，达不到一些自己想要的效果，于是用自己TCP实现一个简单的端口转发。

## 使用场景
### 内网穿透--访问内网机器
&ensp;&ensp;&ensp;&ensp;用网上的一个经典的场景吧，在学校里有你自己的电脑A，放假的时候你先要访问学校里面的电脑A进行一些操作，由于没有开放的端口和公网IP你是无法访问电脑A的。如果你想要想要访问电脑A，需要一台有公网的电脑或服务器，这里设定你有一台云服务器B，使用内网穿透你就可以通过任意一台电脑C去访问电脑A。
&ensp;&ensp;&ensp;&ensp;场景电脑概述：

- 机器A：位于学校内网中，没有开放的端口，B、C无法访问
- 机器B：云服务器，具有公网IP，A、C都可以访问到
- 机器C：家里的电脑，想要去连接A，可以访问B

### 端口转发
&ensp;&ensp;&ensp;&ensp;比如你在局域网其中一台有一个web服务器，它的接口只有相同局域网的机器才能访问，但由于种种不知名的原因，你在另外一个局域网，你不能直接访问这个web接口。但你能访问其局域网内的另一台机器，此时使用端口转发就比较好。
&ensp;&ensp;&ensp;&ensp;场景电脑概述：

- 机器A:web服务器，没有外网开放端口，外网无法访问
- 机器B：与A在同一个局域网中，可以访问A，C可以登录B
- 机器C：与A、B不在同一个局域网，想要访问A的接口，可以访问机器B

## 安装与使用
### 下载运行
&ensp;&ensp;&ensp;&ensp;程序基于Python3编写，请使用Python3运行程序

&ensp;&ensp;&ensp;&ensp;客户端程序运行，有两种方式：
```angular2html
# 加载配置文件运行方式
python3 Client.py /home/conf/remote.cfg

# 直接传递参数运行方式:服务端IP、服务端端口、内网IP、内网端口
python3 Client.py serverIP serverPort connectIP connectPort
```

&ensp;&ensp;&ensp;&ensp;服务端程序运行：
```angular2html
# 直接传递参数方式：监听的端口
python3 Server.py port
```

### 内网穿透
&ensp;&ensp;&ensp;&ensp;使用上面的内网穿透场景：
- 机器A：位于学校内网中，没有开放的端口，B、C无法访问
- 机器B：云服务器，具有公网IP，A、C都可以访问到，设定IP：192.34.34.34，监听的端口为250吧
- 机器C：家里的电脑，想要去连接A，可以访问B

&ensp;&ensp;&ensp;&ensp;此时我们先在我们学校的机器A上运行客户端程序（Client.py），运行的命令如下（也可以采用配置文件方式）：
```angular2html
python3 Client.py 192.34.34.34 250 localhost 22
```
&ensp;&ensp;&ensp;&ensp;我们让其去连接云服务器，由于我们是要登录SSH，所以后面的参数设置连接机器A的本地的22端口

&ensp;&ensp;&ensp;&ensp;然后在服务器B上运行服务端（Server.py），监听在250端口
```angular2html
python3 Server.py 250
```

&ensp;&ensp;&ensp;&ensp;看到相应的连接成功提示即可：
```angular2html
# 客户端
[ 2018-08-29 20:36:05 ]:  Try connect server: 119.39.96.61 40006
[ 2018-08-29 20:36:05 ]:  Connect server successful

# 服务端
[ 2018-08-29 20:36:05 ]:  Server listen: localhost 40006
[ 2018-08-29 20:36:05 ]:  Receive accept data: b'#CLIENT'
[ 2018-08-29 20:36:05 ]:  Accept intranet client connect
[ 2018-08-29 20:36:05 ]:  Start intranet client listen
```

&ensp;&ensp;&ensp;&ensp;最后我们可以随便找一台机器C，使用SSH命令去连接即可：
```angular2html
ssh -p 250 user@192.34.34.34 
```

### 端口转发
&ensp;&ensp;&ensp;&ensp;使用上面的端口转发场景
- 机器A:web服务器，没有外网开放端口，外网无法访问
- 机器B：与A在同一个局域网中，可以访问A，C可以登录B，设定IP：192.34.34.34，监听的端口为250吧
- 机器C：与A、B不在同一个局域网，想要访问A的接口，可以访问机器B

&ensp;&ensp;&ensp;&ensp;此时我们先在机器A上运行客户端程序（Client.py），去连接机器B上的服务端和本地Web服务的9080端口，运行的命令如下（也可以采用配置文件方式）：
```angular2html
python3 Client.py 192.34.34.34 250 localhost 9080
```

&ensp;&ensp;&ensp;&ensp;然后在机器B上运行服务端（Server.py），监听在250端口
```angular2html
python3 Server.py 250
```

&ensp;&ensp;&ensp;&ensp;这样机器C就可以机器B的250端口访问调用机器A的Web接口了

## 参考链接
&ensp;&ensp;&ensp;&ensp;下面有一些比较好的参考资料，可以去看看，可以帮助更好的理解：
- [SSH协议交互过程:https://blog.csdn.net/kluleia/article/details/8179232](https://blog.csdn.net/kluleia/article/details/8179232)
- [玩转SSH端口转发:https://blog.fundebug.com/2017/04/24/ssh-port-forwarding/](https://blog.fundebug.com/2017/04/24/ssh-port-forwarding/)
- [SSH原理与运用（二）：远程操作与端口转发:http://www.ruanyifeng.com/blog/2011/12/ssh_port_forwarding.html](http://www.ruanyifeng.com/blog/2011/12/ssh_port_forwarding.html)
