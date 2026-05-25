Add-Type -AssemblyName System.Drawing

$ErrorActionPreference = "Stop"

$RootDir = "D:\codex_workspace\legend-of-warriors-master"
$OutFile = Join-Path $RootDir "主程序流程图_论文风格_结合论文内容.png"

$width = 1700
$height = 2250
$bmp = New-Object System.Drawing.Bitmap($width, $height)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$g.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit
$g.Clear([System.Drawing.Color]::White)

$black = [System.Drawing.Color]::Black
$white = [System.Drawing.Color]::White
$pen = New-Object System.Drawing.Pen($black, 3)
$thinPen = New-Object System.Drawing.Pen($black, 2)
$brush = New-Object System.Drawing.SolidBrush($black)
$whiteBrush = New-Object System.Drawing.SolidBrush($white)

$fontPath = "C:\Windows\Fonts\simsun.ttc"
$titleFont = New-Object System.Drawing.Font("SimSun", 26, [System.Drawing.FontStyle]::Regular)
$font = New-Object System.Drawing.Font("SimSun", 24, [System.Drawing.FontStyle]::Regular)
$smallFont = New-Object System.Drawing.Font("SimSun", 19, [System.Drawing.FontStyle]::Regular)
$tinyFont = New-Object System.Drawing.Font("SimSun", 17, [System.Drawing.FontStyle]::Regular)

$sf = New-Object System.Drawing.StringFormat
$sf.Alignment = [System.Drawing.StringAlignment]::Center
$sf.LineAlignment = [System.Drawing.StringAlignment]::Center
$sf.FormatFlags = [System.Drawing.StringFormatFlags]::LineLimit

function Draw-TextBox {
    param(
        [int]$X, [int]$Y, [int]$W, [int]$H,
        [string]$Text,
        [System.Drawing.Font]$UseFont = $font
    )
    $rect = New-Object System.Drawing.Rectangle($X, $Y, $W, $H)
    $textRect = New-Object System.Drawing.RectangleF($X, $Y, $W, $H)
    $g.FillRectangle($whiteBrush, $rect)
    $g.DrawRectangle($pen, $rect)
    $g.DrawString($Text, $UseFont, $brush, $textRect, $sf)
}

function Draw-EllipseNode {
    param(
        [int]$X, [int]$Y, [int]$W, [int]$H,
        [string]$Text,
        [System.Drawing.Font]$UseFont = $font
    )
    $rect = New-Object System.Drawing.Rectangle($X, $Y, $W, $H)
    $textRect = New-Object System.Drawing.RectangleF($X, $Y, $W, $H)
    $g.FillEllipse($whiteBrush, $rect)
    $g.DrawEllipse($pen, $rect)
    $g.DrawString($Text, $UseFont, $brush, $textRect, $sf)
}

function Draw-Diamond {
    param(
        [int]$Cx, [int]$Cy, [int]$W, [int]$H,
        [string]$Text,
        [System.Drawing.Font]$UseFont = $smallFont
    )
    $pts = @(
        (New-Object System.Drawing.Point($Cx, ($Cy - [int]($H / 2)))),
        (New-Object System.Drawing.Point(($Cx + [int]($W / 2)), $Cy)),
        (New-Object System.Drawing.Point($Cx, ($Cy + [int]($H / 2)))),
        (New-Object System.Drawing.Point(($Cx - [int]($W / 2)), $Cy))
    )
    $g.FillPolygon($whiteBrush, $pts)
    $g.DrawPolygon($pen, $pts)
    $rect = New-Object System.Drawing.RectangleF(($Cx - [int]($W * 0.32)), ($Cy - [int]($H * 0.25)), [int]($W * 0.64), [int]($H * 0.5))
    $g.DrawString($Text, $UseFont, $brush, $rect, $sf)
}

function Draw-Label {
    param([int]$X, [int]$Y, [string]$Text)
    $rect = New-Object System.Drawing.RectangleF($X, $Y, 230, 34)
    $g.DrawString($Text, $tinyFont, $brush, $rect, $sf)
}

function Draw-ArrowHead {
    param([int]$X1, [int]$Y1, [int]$X2, [int]$Y2)
    $angle = [Math]::Atan2($Y2 - $Y1, $X2 - $X1)
    $len = 16
    $spread = 0.55
    $p1 = New-Object System.Drawing.Point(
        [int]($X2 - $len * [Math]::Cos($angle - $spread)),
        [int]($Y2 - $len * [Math]::Sin($angle - $spread))
    )
    $p2 = New-Object System.Drawing.Point(
        [int]($X2 - $len * [Math]::Cos($angle + $spread)),
        [int]($Y2 - $len * [Math]::Sin($angle + $spread))
    )
    $p3 = New-Object System.Drawing.Point($X2, $Y2)
    $g.FillPolygon($brush, @($p1, $p2, $p3))
}

function Draw-Arrow {
    param([int]$X1, [int]$Y1, [int]$X2, [int]$Y2)
    $g.DrawLine($pen, $X1, $Y1, $X2, $Y2)
    Draw-ArrowHead $X1 $Y1 $X2 $Y2
}

function Draw-PolylineArrow {
    param([int[]]$Coords)
    for ($i = 0; $i -lt $Coords.Count - 2; $i += 2) {
        $x1 = $Coords[$i]
        $y1 = $Coords[$i + 1]
        $x2 = $Coords[$i + 2]
        $y2 = $Coords[$i + 3]
        $g.DrawLine($pen, $x1, $y1, $x2, $y2)
    }
    $n = $Coords.Count
    Draw-ArrowHead $Coords[$n - 4] $Coords[$n - 3] $Coords[$n - 2] $Coords[$n - 1]
}

