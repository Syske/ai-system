/**
 * skill-sync 上传/下载安全策略（单一来源，R1 修复 2026-09-21）。
 *
 * 背景（盲检 R1 项）：
 * - 上传递归打包**无任何过滤** → `.git` / `node_modules` / `.env` / 隐藏文件一并进包，
 *   凭据文件可能被上传；
 * - 主机无协议时**回退 `http://`** → API Key 明文传输；
 * - `pull.js` / `push.js` 各自复制同一份策略（口径易漂移）。
 *
 * 本模块把三项策略集中定义，供两个脚本 require，并可直接被 node 测试覆盖。
 */

// 绝不打包的目录（另：任何以 "." 开头的目录一律排除）
const PACK_EXCLUDE_DIRS = new Set([
    '.git',
    'node_modules',
    '__pycache__',
    '.venv',
    'venv',
    '.idea',
    '.vscode',
    'dist',
    'build',
    '.pytest_cache',
    '.mypy_cache',
]);

// 绝不打包的文件
const PACK_EXCLUDE_FILES = new Set(['.DS_Store', 'Thumbs.db', '.env']);

// 疑似凭据/私钥 —— 命中即拒绝打包（fail loud，不静默跳过）
const SENSITIVE_RE = /(^|[\\/])(\.env(\..*)?|\.npmrc|\.netrc|credentials(\.json)?|id_rsa|id_ed25519|id_ecdsa|.*\.(pem|key|p12|pfx|jks|keystore|ppk|pub))$/i;

// 取 basename：调用方既可传目录名（push.js 现状），也可传路径（更稳健）
function baseName(name) {
    return String(name).split(/[\\/]/).pop();
}

function isExcludedDir(name) {
    const base = baseName(name);
    return PACK_EXCLUDE_DIRS.has(base) || base.startsWith('.');
}

function isExcludedFile(name) {
    return PACK_EXCLUDE_FILES.has(baseName(name));
}

/** 相对路径是否疑似凭据（用于拒绝打包）。 */
function isSensitive(relPath) {
    return SENSITIVE_RE.test(String(relPath));
}

class InsecureHostError extends Error {}

/**
 * 解析主机为 URL：无协议时**默认 https**；显式 `http://` 仅在
 * `AGENT_INSIGHT_ALLOW_INSECURE=1`（或 opts.allowInsecure）时放行，否则抛错。
 */
function resolveHostUrl(host, opts = {}) {
    const allowInsecure = opts.allowInsecure !== undefined
        ? opts.allowInsecure
        : process.env.AGENT_INSIGHT_ALLOW_INSECURE === '1';

    const raw = String(host || '').trim();

    if (!raw) {
        throw new Error('Agent Insight Host is not configured.');
    }

    if (/^https:\/\//i.test(raw)) {
        return raw;
    }

    if (/^http:\/\//i.test(raw)) {
        if (allowInsecure) {
            return raw;
        }
        throw new InsecureHostError(
            '拒绝使用明文 http 传输（API Key 会以明文发送）。请配置 https 主机，'
            + '或显式设置 AGENT_INSIGHT_ALLOW_INSECURE=1 承担风险。'
        );
    }

    return `https://${raw}`;
}

module.exports = {
    PACK_EXCLUDE_DIRS,
    PACK_EXCLUDE_FILES,
    SENSITIVE_RE,
    InsecureHostError,
    isExcludedDir,
    isExcludedFile,
    isSensitive,
    resolveHostUrl,
};