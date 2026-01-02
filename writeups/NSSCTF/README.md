# NSSCTF - JS 分析题目

## 导弹迷踪

### 题目信息
- 考点：JavaScript 分析
- 难度：⭐

### 解题步骤

1. F12 打开开发者工具
2. 查看 Sources 或 Network，找到 game.js
3. 搜索 "flag" 或 "score" 关键字
4. 找到判断条件，在控制台执行相关代码

---

## 1zjs

### 题目信息
- 考点：JS 混淆、JSFuck
- 难度：⭐⭐

### 解题步骤

**Step 1**: 查看源代码
```
发现引用: ./dist/index.umd.js
```

**Step 2**: 分析 JS 文件
```
找到提示: Your gift just take it : /f@k3f1ag.php
```

**Step 3**: 访问 `/f@k3f1ag.php`

得到一堆 `[]()!+` 符号 —— 这是 **JSFuck** 编码

**Step 4**: 解码 JSFuck
- 方法1：直接在控制台执行
- 方法2：使用在线解码器

### Flag
`NSSCTF{c64abefc-73d3-4f0b-8f83-9f3588c2dc5e}`

---

## JSFuck 是什么？

JSFuck 是只用 6 个字符 `[]()!+` 编写的 JavaScript。

原理：利用 JS 类型转换特性
```javascript
// "a" 的表示
(![]+[])[+!+[]]

// 解释:
// ![] = false
// ![]+[] = "false"
// +!+[] = 1
// "false"[1] = "a"
```

---

## JS 题目通用技巧

1. **F12 大法** - 查看所有 JS 文件
2. **搜索关键字** - flag, key, score, win, success
3. **断点调试** - 在关键位置设断点
4. **控制台执行** - 调用函数或修改变量
5. **混淆识别** - JSFuck、JJEncode、AAEncode
