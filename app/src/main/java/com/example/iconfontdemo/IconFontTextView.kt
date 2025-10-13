package com.example.iconfontdemo

import android.content.Context
import android.graphics.Typeface
import android.util.AttributeSet
import androidx.appcompat.widget.AppCompatTextView

/**
 * IconFontTextView - 用于显示IconFont字符的自定义TextView
 * 支持从assets/fonts目录加载字体文件
 */
class IconFontTextView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : AppCompatTextView(context, attrs, defStyleAttr) {

    companion object {
        private var materialIconsTypeface: Typeface? = null
        private var fontAwesomeTypeface: Typeface? = null

        // 字体类型枚举
        enum class FontType {
            MATERIAL_ICONS,
            FONT_AWESOME
        }
    }

    init {
        // 解析自定义属性
        val typedArray = context.obtainStyledAttributes(attrs, R.styleable.IconFontTextView)
        val fontType = typedArray.getInt(R.styleable.IconFontTextView_iconFont, 0)

        when (fontType) {
            0 -> setIconFont(FontType.MATERIAL_ICONS)
            1 -> setIconFont(FontType.FONT_AWESOME)
        }

        typedArray.recycle()
    }

    /**
     * 设置图标字体类型
     */
    fun setIconFont(fontType: FontType) {
        val typeface = when (fontType) {
            FontType.MATERIAL_ICONS -> getMaterialIconsTypeface()
            FontType.FONT_AWESOME -> getFontAwesomeTypeface()
        }
        this.typeface = typeface
    }

    /**
     * 获取Material Icons字体
     */
    private fun getMaterialIconsTypeface(): Typeface? {
        if (materialIconsTypeface == null) {
            try {
                materialIconsTypeface = Typeface.createFromAsset(
                    context.assets,
                    "fonts/material_icons.ttf"
                )
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
        return materialIconsTypeface
    }

    /**
     * 获取FontAwesome字体
     */
    private fun getFontAwesomeTypeface(): Typeface? {
        if (fontAwesomeTypeface == null) {
            try {
                fontAwesomeTypeface = Typeface.createFromAsset(
                    context.assets,
                    "fonts/fontawesome.ttf"
                )
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
        return fontAwesomeTypeface
    }

    /**
     * 设置图标文本（支持Unicode码点）
     */
    fun setIconText(unicodePoint: Int) {
        text = String(Character.toChars(unicodePoint))
    }

    /**
     * 设置图标文本（支持十六进制字符串）
     */
    fun setIconText(hexString: String) {
        try {
            val codePoint = hexString.replace("0x", "").replace("#", "").toInt(16)
            setIconText(codePoint)
        } catch (e: NumberFormatException) {
            e.printStackTrace()
        }
    }
}