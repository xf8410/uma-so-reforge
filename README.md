# uma-so-reforge

**赛马娘 686 版 SO 插件重构**：从 hlpatch v3.28.3 发布态源码（生成链本地重放解出）为基线的新直线演化仓。

## 与 hlpatch 的关系

- 基线 = hlpatch `main@4441a0c`（v3.28.3 纯数据管道）的**发布态源码**（在本地重放生成链解出，非工作树快照）
- hlpatch 保留不动；本仓从此直线演化，直改源码，不再走生成式补丁链
- 继续遵守：纯数据管道（决策归 jueceramen/umaai-rs）、绝无脱敏逻辑、模拟器黑盒

## v3.29.0 变更

1. **删除"跳过画面加速"**（用户令）：`training_anim_skip` 模块、路由、boot-safe 注册、install 调用全部移除
2. **新增运行时全量偏移导出**：
   - `GET /il2cpp/dump_offsets_meta` — image 名 + 各字母类数统计
   - `GET /il2cpp/dump_offsets?letter=A` — 该字母段全部类：字段名/偏移/类型 + 方法名/运行时地址/token（letter 分页防手机卡死）
   - 游戏版本更新后跑一遍（`tools/dump_pipeline.py`），直接拿新版全部偏移，不再猜
3. 版本 3.29.0（小步递增）

## 构建与发布

- push main → CI 自动编译 arm64 release（NDK r26c）并上传 artifact
- 发布：手动触发 `release.yml`，产出 GitHub Release（拒绝覆盖已存在 tag）

## 686 偏移 dump 流水线

```bash
# 手机注入 v3.29.0+ SO 后（进育成主界面）：
adb forward tcp:18765 tcp:18765
python3 tools/dump_pipeline.py --out ./dump686
# 产物：dump686/dump_offsets_meta.json + offsets_<A-Z>.json
```

## 上游

- Hachimi 插件框架：https://github.com/noccu/hachimi （插件开发文档 https://hachimi.noccu.art/zh-cn/docs/plugins/development ）
- 模拟器唯一可信基准：xulai1001/umaai-rs