# Top-level menu and loading flow.
Draw-EllipseNode 740 35 220 90 "开始"
Draw-Arrow 850 125 850 185
Draw-TextBox 720 185 260 90 "主菜单"
Draw-Arrow 850 275 850 330
Draw-Diamond 850 405 270 160 "用户操作"

Draw-Label 555 365 "开始新游戏"
Draw-PolylineArrow @(715,405,430,405,430,520)
Draw-TextBox 285 520 290 100 "初始化新游戏数据`n创建角色与场景状态" $smallFont
Draw-PolylineArrow @(575,570,710,570,710,690)

Draw-Label 990 365 "继续游戏"
Draw-PolylineArrow @(985,405,1250,405,1250,520)
Draw-TextBox 1105 520 290 90 "读取本地 JSON 存档" $smallFont
Draw-Arrow 1250 610 1250 675
Draw-Diamond 1250 750 250 150 "读取是否成功"
Draw-Arrow 1250 825 1250 850
Draw-Label 1010 708 "是"
Draw-TextBox 1030 850 360 100 "恢复场景、坐标`n生命值与对象状态" $smallFont
Draw-PolylineArrow @(1030,900,990,900,990,738)
Draw-PolylineArrow @(1375,750,1510,750,1510,230,980,230)
Draw-Label 1375 705 "否"

Draw-TextBox 710 690 280 95 "加载游戏场景`n并定位角色" $smallFont
Draw-Arrow 850 785 850 865
Draw-TextBox 720 865 260 90 "进入探索阶段"
Draw-Arrow 850 955 850 1020
Draw-Diamond 850 1095 310 160 "是否触发事件"

# Event branches.
Draw-Label 320 1028 "敌人/攻击"
Draw-PolylineArrow @(695,1095,270,1095,270,1235)
Draw-TextBox 135 1235 270 90 "战斗交互处理"
Draw-Arrow 270 1325 270 1395
Draw-Diamond 270 1470 240 145 "战斗结果"
Draw-Label 395 1415 "胜利"
Draw-PolylineArrow @(390,1470,520,1470,520,1620,680,1620)
Draw-Label 168 1565 "失败"
Draw-PolylineArrow @(270,1542,270,1705)
Draw-TextBox 120 1705 300 90 "显示 Game Over 界面"
Draw-Arrow 270 1795 270 1860
Draw-Diamond 270 1935 250 150 "用户选择"
Draw-Label 12 1925 "重新开始"
Draw-PolylineArrow @(145,1935,60,1935,60,515,285,515)
Draw-Label 390 1925 "返回主菜单"
Draw-PolylineArrow @(395,1935,500,1935,500,2210,1510,2210,1510,230,980,230)

Draw-Label 620 1130 "传送点"
Draw-PolylineArrow @(775,1170,620,1170,620,1235)
Draw-TextBox 485 1235 270 90 "场景切换处理"
Draw-Arrow 620 1325 620 1390
Draw-TextBox 485 1390 270 90 "黑幕过渡`n异步加载新场景" $smallFont
Draw-PolylineArrow @(620,1480,620,1620,680,1620)

Draw-Arrow 850 1175 850 1235
Draw-Label 780 1195 "存档点"
Draw-TextBox 715 1235 270 90 "存档处理"
Draw-Arrow 850 1325 850 1390
Draw-TextBox 715 1390 270 90 "序列化数据`n写入本地文件" $smallFont
Draw-Arrow 850 1480 850 1565

Draw-Label 970 1130 "宝箱/道具/机关"
Draw-PolylineArrow @(925,1170,1080,1170,1080,1235)
Draw-TextBox 945 1235 270 90 "道具拾取与`n机关处理" $smallFont
Draw-PolylineArrow @(1080,1325,1080,1620,1020,1620)

Draw-Label 1210 1028 "暂停/UI"
Draw-PolylineArrow @(1005,1095,1320,1095,1320,1235)
Draw-TextBox 1185 1235 270 90 "暂停、设置`n界面处理" $smallFont
Draw-PolylineArrow @(1320,1325,1320,1620,1020,1620)
Draw-PolylineArrow @(1455,1280,1510,1280,1510,230,980,230)
Draw-Label 1398 1332 "返回主菜单"

Draw-Label 1015 1070 "未触发"
Draw-PolylineArrow @(1005,1095,1510,1095,1510,1565,1020,1565)
Draw-TextBox 680 1565 340 110 "更新角色、敌人、UI`n相机与场景状态" $smallFont
Draw-Arrow 850 1675 850 1745
Draw-Diamond 850 1820 280 150 "是否结束游戏"
Draw-Label 950 1770 "结束/返回"
Draw-PolylineArrow @(990,1820,1260,1820,1260,1985)
Draw-EllipseNode 1135 1985 250 90 "返回主菜单"
Draw-PolylineArrow @(1260,1985,1510,1985,1510,230,980,230)
Draw-Label 610 1770 "继续游戏"
Draw-PolylineArrow @(710,1820,500,1820,500,1010,850,1010)

$captionRect = New-Object System.Drawing.RectangleF(0, 2168, $width, 50)
$g.DrawString("图  主程序流程图", $titleFont, $brush, $captionRect, $sf)

$bmp.Save($OutFile, [System.Drawing.Imaging.ImageFormat]::Png)

$g.Dispose()
$bmp.Dispose()
$pen.Dispose()
$thinPen.Dispose()
$brush.Dispose()
$whiteBrush.Dispose()
$titleFont.Dispose()
$font.Dispose()
$smallFont.Dispose()
$tinyFont.Dispose()

Write-Output $OutFile
