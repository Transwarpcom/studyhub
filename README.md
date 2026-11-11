# StudyHub 学习台

远程下发内容的高数 / 大学英语学习客户端（iOS，未签名 IPA 自签安装）。

## 它是什么

- **课程是文件夹树**：学科 → 章 → 节 → 卡片，不是聊天流。
- **内容由 Hermes 远程下发**：App 拉 `manifest.json`，版本变了自动更新；已读章节离线缓存。
- **渲染**：KaTeX 公式、内联 SVG 矢量图、表格、代码、引用、深色模式。
- **题型**：单选 / 多选 / 判断 / 填空 / 简答，答完即时判分 + 解析。
- **投喂**：拍照、相册、PDF、文本上传到服务端 inbox，Hermes 处理后的讲解自动出现在「答疑」页。

## 构建

GitHub Actions（macOS runner）出未签名 IPA：

```
Actions → Build IPA → 下载 StudyHub-ipa artifact → 解压得到 StudyHub-unsigned.ipa
```

本地构建需要 macOS + Xcode + `brew install xcodegen`：

```bash
xcodegen generate
xcodebuild -project StudyHub.xcodeproj -scheme StudyHub -sdk iphoneos \
  -configuration Release CODE_SIGNING_ALLOWED=NO build
```

## 服务端

`server/studyhub_server.py`：标准库 HTTP 服务，提供

- `GET  /api/manifest` 课程树
- `GET  /api/lesson/<path>` 单个章节
- `GET  /api/replies` 答疑回复
- `POST /api/upload` 上传题目（图片/PDF/文本）
- `GET  /api/inbox`（管理端）查看待处理
- `POST /api/reply`（管理端）推送讲解

## 内容格式

见 `content/` 目录。每章一个 JSON：

```json
{
  "id": "math/lim/01",
  "title": "1.1 数列极限的定义",
  "cards": [
    {"id":"c1","type":"lecture","title":"定义","md":"设 $\\{a_n\\}$ ..."},
    {"id":"c2","type":"choice","question":"...","options":["A","B"],"answer":[0],"explain":"..."},
    {"id":"c3","type":"blank","question":"$\\lim x_n = $ {{1}}","blanks":[["0"]],"explain":"..."}
  ]
}
```
