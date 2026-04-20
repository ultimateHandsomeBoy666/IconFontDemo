package com.example.iconfontdemo

/**
 * AAR 依赖中的 IconFont 引用测试文件
 *
 * 用于验证 IconFontViewer 插件能否：
 * 1. 扫描到 AAR 中的 TTF 字体文件
 * 2. 在 gutter 处预览 AAR 字体的图标
 * 3. 点击 gutter icon 时弹窗展示 AAR 字体的所有可用图标
 *
 * AAR 依赖：
 * - com.mikepenz:fontawesome-typeface:5.13.3.1-kotlin (FontAwesome 5 Solid)
 * - com.mikepenz:google-material-typeface:4.0.0.3-kotlin (Google Material Filled)
 */
object AarIconFontDemo {

    // ── FontAwesome 5 Solid (AAR) ──
    // 以下 R.string 引用的 Unicode 字符来自 fontawesome_solid_font_v5_13_3.ttf

    fun getFontAwesomeIcons(): Map<String, Int> = mapOf(
        "music" to R.string.aar_fa_music,
        "search" to R.string.aar_fa_search,
        "heart" to R.string.aar_fa_heart,
        "user" to R.string.aar_fa_user,
        "check" to R.string.aar_fa_check,
        "close" to R.string.aar_fa_close,
        "cog" to R.string.aar_fa_cog,
        "home" to R.string.aar_fa_home,
        "download" to R.string.aar_fa_download,
        "refresh" to R.string.aar_fa_refresh,
        "plus" to R.string.aar_fa_plus,
        "minus" to R.string.aar_fa_minus,
    )

    // ── Google Material Filled (AAR) ──
    // 以下 R.string 引用的 Unicode 字符来自 google_material_font_filled_v4_0_0_0_original.ttf

    fun getGoogleMaterialIcons(): Map<String, Int> = mapOf(
        "3d_rotation" to R.string.aar_gm_3d_rotation,
        "accessibility" to R.string.aar_gm_accessibility,
        "account_balance" to R.string.aar_gm_account_balance,
        "alarm" to R.string.aar_gm_alarm,
        "alarm_add" to R.string.aar_gm_alarm_add,
        "alarm_off" to R.string.aar_gm_alarm_off,
        "alarm_on" to R.string.aar_gm_alarm_on,
        "all_out" to R.string.aar_gm_all_out,
        "android" to R.string.aar_gm_android,
        "announcement" to R.string.aar_gm_announcement,
        "apps" to R.string.aar_gm_apps,
        "archive" to R.string.aar_gm_archive,
    )

    // ── 混合使用演示 ──

    fun getAllAarIcons(): List<Int> = listOf(
        // FontAwesome
        R.string.aar_fa_heart,
        R.string.aar_fa_user,
        R.string.aar_fa_home,
        R.string.aar_fa_cog,
        // Google Material
        R.string.aar_gm_android,
        R.string.aar_gm_apps,
        R.string.aar_gm_archive,
        R.string.aar_gm_alarm,
    )

    fun selectIcon(useFontAwesome: Boolean): Int {
        return if (useFontAwesome) {
            R.string.aar_fa_heart
        } else {
            R.string.aar_gm_android
        }
    }
}
