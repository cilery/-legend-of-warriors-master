Add-Type -AssemblyName System.Drawing

$ErrorActionPreference = "Stop"

$RootDir = "D:\codex_workspace\legend-of-warriors-master"
$OutFile = Join-Path $RootDir "主程序流程图_无交叉精简版.png"

$width = 1350
$height = 1750
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

function Draw-Connector {
    param([int]$X, [int]$Y, [string]$Text)
    Draw-EllipseNode $X $Y 70 70 $Text $smallFont
}

function Draw-Label {
    param([int]$X, [int]$Y, [string]$Text, [int]$W = 160)
    $rect = New-Object System.Drawing.RectangleF($X, $Y, $W, 30)
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

$cx = 675

Draw-EllipseNode 565 35 220 82 "开始"
Draw-Arrow $cx 117 $cx 175
Draw-TextBox 535 175 280 82 "进入主菜单"
Draw-Arrow $cx 257 $cx 315
Draw-Diamond $cx 385 300 140 "选择游戏方式"

Draw-Label 380 345 "新游戏"
Draw-PolylineArrow @(525,385,330,385,330,500)
Draw-TextBox 205 500 250 82 "初始化游戏数据" $smallFont
Draw-PolylineArrow @(455,541,535,541,535,640)

Draw-Label 815 345 "继续游戏"
Draw-PolylineArrow @(825,385,1020,385,1020,500)
Draw-TextBox 895 500 250 82 "读取本地存档" $smallFont
Draw-Arrow 1020 582 1020 640
Draw-Diamond 1020 705 230 130 "存档有效"
Draw-Label 1088 665 "否"
Draw-PolylineArrow @(1135,705,1215,705,1215,216,815,216)
Draw-Label 862 665 "是"
Draw-PolylineArrow @(905,705,815,705,815,640)

Draw-TextBox 535 640 280 88 "加载场景`n定位玩家角色" $smallFont
Draw-Arrow $cx 728 $cx 785
Draw-Connector 640 785 "A"
Draw-Arrow $cx 855 $cx 910
Draw-TextBox 535 910 280 82 "进入游戏探索"
Draw-Arrow $cx 992 $cx 1050
Draw-Diamond $cx 1120 300 140 "处理游戏事件"

Draw-Label 292 1080 "战斗事件"
Draw-PolylineArrow @(525,1120,330,1120,330,1235)
Draw-TextBox 195 1235 270 90 "战斗判定`n伤害结算" $smallFont
Draw-Arrow 330 1325 330 1385
Draw-Diamond 330 1450 230 130 "角色死亡"
Draw-Label 398 1410 "是"
Draw-PolylineArrow @(445,1450,505,1450,505,1570)
Draw-Label 210 1410 "否"
Draw-PolylineArrow @(330,1515,330,1580,535,1580)

Draw-Arrow $cx 1190 $cx 1235
Draw-TextBox 535 1235 280 90 "处理传送、存档`n道具与机关" $smallFont
Draw-Arrow $cx 1325 $cx 1400

Draw-Label 900 1080 "界面事件"
Draw-PolylineArrow @(825,1120,1020,1120,1020,1235)
Draw-TextBox 885 1235 270 90 "暂停、设置`n返回操作" $smallFont
Draw-Arrow 1020 1325 1020 1385
Draw-Diamond 1020 1450 230 130 "返回主菜单"
Draw-Label 1088 1410 "是"
Draw-PolylineArrow @(1135,1450,1215,1450,1215,1620,815,1620)
Draw-Label 905 1410 "否"
Draw-PolylineArrow @(905,1450,815,1450,815,1580)

Draw-TextBox 535 1400 280 90 "刷新角色、敌人、UI`n相机与场景状态" $smallFont
Draw-Arrow $cx 1490 $cx 1545
Draw-Diamond $cx 1610 250 120 "继续游戏"
Draw-Label 755 1570 "否"
Draw-Arrow 800 1610 815 1610
Draw-EllipseNode 815 1568 250 85 "返回主菜单"
Draw-Label 548 1570 "是"
Draw-PolylineArrow @(550,1610,470,1610,470,820,640,820)

Draw-TextBox 505 1570 300 90 "显示失败或结束界面" $smallFont

$captionRect = New-Object System.Drawing.RectangleF(0, 1690, $width, 42)
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
