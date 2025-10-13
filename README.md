# IconFont Demo Project

这个Android项目是专门为测试 `IconFontViewer` IDEA/Android Studio 插件而创建的。

## 项目目的

测试 `IconFontViewer` 插件在以下场景中的图标预览功能：

1. **XML布局文件** - 测试 `@string/xxx` 引用的预览
2. **Kotlin/Java代码** - 测试 `R.string.xxx` 引用的预览
3. **资源文件** - 测试各种字符串资源文件中的字符/码点预览
4. **AAR库依赖** - 测试跨模块的iconfont引用预览

## 项目结构

### 主应用 (app模块)

```
app/
├── src/main/
│   ├── java/com/example/iconfontdemo/
│   │   ├── MainActivity.kt                 # 主活动，包含大量R.string引用
│   │   ├── IconFontTextView.kt            # 自定义IconFont视图
│   │   └── IconFontManager.kt             # 图标管理类，演示代码中的各种使用场景
│   ├── res/
│   │   ├── layout/
│   │   │   └── activity_main.xml          # 主布局，包含@string/引用案例
│   │   ├── values/
│   │   │   ├── strings.xml                # 主要的iconfont字符定义
│   │   │   ├── icon_strings.xml           # 额外的图标字符串
│   │   │   ├── arrays.xml                 # 图标数组，包含@string/引用
│   │   │   ├── attrs.xml                  # 自定义属性
│   │   │   ├── colors.xml                 # 颜色资源
│   │   │   └── themes.xml                 # 主题样式
│   │   ├── values-zh/
│   │   │   └── strings.xml                # 中文版字符串资源
│   │   ├── menu/
│   │   │   ├── main_menu.xml              # 主菜单，title使用@string/引用
│   │   │   └── navigation_menu.xml        # 导航菜单
│   │   ├── font/
│   │   │   └── material_icons.ttf         # Material Icons字体文件
│   │   └── assets/fonts/
│   │       ├── material_icons.ttf         # Material Icons字体文件副本
│   │       └── fontawesome.ttf            # FontAwesome字体文件
│   └── AndroidManifest.xml
├── build.gradle                           # 应用构建配置
└── proguard-rules.pro
```

### AAR库模块 (iconfont-lib)

```
iconfont-lib/
├── src/main/
│   ├── java/com/example/iconfontlib/
│   │   └── IconFontHelper.kt              # 库中的工具类，包含R.string引用
│   ├── res/
│   │   ├── values/
│   │   │   └── strings.xml                # 库中的iconfont字符定义
│   │   └── font/
│   │       └── feather_icons.ttf          # Feather Icons字体文件
│   ├── assets/fonts/
│   │   └── feather_icons.ttf              # Feather Icons字体文件副本
│   └── AndroidManifest.xml
├── build.gradle                           # 库构建配置
├── proguard-rules.pro
└── consumer-rules.pro
```

## 测试覆盖的场景

### 1. XML布局文件中的@string/引用
- `android:text="@string/icon_home"`
- `android:title="@string/icon_settings"`
- 自定义视图属性中的引用

### 2. Kotlin代码中的R.string引用
- `getString(R.string.icon_home)`
- `context.getString(R.string.icon_search)`
- 数组、List、Map中的R.string引用
- 条件语句中的R.string引用
- 函数参数中的R.string引用

### 3. 资源文件中的引用
- `arrays.xml`中的`@string/`引用
- `menu.xml`中的`android:title="@string/"`引用
- 多语言资源文件中的字符定义

### 4. 跨模块引用
- 主应用引用AAR库中的R.string资源
- 通过工具类方法间接引用

## 字体文件说明

项目包含以下iconfont字体文件的占位符：

1. **Material Icons** (`material_icons.ttf`)
   - Unicode范围：E000-F8FF
   - 示例字符：&#xE88A; (home), &#xE8B6; (search)

2. **FontAwesome** (`fontawesome.ttf`)
   - Unicode范围：F000-F2FF
   - 示例字符：\uF004 (heart), \uF005 (star)

3. **Feather Icons** (`feather_icons.ttf`)
   - 在AAR库中提供
   - Unicode范围：E000-F8FF

## 如何使用

1. 在Android Studio中打开此项目
2. 确保已安装 `IconFontViewer` 插件
3. 插件应该能在以下位置显示图标预览：
   - XML布局文件的gutter中
   - Kotlin/Java代码行的gutter中
   - 资源文件的gutter中

## 预期效果

插件应该能够：
- 识别所有的`@string/icon_*`引用并显示对应图标
- 识别所有的`R.string.icon_*`引用并显示对应图标
- 在不同类型的资源文件中正确预览
- 跨模块正确识别AAR库中的图标资源
