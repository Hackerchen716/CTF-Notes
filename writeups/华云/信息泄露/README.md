# 华云 - 信息泄露系列 (xxxl1-8) 详细 Writeup

> 信息泄露是 Web 安全中最基础也最常见的漏洞类型，本系列涵盖了 8 种常见的信息泄露场景。

---

## xxxl1 - 源码注释泄露

### 题目地址
https://my6n.huayunsys.com/games/1/challenges#68-xxxl1

### 解题过程

**Step 1**: 打开网页，看到一个前端样式展示页面 "Imaginarium"

**Step 2**: F12 打开开发者工具，查看 Elements（元素）面板

**Step 3**: 发现 HTML 注释中直接包含 flag：
```html
<!--
secret: flag{b5acbcb1-2503-4952-a846-b40c8994b27f}
Hint: View page source (右键 → 查看源代码) or Inspect to find more easter-eggs.
-->
```

**Step 4**: 还发现 body 标签有隐藏属性：
```html
<body data-secret="flag-hidden-1">
```

### Flag
```
flag{b5acbcb1-2503-4952-a846-b40c8994b27f}
```

### 知识点扩展

#### 为什么会有注释泄露？

1. **开发调试遗留**：开发者在调试时写的注释忘记删除
2. **版本控制问题**：从开发环境直接部署到生产环境
3. **模板引擎**：某些模板引擎不会过滤 HTML 注释

#### 常见注释泄露位置

```html
<!-- 这是 HTML 注释 -->
<!-- TODO: 删除这个测试账号 admin/123456 -->
<!-- DEBUG: API_KEY=xxxxx -->

/* CSS 注释 */
/* 临时隐藏，密码是 password123 */

// JavaScript 注释
// var secret_api = "https://internal.api.com/v1"
/* 
 * 作者：张三
 * 数据库：mysql://root:root@localhost/db
 */
```

#### 查看源码的多种方式

| 方法 | 操作 | 说明 |
|------|------|------|
| 右键菜单 | 右键 → 查看页面源代码 | 可能被 JS 禁用 |
| 快捷键 | `Ctrl+U` / `Cmd+Option+U` | 不受 JS 影响 |
| 地址栏 | `view-source:http://xxx` | 最可靠的方式 |
| F12 | 开发者工具 → Elements | 可以看到动态生成的内容 |
| curl | `curl http://xxx` | 命令行获取原始 HTML |

#### 自动化检测脚本

```python
import requests
import re

def check_html_comments(url):
    """检查 HTML 注释中的敏感信息"""
    r = requests.get(url)
    
    # 匹配 HTML 注释
    comments = re.findall(r'<!--(.*?)-->', r.text, re.DOTALL)
    
    # 敏感关键词
    sensitive = ['password', 'secret', 'key', 'token', 'flag', 
                 'admin', 'root', 'debug', 'todo', 'fixme']
    
    for comment in comments:
        for word in sensitive:
            if word.lower() in comment.lower():
                print(f"[!] 发现敏感注释: {comment[:100]}...")
                
check_html_comments("http://target.com")
```

---

## xxxl2 - phpinfo 信息泄露

### 题目地址
端口 :37315

### 解题过程

**Step 1**: 打开页面，发现是 `phpinfo()` 输出页面

**Step 2**: 使用 `Ctrl+F` 搜索 "flag"

**Step 3**: 在 `$_SERVER` 或 `$_ENV` 部分找到：
```
$_SERVER['GZCTF_FLAG'] = flag{a24a552b-48ec-4161-bb92-69c596e5a67d}
```

### Flag
```
flag{a24a552b-48ec-4161-bb92-69c596e5a67d}
```

### 知识点扩展

#### phpinfo() 泄露的危害

`phpinfo()` 会暴露大量服务器信息：

| 信息类型 | 泄露内容 | 危害 |
|----------|----------|------|
| PHP 版本 | `PHP Version 7.4.3` | 可针对性找漏洞 |
| 系统信息 | `Linux xxx 5.4.0` | 确定操作系统 |
| 配置路径 | `/etc/php/7.4/apache2/php.ini` | 文件包含利用 |
| 网站路径 | `DOCUMENT_ROOT: /var/www/html` | 确定 Web 根目录 |
| 环境变量 | `$_ENV`, `$_SERVER` | 可能包含密钥、密码 |
| 已加载扩展 | `curl`, `mysql`, `gd` | 确定可用功能 |
| disabled_functions | `system,exec,shell_exec` | 确定禁用函数 |

#### 常见 phpinfo 路径

```
/phpinfo.php
/info.php
/php_info.php
/test.php
/i.php
/pi.php
/?phpinfo=1
/?debug=phpinfo
```

#### 重要关注项

