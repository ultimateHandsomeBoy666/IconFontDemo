#!/bin/bash

# IconFont Demo - 字体文件下载脚本
# 使用方法: chmod +x download_fonts.sh && ./download_fonts.sh

echo "🔥 正在下载IconFont字体文件..."

# 创建临时下载目录
mkdir -p temp_fonts

# 下载Material Icons
echo "📥 下载Material Icons..."
curl -L -o temp_fonts/MaterialIcons-Regular.ttf \
  "https://github.com/google/material-design-icons/raw/master/font/MaterialIcons-Regular.ttf"

if [ $? -eq 0 ]; then
    echo "✅ Material Icons下载成功"
    # 替换主应用中的字体文件
    cp temp_fonts/MaterialIcons-Regular.ttf app/src/main/res/font/material_icons.ttf
    cp temp_fonts/MaterialIcons-Regular.ttf app/src/main/assets/fonts/material_icons.ttf
    echo "📂 Material Icons已替换到项目中"
else
    echo "❌ Material Icons下载失败"
fi

# 尝试下载Font Awesome (可能需要特定版本)
echo "📥 尝试下载Font Awesome..."
curl -L -o temp_fonts/fa-solid-900.ttf \
  "https://use.fontawesome.com/releases/v6.4.0/webfonts/fa-solid-900.ttf"

if [ $? -eq 0 ] && [ -s temp_fonts/fa-solid-900.ttf ]; then
    echo "✅ Font Awesome下载成功"
    cp temp_fonts/fa-solid-900.ttf app/src/main/assets/fonts/fontawesome.ttf
    echo "📂 Font Awesome已替换到项目中"
else
    echo "❌ Font Awesome下载失败，请手动下载"
    echo "   下载地址: https://fontawesome.com/download"
fi

# 尝试下载一个开源的图标字体作为Feather Icons替代
echo "📥 下载开源图标字体作为Feather Icons..."
curl -L -o temp_fonts/feather.ttf \
  "https://at.alicdn.com/t/font_1465353_ui1hgbg5nma.ttf"

if [ $? -eq 0 ] && [ -s temp_fonts/feather.ttf ]; then
    echo "✅ Feather Icons替代字体下载成功"
    cp temp_fonts/feather.ttf iconfont-lib/src/main/res/font/feather_icons.ttf
    cp temp_fonts/feather.ttf iconfont-lib/src/main/assets/fonts/feather_icons.ttf
    echo "📂 Feather Icons已替换到AAR库中"
else
    echo "⚠️  Feather Icons替代字体下载失败"
fi

# 清理临时文件
rm -rf temp_fonts

echo ""
echo "🎉 字体文件下载完成！"
echo ""
echo "📋 下一步操作:"
echo "   1. 在Android Studio中打开项目"
echo "   2. Clean & Rebuild项目"
echo "   3. 运行应用查看图标效果"
echo "   4. 测试IconFontViewer插件预览功能"
echo ""
echo "⚠️  如果某些字体下载失败，请查看 FONT_DOWNLOAD_GUIDE.md 手动下载"