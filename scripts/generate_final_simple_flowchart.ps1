Add-Type -AssemblyName System.Drawing

$ErrorActionPreference = "Stop"

$RootDir = "D:\codex_workspace\legend-of-warriors-master"
$OutFile = Join-Path $RootDir "主程序流程图_终版简洁无交叉.png"

$width = 1200
$height = 1580
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

$font = New-Object System.Drawing.Font("SimSun", 23, [System.Drawing.FontStyle]::Regular)
$smallFont = New-Object System.Drawing.Font("SimSun", 19, [System.Drawing.FontStyle]::Regular)
$tinyFont = New-Object System.Drawing.Font("SimSun", 16, [System.Drawing.FontStyle]::Regular)
$captionFont = New-Object System.Drawing.Font("SimSun", 25, [System.Drawing.FontStyle]::Regular)

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
    param([int]$X, [int]$Y, [int]$W, [int]$H, [string]$Text, [System.Drawing.Font]$UseFont = $font)
    $rect = New-Object System.Drawing.Rectangle($X, $Y, $W, $H)
    $textRect = New-Object System.Drawing.RectangleF($X, $Y, $W, $H)
    $g.FillEllipse($whiteBrush, $rect)
    $g.DrawEllipse($pen, $rect)
    $g.DrawString($Text, $UseFont, $brush, $textRect, $sf)
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
    param([int]$X, [int]$Y, [string]$Text, [int]$W = 150)
    $rect = New-Object System.Drawing.RectangleF($X, $Y, $W, 28)
    $g.DrawString($Text, $tinyFont, $brush, $rect, $sf)
}

function Draw-ArrowHead {
    param([int]$X1, [int]$Y1, [int]$X2, [int]$Y2)
    $angle = [Math]::Atan2($Y2 - $Y1, $X2 - $X1)
    $len = 14
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

$cx = 600

Draw-EllipseNode 500 30 200 78 "开始"
Draw-Arrow $cx 108 $cx 165
Draw-TextBox 480 165 240 78 "主菜单"
Draw-Arrow $cx 243 $cx 300
Draw-Diamond $cx 365 270 130 "选择游戏方式"

Draw-Label 335 328 "新游戏"
Draw-PolylineArrow @(465,365,280,365,280,470)
Draw-TextBox 160 470 240 78 "初始化游戏数据" $smallFont
Draw-PolylineArrow @(400,509,480,509,480,590)

Draw-Label 722 328 "继续游戏"
Draw-PolylineArrow @(735,365,920,365,920,470)
Draw-TextBox 800 470 240 78 "读取本地存档" $smallFont
Draw-Arrow 920 548 920 605
Draw-Diamond 920 665 220 120 "存档有效"
Draw-Label 985 630 "否"
Draw-PolylineArrow @(1030,665,1110,665,1110,204,720,204)
Draw-Label 755 630 "是"
Draw-PolylineArrow @(810,665,720,665,720,590)

Draw-TextBox 480 590 240 82 "加载场景`n定位角色" $smallFont
Draw-Arrow $cx 672 $cx 730
Draw-TextBox 480 730 240 78 "进入游戏探索"
Draw-Arrow $cx 808 $cx 865
Draw-Diamond $cx 930 280 130 "触发事件类型"

Draw-Label 210 895 "战斗"
Draw-PolylineArrow @(460,930,240,930,240,1040)
Draw-TextBox 110 1040 260 85 "战斗判定`n伤害与失败处理" $smallFont

Draw-Label 520 995 "探索交互"
Draw-Arrow $cx 995 $cx 1040
Draw-TextBox 470 1040 260 85 "传送、存档`n道具与机关处理" $smallFont

Draw-Label 860 895 "界面"
Draw-PolylineArrow @(740,930,960,930,960,1040)
Draw-TextBox 830 1040 260 85 "暂停、设置`n返回操作" $smallFont

Draw-PolylineArrow @(240,1125,240,1180,600,1180,600,1225)
Draw-Arrow 600 1125 600 1225
Draw-PolylineArrow @(960,1125,960,1180,600,1180,600,1225)
Draw-TextBox 430 1225 340 88 "刷新角色、敌人、UI、`n相机与场景状态" $smallFont
Draw-Arrow $cx 1313 $cx 1365
Draw-Diamond $cx 1425 260 120 "继续游戏"

Draw-Label 710 1390 "否"
Draw-Arrow 730 1425 820 1425
Draw-EllipseNode 820 1385 240 80 "返回主菜单"

Draw-Label 340 1386 "是"
Draw-Arrow 470 1425 350 1425
Draw-EllipseNode 260 1385 90 80 "A" $smallFont
Draw-Label 200 1462 "转入探索阶段" 220
Draw-EllipseNode 325 730 90 78 "A" $smallFont
Draw-Arrow 415 769 480 769

$captionRect = New-Object System.Drawing.RectangleF(0, 1520, $width, 40)
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
