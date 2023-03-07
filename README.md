### Python版本说明

基于python3.11.2开发。

### pip安装python依赖包

```shell
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn
```

windows可能遇到以下错误：
`error: Microsoft Visual C++ 14.0 or greater is required.`

请到 <https://www.lfd.uci.edu/~gohlke/pythonlibs/> 直接下载该包的whl文件，放到项目下，然后`pip install xxx.whl`

例如：

```shell
pip install twisted_iocpsupport‑1.0.2‑cp311‑cp311‑win_amd64.whl
```

### 配置pre-commit

```shell
pip install pre-commit
pre-commit install --allow-missing-config
pre-commit install --hook-type commit-msg --allow-missing-config
```

### Celery命令

#### 启动celery worker

```shell
# celery worker --help
celery -A heartgo worker -l INFO
[-Q your_queue] [-c 10] [-O fair] [--max-tasks-per-child=50]

# win10调用celery4.x版本以上，执行task抛ValueError
# 更改默认prefork多进程并发为协程
celery -A ... -P gevent -c 100
```

#### 启动celery beat

```shell
celery -A heartgo beat -l INFO
```