package com.example.iconfontlib

import android.content.Context
import android.graphics.Typeface
import android.widget.TextView

/**
 * IconFontHelper - AAR库中的图标字体工具类
 * 这个类中的字符串引用也将被插件识别并预览
 */
object IconFontHelper {

    private var featherIconsTypeface: Typeface? = null

    /**
     * 获取Feather Icons字体
     */
    fun getFeatherIconsTypeface(context: Context): Typeface? {
        if (featherIconsTypeface == null) {
            try {
                featherIconsTypeface = Typeface.createFromAsset(
                    context.assets,
                    "fonts/feather_icons.ttf"
                )
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
        return featherIconsTypeface
    }

    /**
     * 设置TextView使用Feather Icons字体
     */
    fun setFeatherIcon(context: Context, textView: TextView, iconRes: Int) {
        textView.typeface = getFeatherIconsTypeface(context)
        textView.text = context.getString(iconRes)
    }

    /**
     * 获取AAR库中的图标字符串 - 这些R.string引用将被插件识别
     */
    fun getLibraryIcons(context: Context): Map<String, String> {
        return mapOf(
            "activity" to context.getString(R.string.lib_icon_activity),
            "airplay" to context.getString(R.string.lib_icon_airplay),
            "alert_circle" to context.getString(R.string.lib_icon_alert_circle),
            "alert_triangle" to context.getString(R.string.lib_icon_alert_triangle),
            "archive" to context.getString(R.string.lib_icon_archive),
            "arrow_down" to context.getString(R.string.lib_icon_arrow_down),
            "arrow_left" to context.getString(R.string.lib_icon_arrow_left),
            "arrow_right" to context.getString(R.string.lib_icon_arrow_right),
            "arrow_up" to context.getString(R.string.lib_icon_arrow_up),
            "battery" to context.getString(R.string.lib_icon_battery)
        )
    }

    /**
     * 获取Ionicons图标 - 这些R.string引用也将被插件识别
     */
    fun getIonicons(context: Context): Map<String, String> {
        return mapOf(
            "home" to context.getString(R.string.lib_ionicon_home),
            "user" to context.getString(R.string.lib_ionicon_user),
            "search" to context.getString(R.string.lib_ionicon_search),
            "settings" to context.getString(R.string.lib_ionicon_settings),
            "heart" to context.getString(R.string.lib_ionicon_heart),
            "camera" to context.getString(R.string.lib_ionicon_camera),
            "location" to context.getString(R.string.lib_ionicon_location),
            "phone" to context.getString(R.string.lib_ionicon_phone),
            "mail" to context.getString(R.string.lib_ionicon_mail),
            "calendar" to context.getString(R.string.lib_ionicon_calendar)
        )
    }

    /**
     * 批量应用图标到TextView列表
     */
    fun applyIconsToViews(context: Context, iconMap: Map<TextView, Int>) {
        iconMap.forEach { (textView, iconRes) ->
            setFeatherIcon(context, textView, iconRes)
        }
    }

    /**
     * 根据名称获取图标字符串
     */
    fun getIconByName(context: Context, iconName: String): String? {
        return when (iconName) {
            "lib_activity" -> context.getString(R.string.lib_icon_activity)
            "lib_airplay" -> context.getString(R.string.lib_icon_airplay)
            "lib_alert_circle" -> context.getString(R.string.lib_icon_alert_circle)
            "lib_alert_triangle" -> context.getString(R.string.lib_icon_alert_triangle)
            "lib_archive" -> context.getString(R.string.lib_icon_archive)
            "lib_arrow_down" -> context.getString(R.string.lib_icon_arrow_down)
            "lib_arrow_left" -> context.getString(R.string.lib_icon_arrow_left)
            "lib_arrow_right" -> context.getString(R.string.lib_icon_arrow_right)
            "lib_arrow_up" -> context.getString(R.string.lib_icon_arrow_up)
            "lib_battery" -> context.getString(R.string.lib_icon_battery)
            else -> null
        }
    }
}