Add-Type -AssemblyName System.Drawing

$ErrorActionPreference = "Stop"

$RootDir = "D:\codex_workspace\legend-of-warriors-master"
$OutFile = Join-Path $RootDir "主程序流程图_简化清晰版.png"

$width = 1400
$height = 1900
$bmp = New-Object System.Drawing.Bitmap($width, $height)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$g.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit
$g.Clear([System.Drawing.Color]::White)

$black = [System.Drawing.Color]::Black
$white = [System.Drawing.Color]::White
$pen = New-Object System.Drawing.Pen($black, 3)
$brush = New-Object System.Drawing.SolidBrush($black)
$whiteBrush = New-Object System.Drawing.SolidBrush($white)

$font = New-Object System.Drawing.Font("SimSun", 24, [System.Drawing.FontStyle]::Regular)
$smallFont = New-Object System.Drawing.Font("SimSun", 20, [System.Drawing.FontStyle]::Regular)
$tinyFont = New-Object System.Drawing.Font("SimSun", 17, [System.Drawing.FontStyle]::Regular)
$captionFont = New-Object System.Drawing.Font("SimSun", 26, [System.Drawing.FontStyle]::Regular)

$sf = New-Object System.Drawing.StringFormat
$sf.Alignment = [System.Drawing.StringAlignment]::Center
$sf.LineAlignment = [System.Drawing.StringAlignment]::Center
$sf.FormatFlags = [System.Drawing.StringFormatFlags]::LineLimit

function Draw-TextBox {
    param([int]$X, [int]$Y, [int]$W, [int]$H, [string]$Text, [System.Drawing.Font]$UseFont = $font)
    $rect = New-Object System.Drawing.Rectangle($X, $Y, $W, $H)
    $textRect = New-Object System.Drawing.RectangleF($X, $Y, $W, $H)
    $g.FillRectangle($whiteBrush, $rect)
    $g.DrawRectangle($pen, $rect)
    $g.DrawString($Text, $UseFont, $brush, $textRect, $sf)
}

function Draw-EllipseNode {
    param([int]$X, [int]$Y, [int]$W, [int]$H, [string]$Text)
    $rect = New-Object System.Drawing.Rectangle($X, $Y, $W, $H)
    $textRect = New-Object System.Drawing.RectangleF($X, $Y, $W, $H)
    $g.FillEllipse($whiteBrush, $rect)
    $g.DrawEllipse($pen, $rect)
    $g.DrawString($Text, $font, $brush, $textRect, $sf)
}

function Draw-Diamond {
    param([int]$Cx, [int]$Cy, [int]$W, [int]$H, [string]$Text)
    $pts = @(
        (New-Object System.Drawing.Point($Cx, ($Cy - [int]($H / 2)))),
        (New-Object System.Drawing.Point(($Cx + [int]($W / 2)), $Cy)),
        (New-Object System.Drawing.Point($Cx, ($Cy + [int]($H / 2)))),
        (New-Object System.Drawing.Point(($Cx - [int]($W / 2)), $Cy))
    )
    $g.FillPolygon($whiteBrush, $pts)
    $g.DrawPolygon($pen, $pts)
    $rect = New-Object System.Drawing.RectangleF(($Cx - [int]($W * 0.34)), ($Cy - [int]($H * 0.24)), [int]($W * 0.68), [int]($H * 0.48))
    $g.DrawString($Text, $smallFont, $brush, $rect, $sf)
}

function Draw-Label {
    param([int]$X, [int]$Y, [string]$Text, [int]$W = 180)
    $rect = New-Object System.Drawing.RectangleF($X, $Y, $W, 32)
    $g.DrawString($Text, $tinyFont, $brush, $rect, $sf)
}

function Draw-ArrowHead {
    param([int]$X1, [int]$Y1, [int]$X2, [int]$Y2)
    $angle = [Math]::Atan2($Y2 - $Y1, $X2 - $X1)
    $len = 15
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
        $g.DrawLine($pen, $Coords[$i], $Coords[$i + 1], $Coords[$i + 2], $Coords[$i + 3])
    }
    $n = $Coords.Count
    Draw-ArrowHead $Coords[$n - 4] $Coords[$n - 3] $Coords[$n - 2] $Coords[$n - 1]
}

