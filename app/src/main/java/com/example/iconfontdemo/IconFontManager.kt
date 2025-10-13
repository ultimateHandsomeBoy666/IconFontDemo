package com.example.iconfontdemo

import android.content.Context
import android.widget.TextView
import com.example.iconfontlib.IconFontHelper

/**
 * IconFontManager - 管理应用中所有iconfont的使用
 * 这个类演示了在代码中大量使用R.string引用iconfont字符的情况
 */
class IconFontManager(private val context: Context) {

    /**
     * 获取所有主应用的图标 - 这些R.string引用将被插件识别
     */
    fun getAllMainIcons(): Map<String, String> {
        return mapOf(
            "home" to context.getString(R.string.icon_home),
            "search" to context.getString(R.string.icon_search),
            "favorite" to context.getString(R.string.icon_favorite),
            "settings" to context.getString(R.string.icon_settings),
            "person" to context.getString(R.string.icon_person),
            "add" to context.getString(R.string.icon_add),
            "delete" to context.getString(R.string.icon_delete),
            "edit" to context.getString(R.string.icon_edit),
            "share" to context.getString(R.string.icon_share),
            "download" to context.getString(R.string.icon_download),
            "upload" to context.getString(R.string.icon_upload),
            "play" to context.getString(R.string.icon_play),
            "pause" to context.getString(R.string.icon_pause),
            "stop" to context.getString(R.string.icon_stop),
            "refresh" to context.getString(R.string.icon_refresh)
        )
    }

    /**
     * 获取Material Icons 2的图标 - 使用了不同的字符串格式
     */
    fun getMaterialIcons2(): Map<String, String> {
        return mapOf(
            "mat_home" to context.getString(R.string.mat_icon_home),
            "mat_menu" to context.getString(R.string.mat_icon_menu),
            "mat_close" to context.getString(R.string.mat_icon_close),
            "mat_check" to context.getString(R.string.mat_icon_check)
        )
    }

    /**
     * 获取FontAwesome图标
     */
    fun getFontAwesomeIcons(): Map<String, String> {
        return mapOf(
            "fa_heart" to context.getString(R.string.fa_icon_heart),
            "fa_star" to context.getString(R.string.fa_icon_star),
            "fa_user" to context.getString(R.string.fa_icon_user),
            "fa_cog" to context.getString(R.string.fa_icon_cog)
        )
    }

    /**
     * 从AAR库获取图标 - 演示跨模块的R.string引用
     */
    fun getLibraryIcons(): Map<String, String> {
        return IconFontHelper.getLibraryIcons(context)
    }

    /**
     * 设置TextView的图标文本
     */
    fun setIconToTextView(textView: TextView, iconType: IconType, iconName: String) {
        val iconText = when (iconType) {
            IconType.MATERIAL_DESIGN -> {
                when (iconName) {
                    "home" -> context.getString(R.string.icon_home)
                    "search" -> context.getString(R.string.icon_search)
                    "favorite" -> context.getString(R.string.icon_favorite)
                    "settings" -> context.getString(R.string.icon_settings)
                    "person" -> context.getString(R.string.icon_person)
                    "add" -> context.getString(R.string.icon_add)
                    else -> ""
                }
            }
            IconType.FONT_AWESOME -> {
                when (iconName) {
                    "heart" -> context.getString(R.string.fa_icon_heart)
                    "star" -> context.getString(R.string.fa_icon_star)
                    "user" -> context.getString(R.string.fa_icon_user)
                    "cog" -> context.getString(R.string.fa_icon_cog)
                    else -> ""
                }
            }
            IconType.LIBRARY_ICONS -> {
                IconFontHelper.getIconByName(context, iconName) ?: ""
            }
        }

        textView.text = iconText
    }

    /**
     * 批量设置图标
     */
    fun setupNavigationIcons(
        homeIcon: TextView,
        searchIcon: TextView,
        favoriteIcon: TextView,
        settingsIcon: TextView
    ) {
        // 这些getString调用也会被插件识别
        homeIcon.text = context.getString(R.string.icon_home)
        searchIcon.text = context.getString(R.string.icon_search)
        favoriteIcon.text = context.getString(R.string.icon_favorite)
        settingsIcon.text = context.getString(R.string.icon_settings)
    }

    /**
     * 创建图标字符串组合
     */
    fun createIconCombination(): String {
        // 字符串拼接中的R.string引用也应该被识别
        return context.getString(R.string.icon_home) + " " +
               context.getString(R.string.icon_search) + " " +
               context.getString(R.string.icon_favorite)
    }

    /**
     * 根据条件获取图标
     */
    fun getConditionalIcon(condition: Boolean): String {
        return if (condition) {
            context.getString(R.string.icon_play)
        } else {
            context.getString(R.string.icon_pause)
        }
    }

    /**
     * 图标类型枚举
     */
    enum class IconType {
        MATERIAL_DESIGN,
        FONT_AWESOME,
        LIBRARY_ICONS
    }
}