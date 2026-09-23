"""字段名归一化的单一来源（R2：#15 两处口径不一致）。

背景：`workflow_reader._norm_field_name` 剥离**任意**尾部括号注解，
而 `menu_config._base` 只剥 `(default: ...)` → 对
`发布内容 (services, clusters, ...)` 这类字段两处结果不同（查找不一致）。

规则（本模块唯一定义）：**尾部括号注解属元数据，不属字段身份** → 一律剥离。
"""

import re

# 尾部括号注解：`Base Branch (default: master)` → `Base Branch`
_ANNOTATION_RE = re.compile(r"\s*\([^)]*\)\s*$")


def base_field_name(field):
    """返回剥离尾部括号注解后的字段名（无注解则原样返回）。"""

    return _ANNOTATION_RE.sub("", str(field or ""))