```bash
# 搜索这些关键词
flag
password
secret
key
token
DOCUMENT_ROOT      # 网站根目录
disable_functions  # 禁用的危险函数
open_basedir       # 目录限制
allow_url_include  # 远程文件包含
```

---

## xxxl3 - robots.txt 泄露

### 题目地址
端口 :37316

### 解题过程

**Step 1**: 访问 `/robots.txt`
```
disallow: f14ggggggggggg.txt
```

**Step 2**: 访问 `/f14ggggggggggg.txt`

### Flag
```
flag{62b916b6-c985-4a31-b673-a43c0e9a098f}
```

### 知识点扩展

#### robots.txt 是什么？

```
robots.txt 是网站根目录下的爬虫协议文件
用于告诉搜索引擎哪些页面可以抓取，哪些不可以
但这只是"君子协议"，恶意爬虫完全可以忽略
```

#### 标准格式

```txt
# 允许所有爬虫访问所有内容
User-agent: *
Allow: /

# 禁止所有爬虫访问 /admin 目录
User-agent: *
Disallow: /admin/

# 只允许 Google 爬虫
User-agent: Googlebot
Allow: /
User-agent: *
Disallow: /

# 指定 sitemap 位置
Sitemap: https://example.com/sitemap.xml
```

#### CTF 中的利用

```txt
# 常见的 flag 藏匿方式
Disallow: /flag.txt
Disallow: /admin/flag.php
Disallow: /secret/
Disallow: /backup/
Disallow: /.git/
Disallow: /flag_is_here.php
```

---

## xxxl4 - 源码压缩包泄露

### 题目地址
端口 :37317

### 解题过程

**Step 1**: 尝试常见的备份文件名，下载 `www.zip`

**Step 2**: 解压后查看 `index.php`：
```php
<?php
echo "flag is here!";
//flag{696ce6f6-7ce2-4e0f-9154-d6892c74b5d8};
?>
```

### Flag
```
flag{696ce6f6-7ce2-4e0f-9154-d6892c74b5d8}
```

### 知识点扩展

#### 常见备份文件名

| 类型 | 文件名 | 说明 |
|------|--------|------|
| 压缩包 | `www.zip`, `web.zip`, `backup.zip` | 最常见 |
| 压缩包 | `html.zip`, `htdocs.zip` | Apache 默认目录名 |
| 压缩包 | `wwwroot.zip`, `wwwroot.rar` | IIS/宝塔常见 |
| 压缩包 | `website.tar.gz`, `site.tar.gz` | Linux 打包 |
| 压缩包 | `[域名].zip` | 如 `example.com.zip` |
| 数据库 | `backup.sql`, `dump.sql`, `db.sql` | 数据库备份 |
| 单文件 | `index.php.bak`, `index.php~` | 编辑器备份 |
| 单文件 | `.index.php.swp`, `.index.php.swo` | Vim 临时文件 |

#### 为什么会有备份泄露？

1. **运维习惯**：直接在 Web 目录打包备份
   ```bash
   cd /var/www/html
   zip -r www.zip ./*    # 错误！应该放到 Web 目录外
   ```

2. **编辑器自动备份**：
   ```bash
   vim index.php    # 会产生 .index.php.swp
   gedit index.php  # 会产生 index.php~
   ```

#### 自动化扫描工具

**dirsearch**：
```bash
python dirsearch.py -u http://target.com -e php,txt,zip,bak,sql
```

---

## xxxl5 - 302 重定向泄露

### 解题过程

**Step 1**: 访问页面，发现自动跳转

**Step 2**: F12 → Network（网络）面板 → 刷新页面

**Step 3**: 查看第一个请求（302 状态码），在响应头或响应体中找到 flag

### 知识点扩展

#### HTTP 重定向状态码

| 状态码 | 含义 | 说明 |
|--------|------|------|
| 301 | 永久重定向 | 资源永久移动 |
| 302 | 临时重定向 | 资源临时移动 |
| 303 | See Other | POST 后重定向到 GET |
| 307 | 临时重定向 | 保持请求方法不变 |

#### 为什么重定向会泄露信息？

```php
<?php
// 漏洞代码示例
$flag = "flag{xxx}";
echo $flag;  // 先输出了 flag
header("Location: /login.php");  // 再重定向
// 问题：浏览器会自动跳转，但响应体已经发送了
?>
```

正确写法：
```php
<?php
header("Location: /login.php");
exit();  // 必须 exit，否则后面的代码还会执行
?>
```

#### 如何捕获重定向响应？

**方法 1: F12 Network**
```
1. 打开 F12 → Network
2. 刷新页面
3. 点击 302 的请求
4. 查看 Response（响应）标签
```

**方法 2: curl 不跟随重定向**
```bash
curl -I http://target.com/           # 只看响应头
curl http://target.com/              # 看响应体（不跟随跳转）
curl -L http://target.com/           # 跟随跳转
```

