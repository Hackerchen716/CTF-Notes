# 华云 - 暴力破解系列 (blpj1-4) 详细 Writeup

> 暴力破解是 Web 安全中常见的攻击手段，本系列涵盖了基础爆破和 Payload 处理两种场景。

---

## blpj1 - 基础爆破

### 题目信息
- 考点：多参数暴力破解
- 难度：⭐

### 解题思路

1. 打开题目是登录页面
2. 题目提示用户名是 0-5 的数字
3. 使用 Burp Suite 或 Python 脚本爆破

### Burp Suite 配置

**Step 1**: 抓包，发送到 Intruder

**Step 2**: Attack type 选择 **Cluster bomb**（多参数笛卡尔积）

**Step 3**: 设置 Payload：
- Position 1 (username): Numbers, 0-5
- Position 2 (password): 加载字典 top50k.txt

**Step 4**: Start attack，观察 Length 列

### Python 脚本配置

```python
payloads = {
    "USER": {"type": "range", "start": 0, "end": 5, "processors": []},
    "PASS": {"type": "file", "path": "top50k.txt", "processors": []}
}
```

---

## blpj2 - 多参数爆破

### 题目信息
- 考点：多参数暴力破解
- 难度：⭐

### 解题思路

和 blpj1 类似，都是多参数爆破，可能：
- 用户名范围不同
- 密码字典不同

### 配置方式

```python
# 根据题目提示调整范围
payloads = {
    "USER": {"type": "range", "start": 0, "end": 10, "processors": []},
    "PASS": {"type": "file", "path": "top50k.txt", "processors": []}
}
```

---

## blpj3 - Payload 处理（Base64）

### 题目信息
- 考点：Payload 处理、Base64 编码
- 难度：⭐⭐

### 解题思路

观察 Burp Suite 的 Payload Processing 规则：
1. **Add Prefix**: `admin:` 
2. **Base64-encode**

### 密码处理流程

```
原始密码: 123456
    ↓
添加前缀: admin:123456
    ↓
Base64编码: YWRtaW46MTIzNDU2
    ↓
发送到服务器
```

### Burp Suite 配置

```
Intruder → Payloads → Payload Processing
1. Add rule: Add Prefix → admin:
2. Add rule: Encode → Base64-encode
```

### Python 脚本配置

```python
payloads = {
    "USER": {"type": "list", "values": ["admin"], "processors": []},
    "PASS": {
        "type": "file", 
        "path": "top50k.txt",
        "processors": [
            P.prefix("admin:"),
            P.base64_encode()
        ]
    }
}
```

---

## blpj4 - 多参数爆破

### 题目信息
- 考点：多参数暴力破解
- 难度：⭐

### 解题思路

和 blpj1、blpj2 类似，根据题目提示调整参数范围即可。

### 通用配置

```python
# 根据题目实际提示修改
payloads = {
    "USER": {"type": "range", "start": 0, "end": N, "processors": []},
    "PASS": {"type": "file", "path": "top50k.txt", "processors": []}
}
```

---

## 爆破技巧总结

### Burp Suite Attack Types

| 类型 | 说明 | 适用场景 |
|------|------|----------|
| Sniper | 单参数逐个替换 | 只爆破一个参数 |
| Battering ram | 所有参数同时替换相同值 | 用户名=密码的情况 |
| Pitchfork | 多参数一一对应 | 用户名和密码成对 |
| **Cluster bomb** | 多参数笛卡尔积 | 最常用，全组合 |

### 常见 Payload 处理规则

| 处理类型 | 说明 | 示例 |
|----------|------|------|
| Add Prefix | 添加前缀 | `admin:` + pwd |
| Add Suffix | 添加后缀 | pwd + `@123` |
| Base64-encode | Base64 编码 | `YWRtaW4=` |
| MD5 | MD5 哈希 | 32位小写 |
| SHA1 | SHA1 哈希 | 40位 |
| URL-encode | URL 编码 | `%20` |

### Burp vs Python 速度对比

| 工具 | 并发数 | 速度 | 适用场景 |
|------|--------|------|----------|
| Burp Suite | 10-50 | ~100/s | 调试、小字典 |
| Python 异步 | 300-500 | 2000+/s | 大字典爆破 |

### 提高 Burp 速度

```
1. Intruder → Resource Pool → 新建池
2. Maximum concurrent requests: 50-100
3. 或使用 Turbo Intruder 插件
```

---

## 通用爆破工具使用

使用仓库中的 `tools/ctf_brute_v6.py`：

```bash
# 基本使用
python tools/ctf_brute_v6.py -u http://target.com/ -t 500

# 修改配置
编辑脚本中的 payloads 字典，设置：
- 参数类型：range/list/file
- 处理器：P.prefix()/P.base64_encode()/P.md5() 等
```

### 支持的处理器

```python
P.prefix("xxx")      # 添加前缀
P.suffix("xxx")      # 添加后缀
P.base64_encode()    # Base64 编码
P.md5()              # MD5 哈希
P.sha1()             # SHA1 哈希
P.url_encode()       # URL 编码
P.upper()            # 转大写
P.lower()            # 转小写
```
