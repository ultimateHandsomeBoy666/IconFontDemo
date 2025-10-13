# 字体文件下载指南

当前项目中的TTF文件只是占位符，需要替换为真实的字体文件才能正常工作。

## 📥 需要下载的字体文件

### 1. Material Icons
- **下载地址**: https://github.com/google/material-design-icons/blob/master/font/MaterialIcons-Regular.ttf
- **替换文件**:
  - `app/src/main/res/font/material_icons.ttf`
  - `app/src/main/assets/fonts/material_icons.ttf`
- **字符编码**: 使用Unicode私有区域 (E000-F8FF)

### 2. Font Awesome
- **下载地址**: https://fontawesome.com/download (需要注册)
- **或GitHub**: https://github.com/FortAwesome/Font-Awesome/tree/6.x/webfonts
- **文件名**: `fa-solid-900.ttf` 或 `fontawesome-webfont.ttf`
- **替换文件**: `app/src/main/assets/fonts/fontawesome.ttf`

### 3. Feather Icons (用于AAR库测试)
- **下载地址**: https://github.com/feathericons/feather
- **或直接**: https://at.alicdn.com/t/font_1392140_u4nrnp8owdj.ttf
- **替换文件**:
  - `iconfont-lib/src/main/res/font/feather_icons.ttf`
  - `iconfont-lib/src/main/assets/fonts/feather_icons.ttf`

## 🔄 快速替换步骤

1. **下载Material Icons**:
```bash
# 方法1: 直接下载
curl -L -o material_icons.ttf "https://github.com/google/material-design-icons/raw/master/font/MaterialIcons-Regular.ttf"

# 方法2: 从Google Fonts获取
# 访问 https://fonts.google.com/icons，点击下载按钮
```

2. **下载Font Awesome**:
```bash
# 从CDN获取 (可能需要找到最新链接)
curl -L -o fontawesome.ttf "https://use.fontawesome.com/releases/v6.4.0/webfonts/fa-solid-900.ttf"
```

3. **替换占位符文件**:
```bash
# 进入项目目录
cd /Users/bullfrog/AndroidStudioProjects/IconFontDemo

# 替换Material Icons
cp ~/Downloads/MaterialIcons-Regular.ttf app/src/main/res/font/material_icons.ttf
cp ~/Downloads/MaterialIcons-Regular.ttf app/src/main/assets/fonts/material_icons.ttf

# 替换Font Awesome
cp ~/Downloads/fa-solid-900.ttf app/src/main/assets/fonts/fontawesome.ttf

# 如果有Feather Icons
cp ~/Downloads/feather.ttf iconfont-lib/src/main/res/font/feather_icons.ttf
cp ~/Downloads/feather.ttf iconfont-lib/src/main/assets/fonts/feather_icons.ttf
```

## 🎯 验证字体文件

替换后，您可以通过以下方式验证字体文件是否正确：

1. **在Android Studio中预览**
   - 打开 `res/font/material_icons.ttf`
   - 应该能看到字体预览

2. **运行应用测试**
   - 构建并运行项目
   - 查看图标是否正确显示

3. **插件测试**
   - 打开任意包含 `@string/icon_xxx` 的文件
   - 检查gutter是否显示图标预览

## 📋 Unicode对应表

### Material Icons 常用字符
```
E88A - home (首页)
E8B6 - search (搜索)
E87D - favorite (收藏)
E8B8 - settings (设置)
E7FD - person (用户)
E145 - add (添加)
E872 - delete (删除)
E3C9 - edit (编辑)
E80D - share (分享)
```

### Font Awesome 常用字符
```
F004 - heart (心形)
F005 - star (星形)
F007 - user (用户)
F013 - cog (设置齿轮)
F015 - home (首页)
F002 - search (搜索)
```

## ⚠️ 注意事项

1. **版权问题**: 确保遵守字体的许可证条款
2. **文件大小**: 字体文件可能较大，注意应用包大小
3. **字符映射**: 不同版本的字体文件，字符映射可能不同
4. **测试覆盖**: 替换字体后，测试所有引用的字符是否正确显示

## 🚀 推荐的测试流程

1. 先替换Material Icons，测试主要功能
2. 再添加Font Awesome，测试多字体支持
3. 最后添加Feather Icons，测试AAR库引用
4. 在Android Studio中运行项目，验证显示效果
5. 测试插件在各种文件中的预览功能