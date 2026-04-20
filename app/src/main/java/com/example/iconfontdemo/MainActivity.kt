package com.example.iconfontdemo

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import com.example.iconfontlib.IconFontHelper

class MainActivity : AppCompatActivity() {

    private lateinit var iconFontManager: IconFontManager

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // 初始化图标管理器
        iconFontManager = IconFontManager(this)

        // 动态设置IconFont示例 - 这些代码中的字符串引用将被插件识别
        setupIconFonts()

        // 演示更多使用场景
        demonstrateAdvancedUsage()
    }

    private fun setupIconFonts() {
        // 通过代码设置iconfont字符 - 使用R.string引用
        val iconHome = findViewById<IconFontTextView>(R.id.icon_home_code)
        iconHome?.text = getString(R.string.icon_home)

        val iconSettings = findViewById<IconFontTextView>(R.id.icon_settings_code)
        iconSettings?.text = getString(R.string.icon_settings)

        // 直接设置Unicode码点
        val iconFavorite = findViewById<IconFontTextView>(R.id.icon_favorite_code)
        iconFavorite?.setIconText(0xE87D) // Material Icons favorite

        // 通过十六进制字符串设置
        val iconSearch = findViewById<IconFontTextView>(R.id.icon_search_code)
        iconSearch?.setIconText("E8B6") // Material Icons search

        // FontAwesome 图标示例
        val faIconHeart = findViewById<IconFontTextView>(R.id.fa_icon_heart_code)
        faIconHeart?.text = getString(R.string.fa_icon_heart)
        faIconHeart?.setIconFont(IconFontTextView.Companion.FontType.FONT_AWESOME)

        val faIconStar = findViewById<IconFontTextView>(R.id.fa_icon_star_code)
        faIconStar?.text = getString(R.string.fa_icon_star)
        faIconStar?.setIconFont(IconFontTextView.Companion.FontType.FONT_AWESOME)

        // 设置颜色示例
        val iconAdd = findViewById<IconFontTextView>(R.id.icon_add_code)
        iconAdd?.text = getString(R.string.icon_add)
        iconAdd?.setTextColor(ContextCompat.getColor(this, R.color.purple_500))

        // 演示字符串拼接
        val combinedIcon = getString(R.string.icon_play) + " " + getString(R.string.demo_text)
        val iconCombined = findViewById<IconFontTextView>(R.id.icon_combined_code)
        iconCombined?.text = combinedIcon
    }

    /**
     * 演示更高级的iconfont使用场景
     */
    private fun demonstrateAdvancedUsage() {
        // 使用IconFontManager的方法 - 这些也包含R.string引用
        val allIcons = iconFontManager.getAllMainIcons()
        val materialIcons = iconFontManager.getMaterialIcons2()
        val fontAwesomeIcons = iconFontManager.getFontAwesomeIcons()

        // 从AAR库获取图标 - 演示跨模块引用
        val libraryIcons = iconFontManager.getLibraryIcons()

        // 条件性图标选择
        val isPlaying = false
        val playPauseIcon = if (isPlaying) {
            getString(R.string.aar_fa_refresh) // 这个R.string引用也会被识别
        } else {
            getString(R.string.icon_play)  // 这个也是
        }

        // 使用IconFontHelper中的方法
        val libraryIconByName = IconFontHelper.getIconByName(this, "lib_activity")

        // 数组中的R.string引用
        val iconArray = arrayOf(
            getString(R.string.icon_delete),
            getString(R.string.icon_edit),
            getString(R.string.icon_share),
            getString(R.string.icon_download),
            getString(R.string.icon_upload)
        )

        // List中的R.string引用
        val iconList = listOf(
            getString(R.string.icon_refresh),
            getString(R.string.icon_delete),
            getString(R.string.mat_icon_menu),
            getString(R.string.mat_icon_close),
            getString(R.string.mat_icon_check)
        )

        // Map中的R.string引用
        val iconMap = mapOf(
            "navigation_home" to getString(R.string.icon_home),
            "navigation_search" to getString(R.string.icon_search),
            "action_settings" to getString(R.string.icon_settings),
            "user_profile" to getString(R.string.icon_person)
        )

        // 函数调用中的R.string引用
        setupCustomIcon(getString(R.string.fa_icon_cog))
        updateIconDisplay(getString(R.string.fa_icon_star))

        // 三元运算符中的R.string引用
        val statusIcon = if (System.currentTimeMillis() % 2 == 0L)
            getString(R.string.icon_favorite) else getString(R.string.icon_add)
    }

    /**
     * 自定义函数接收icon字符串
     */
    private fun setupCustomIcon(iconString: String) {
        // 使用传入的icon字符串
    }

    /**
     * 更新图标显示
     */
    private fun updateIconDisplay(iconChar: String) {
        // 更新UI中的图标显示
    }
}