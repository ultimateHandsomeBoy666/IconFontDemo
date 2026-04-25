package com.example.iconfontdemo

import android.os.Bundle
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity

class FeatherIconDemo : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Feather Icons 引用 — 需要启用 feather_icons.ttf 字体才能看到 gutter 预览
        val activity = getString(R.string.feather_activity)
        val airplay = getString(R.string.feather_airplay)
        val alertCircle = getString(R.string.feather_alert_circle)
        val alertTriangle = getString(R.string.feather_alert_triangle)
        val anchor = getString(R.string.feather_anchor)
        val archive = getString(R.string.feather_archive)
        val arrowDown = getString(R.string.feather_arrow_down)
        val arrowLeft = getString(R.string.feather_arrow_left)
        val arrowRight = getString(R.string.feather_arrow_right)
        val arrowUp = getString(R.string.feather_arrow_up)
        val award = getString(R.string.feather_award)
        val bell = getString(R.string.feather_bell)
        val bluetooth = getString(R.string.feather_bluetooth)
        val book = getString(R.string.feather_book)
        val bookmark = getString(R.string.feather_bookmark)
    }
}