$cx = 700

Draw-EllipseNode 590 40 220 85 "开始"
Draw-Arrow $cx 125 $cx 185
Draw-TextBox 560 185 280 85 "进入主菜单"
Draw-Arrow $cx 270 $cx 325
Draw-Diamond $cx 400 300 150 "选择游戏方式"

Draw-Label 380 360 "新游戏"
Draw-PolylineArrow @(550,400,360,400,360,515)
Draw-TextBox 230 515 260 90 "初始化角色、场景`n和基础数据" $smallFont
Draw-PolylineArrow @(490,560,560,560,560,670)

Draw-Label 845 360 "继续游戏"
Draw-PolylineArrow @(850,400,1040,400,1040,515)
Draw-TextBox 910 515 260 90 "读取本地存档" $smallFont
Draw-Arrow 1040 605 1040 665
Draw-Diamond 1040 735 240 140 "存档有效"
Draw-Label 1115 700 "否"
Draw-PolylineArrow @(1160,735,1265,735,1265,228,840,228)
Draw-Label 900 700 "是"
Draw-PolylineArrow @(920,735,840,735,840,560,840,560)

Draw-TextBox 560 670 280 90 "加载游戏场景`n定位玩家角色" $smallFont
Draw-Arrow $cx 760 $cx 830
Draw-TextBox 560 830 280 85 "进入游戏探索"
Draw-Arrow $cx 915 $cx 980
Draw-Diamond $cx 1055 310 150 "触发游戏事件"

Draw-Label 330 1015 "战斗"
Draw-PolylineArrow @(545,1055,360,1055,360,1190)
Draw-TextBox 225 1190 270 85 "执行战斗判定"
Draw-Arrow 360 1275 360 1335
Draw-Diamond 360 1410 240 140 "角色死亡"
Draw-Label 450 1375 "否"
Draw-PolylineArrow @(480,1410,560,1410,560,1510)
Draw-Label 245 1375 "是"
Draw-Arrow 360 1480 360 1540
Draw-TextBox 225 1540 270 85 "显示失败界面"
Draw-PolylineArrow @(360,1625,360,1740,560,1740)

Draw-Arrow $cx 1130 $cx 1190
Draw-TextBox 560 1190 280 85 "处理传送、存档`n道具与机关" $smallFont
Draw-Arrow $cx 1275 $cx 1350
Draw-TextBox 560 1350 280 85 "刷新角色、敌人、UI`n相机与场景状态" $smallFont
Draw-Arrow $cx 1435 $cx 1505

Draw-Label 900 1015 "暂停/返回"
Draw-PolylineArrow @(855,1055,1040,1055,1040,1190)
Draw-TextBox 905 1190 270 85 "暂停或设置界面"
Draw-Arrow 1040 1275 1040 1335
Draw-Diamond 1040 1410 240 140 "返回主菜单"
Draw-Label 1115 1375 "是"
Draw-PolylineArrow @(1160,1410,1265,1410,1265,228,840,228)
Draw-Label 925 1375 "否"
Draw-PolylineArrow @(920,1410,840,1410,840,1510)

Draw-Diamond $cx 1580 300 150 "是否结束游戏"
Draw-Label 790 1540 "是"
Draw-PolylineArrow @(850,1580,1040,1580,1040,1740,840,1740)
Draw-Label 495 1540 "否"
Draw-PolylineArrow @(550,1580,490,1580,490,955,700,955)

Draw-EllipseNode 560 1740 280 85 "返回主菜单"
Draw-PolylineArrow @(840,1782,1265,1782,1265,228,840,228)

$captionRect = New-Object System.Drawing.RectangleF(0, 1835, $width, 45)
$g.DrawString("图  主程序流程图", $captionFont, $brush, $captionRect, $sf)

$bmp.Save($OutFile, [System.Drawing.Imaging.ImageFormat]::Png)

$g.Dispose()
$bmp.Dispose()
$pen.Dispose()
$brush.Dispose()
$whiteBrush.Dispose()
$font.Dispose()
$smallFont.Dispose()
$tinyFont.Dispose()
$captionFont.Dispose()

Write-Output $OutFile
