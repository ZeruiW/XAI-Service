1. 使用装饰器，针对每个post request
    1. 响应时间来分析：complexity(calculate with time delay)计算操作复杂度：\
        使用 time 或 datetime 库来记录每次操作的执行时间。\
        使用 requests 库来处理 API 调用，进而计算 API 调用次数
        timeit: 用于测量代码执行时间的库，可以替代 time 和 datetime。
        aiohttp: 一个异步 HTTP 客户端/服务器库，可以用来处理 API 调用。
         - 监控网络延迟：网络延迟是服务间通信的主要瓶颈之一。您可以监控服务间的请求和响应时间，找出高延迟的服务。Python 的 requests 库可以帮助您记录请求的时间

    2 radon: Radon is a Python library that computes various code metrics, including Cyclomatic Complexity, Halstead metrics, Maintainability Index, and Lines of Code. 
 
    3 要记录 microservice 使用和占用的计算资源，您可以监控以下指标：

CPU 使用率
内存使用率
磁盘 I/O
网络 I/O
对于 Python 应用程序，您可以使用 psutil 库来收集这些指标。首先，需要安装 psutil：
对于每个 POST 请求的情况，如果您使用 Flask 作为 Web 框架，可以使用 after_request 装饰器来实现类似的功能：


from flask import Flask, request
import psutil
import os

app = Flask(__name__)

@app.route('/api/your_endpoint', methods=['POST'])
def your_endpoint():
    # Your endpoint implementation
    return "Your response"

@app.after_request
def log_resource_usage(response):
    if request.method == 'POST':
        # 获取当前进程
        current_process = psutil.Process(os.getpid())

        # 收集资源使用情况
        cpu_percent = current_process.cpu_percent()
        memory_info = current_process.memory_info()
        rss = memory_info.rss
        io_counters = current_process.io_counters()
        read_bytes = io_counters.read_bytes
        write_bytes = io_counters.write_bytes
        net_io_counters = psutil.net_io_counters()
        bytes_sent = net_io_counters.bytes_sent
        bytes_recv = net_io_counters.bytes_recv

        # 输出资源使用情况
        print(f"POST request: {request.path}")
        print(f"CPU: {cpu_percent}%")
        print(f"Memory: {rss} bytes")
        print(f"Disk I/O (Read/Write): {read_bytes}/{write_bytes} bytes")
        print(f"Network I/O (Sent/Received): {bytes_sent}/{bytes_recv} bytes")

    return response

if __name__ == "__main__":
    app.run()
'''