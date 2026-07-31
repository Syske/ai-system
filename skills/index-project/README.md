# Index Project

重建当前项目的语义代码索引。

## 使用方式

```bash
/index-project
```

增量索引（默认）：

```bash
/index-project --full
```

全量重建索引。

## 功能

- 使用 code-index CLI 构建代码语义索引
- 实时显示索引进度
- 自动将 `.code_index` 加入 `.gitignore`