---

## xxxl6 - .git 泄露

### 解题过程

**Step 1**: 访问 `/.git/config` 确认存在

**Step 2**: 使用 GitHack 下载源码
```bash
python GitHack.py http://target.com/.git/
```

**Step 3**: 在恢复的源码中找到 flag

### 知识点扩展

#### .git 目录结构

```
.git/
├── config          # 仓库配置
├── HEAD            # 当前分支指针
├── index           # 暂存区
├── objects/        # Git 对象（commits, trees, blobs）
├── refs/           # 引用（分支、标签）
└── logs/           # 操作日志
```

#### 利用工具

**GitHack**：
```bash
git clone https://github.com/lijiejie/GitHack.git
python GitHack.py http://target.com/.git/
```

**git-dumper**（更强大）：
```bash
pip install git-dumper
git-dumper http://target.com/.git/ output_dir
```

#### 查看历史提交

```bash
cd output_dir
git log --all                    # 查看所有提交
git show <commit_hash>           # 查看某次提交的内容
git diff HEAD~1                  # 对比上一次提交
```

---

## xxxl7 - .DS_Store 泄露

### 知识点扩展

#### 什么是 .DS_Store？

```
.DS_Store (Desktop Services Store) 是 macOS 系统自动生成的隐藏文件
用于存储目录的自定义属性（图标位置、背景图等）
里面包含了目录下的文件列表！
```

#### 利用方式

```bash
git clone https://github.com/lijiejie/ds_store_exp.git
python ds_store_exp.py http://target.com/.DS_Store
```

---

## xxxl8 - 目录扫描

### 题目地址
端口 :37319

### 解题过程

**Step 1**: 访问 `/robots.txt`
```
User-agent: *
Disallow: test.php

have fun with my test!
try scan me!
```

**Step 2**: 提示 "try scan me" → 需要目录扫描

**Step 3**: 使用 dirsearch 扫描
```bash
python dirsearch.py -u http://47.109.105.62:37319/ -e php,txt,html
```

**Step 4**: 找到隐藏的文件/目录，获取 flag

### 知识点扩展

#### 常用目录扫描工具

| 工具 | 特点 | 命令 |
|------|------|------|
| dirsearch | Python，速度快 | `python dirsearch.py -u url -e php` |
| dirb | Kali 自带 | `dirb http://url /usr/share/wordlists/dirb/common.txt` |
| gobuster | Go 语言，超快 | `gobuster dir -u url -w wordlist.txt` |
| ffuf | Go 语言，灵活 | `ffuf -u url/FUZZ -w wordlist.txt` |

#### dirsearch 常用参数

```bash
# 基本扫描
python dirsearch.py -u http://target.com -e php,txt,html,zip

# 指定字典
python dirsearch.py -u http://target.com -w /path/to/wordlist.txt

# 多线程
python dirsearch.py -u http://target.com -t 50

# 递归扫描
python dirsearch.py -u http://target.com -r

# 过滤状态码
python dirsearch.py -u http://target.com --exclude-status 404,403
```

#### 常见敏感目录

```
/admin/
/backup/
/test/
/upload/
/config/
/data/
/include/
/api/
/debug/
/.svn/
/.git/
```

---

## 总结 - 信息泄露检测清单

```bash
# 必查路径
/robots.txt
/.git/config
/.svn/entries
/.DS_Store
/phpinfo.php
/info.php

# 常见备份
/www.zip
/backup.zip
/web.zip
/backup.sql
/index.php.bak
/.index.php.swp
```

### 自动化扫描脚本

```python
#!/usr/bin/env python3
"""信息泄露一键检测"""
import requests

PATHS = [
    '/robots.txt',
    '/.git/config',
    '/.git/HEAD',
    '/.svn/entries',
    '/.svn/wc.db',
    '/.DS_Store',
    '/phpinfo.php',
    '/info.php',
    '/www.zip',
    '/backup.zip',
    '/web.zip',
    '/backup.sql',
    '/index.php.bak',
]

def scan(url):
    url = url.rstrip('/')
    print(f"[*] 扫描目标: {url}\n")
    
    for path in PATHS:
        try:
            r = requests.get(url + path, timeout=5)
            if r.status_code == 200 and len(r.content) > 0:
                print(f"[+] 发现: {path} ({len(r.content)} bytes)")
        except:
            pass

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("用法: python leak_scan.py <url>")
    else:
        scan(sys.argv[1])
```

---

## 防御措施

1. **部署前检查**：删除 .git、.svn、备份文件
2. **Web 服务器配置**：禁止访问隐藏文件
   ```nginx
   # Nginx
   location ~ /\. {
       deny all;
   }
   ```
3. **代码审查**：删除调试注释
4. **使用 .gitignore**：排除敏感文件
5. **CI/CD 规范**：自动化部署流程
