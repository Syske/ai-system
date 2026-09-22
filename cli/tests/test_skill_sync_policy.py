#!/usr/bin/env python3
"""skill-sync 安全策略契约测试（node 驱动）—— R1：上传过滤 / 敏感文件 / 主机协议。

R1 背景（2026-09-21 盲检）：上传递归打包无过滤、无协议时回退 `http://`（API Key 明文）、
pull/push 各自复制同一份策略。策略已抽为 `skills/skill-sync/scripts/sync-policy.js`，
本测试直接驱动 node 校验其行为（无 node 时跳过）。

Run:
    python -m unittest cli.tests.test_skill_sync_policy
"""

import json
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
POLICY = REPO_ROOT / "skills" / "skill-sync" / "scripts" / "sync-policy.js"

NODE = shutil.which("node")


@unittest.skipUnless(NODE, "本机无 node，跳过 JS 策略测试")
class TestSyncPolicy(unittest.TestCase):

    def _eval(self, js):
        """在 node 中求值并回传 JSON（避免在 Python 里复制策略逻辑）。"""

        script = (
            f"const p = require({json.dumps(str(POLICY))});"
            f"const out = (() => {{ {js} }})();"
            "process.stdout.write(JSON.stringify(out));"
        )
        proc = subprocess.run(
            [NODE, "-e", script], capture_output=True, text=True, timeout=60
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return json.loads(proc.stdout)

    # ── 主机协议：无协议默认 https；显式 http 默认拒绝，仅在显式放行时通过

    def test_无协议默认_https(self):
        self.assertEqual(
            self._eval("return p.resolveHostUrl('insight.example.com');"),
            "https://insight.example.com",
        )

    def test_https_原样返回(self):
        self.assertEqual(
            self._eval("return p.resolveHostUrl('https://h.example.com');"),
            "https://h.example.com",
        )

    def test_显式_http_默认拒绝(self):
        self.assertTrue(self._eval(
            "try { p.resolveHostUrl('http://h.example.com', {allowInsecure: false});"
            " return {ok: true}; }"
            " catch (e) { return {ok: false, name: e.constructor.name}; }"
        )["ok"] is False)

    def test_显式_http_放行时通过(self):
        self.assertEqual(
            self._eval(
                "return p.resolveHostUrl('http://h.example.com', {allowInsecure: true});"
            ),
            "http://h.example.com",
        )

    def test_空主机报错(self):
        self.assertTrue(self._eval(
            "try { p.resolveHostUrl(''); return {ok: true}; }"
            " catch (e) { return {ok: false}; }"
        )["ok"] is False)

    # ── 打包排除：目录（含隐藏目录）/ 文件

    def test_排除目录(self):
        result = self._eval(
            "return ['/.git', 'node_modules', '.vscode', 'src', 'scripts']"
            ".map(n => p.isExcludedDir(n));"
        )
        self.assertEqual(result, [True, True, True, False, False])

    def test_排除文件(self):
        result = self._eval(
            "return ['.env', '.DS_Store', 'Thumbs.db', 'SKILL.md', 'helper.py']"
            ".map(n => p.isExcludedFile(n));"
        )
        self.assertEqual(result, [True, True, True, False, False])

    # ── 敏感文件：疑似凭据/私钥命中即拒传（fail loud）

    def test_敏感文件命中(self):
        result = self._eval(
            "return ['keys/id_rsa', '.env.prod', 'certs/server.pem', 'a/b.key',"
            " 'credentials.json', 'id_ed25519', '.npmrc'].map(f => p.isSensitive(f));"
        )
        self.assertEqual(result, [True] * 7)

    def test_普通文件不误报(self):
        result = self._eval(
            "return ['SKILL.md', 'scripts/pull.js', 'keys/readme.md', 'keyboard.md']"
            ".map(f => p.isSensitive(f));"
        )
        self.assertEqual(result, [False, False, False, False])

    # ── 两脚本确实使用共享策略（防再次分叉）

    def test_pull_push_引用共享策略(self):
        for name in ("pull.js", "push.js"):
            text = (POLICY.parent / name).read_text(encoding="utf-8")
            self.assertIn("require('./sync-policy')", text, name)
            self.assertNotIn("`http://${host}`", text, name)


if __name__ == "__main__":
    unittest.main()
