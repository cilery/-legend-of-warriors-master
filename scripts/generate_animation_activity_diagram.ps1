Add-Type -AssemblyName System.Drawing

$ErrorActionPreference = "Stop"

$RootDir = "D:\codex_workspace\legend-of-warriors-master"
$OutFile = Join-Path $RootDir "动画管理活动图_黑白论文版.png"

$width = 1300
$height = 1750
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

$titleFont = New-Object System.Drawing.Font("SimSun", 28, [System.Drawing.FontStyle]::Bold)
$font = New-Object System.Drawing.Font("SimSun", 23, [System.Drawing.FontStyle]::Regular)
$smallFont = New-Object System.Drawing.Font("SimSun", 19, [System.Drawing.FontStyle]::Regular)
$tinyFont = New-Object System.Drawing.Font("SimSun", 16, [System.Drawing.FontStyle]::Regular)
$captionFont = New-Object System.Drawing.Font("SimSun", 25, [System.Drawing.FontStyle]::Regular)

$sf = New-Object System.Drawing.StringFormat
$sf.Alignment = [System.Drawing.StringAlignment]::Center
$sf.LineAlignment = [System.Drawing.StringAlignment]::Center
$sf.FormatFlags = [System.Drawing.StringFormatFlags]::LineLimit

function New-RoundedPath {
    param([int]$X, [int]$Y, [int]$W, [int]$H, [int]$R)
    $path = New-Object System.Drawing.Drawing2D.GraphicsPath
    $d = $R * 2
    $path.AddArc($X, $Y, $d, $d, 180, 90)
    $path.AddArc($X + $W - $d, $Y, $d, $d, 270, 90)
    $path.AddArc($X + $W - $d, $Y + $H - $d, $d, $d, 0, 90)
    $path.AddArc($X, $Y + $H - $d, $d, $d, 90, 90)
    $path.CloseFigure()
    return $path
}

function Draw-Action {
    param([int]$X, [int]$Y, [int]$W, [int]$H, [string]$Text, [System.Drawing.Font]$UseFont = $smallFont)
    $path = New-RoundedPath $X $Y $W $H 16
    $rect = New-Object System.Drawing.RectangleF($X, $Y, $W, $H)
    $g.FillPath($whiteBrush, $path)
    $g.DrawPath($pen, $path)
    $g.DrawString($Text, $UseFont, $brush, $rect, $sf)
    $path.Dispose()
}

function Draw-TextBox {
    param([int]$X, [int]$Y, [int]$W, [int]$H, [string]$Text, [System.Drawing.Font]$UseFont = $smallFont)
    $rect = New-Object System.Drawing.Rectangle($X, $Y, $W, $H)
    $textRect = New-Object System.Drawing.RectangleF($X, $Y, $W, $H)
    $g.FillRectangle($whiteBrush, $rect)
    $g.DrawRectangle($pen, $rect)
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
    $rect = New-Object System.Drawing.RectangleF(($Cx - [int]($W * 0.34)), ($Cy - [int]($H * 0.25)), [int]($W * 0.68), [int]($H * 0.5))
    $g.DrawString($Text, $smallFont, $brush, $rect, $sf)
}

function Draw-Label {
    param([int]$X, [int]$Y, [string]$Text, [int]$W = 170)
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

function Draw-Start {
    param([int]$Cx, [int]$Cy)
    $g.FillEllipse($brush, $Cx - 18, $Cy - 18, 36, 36)
}

function Draw-End {
    param([int]$Cx, [int]$Cy)
    $g.FillEllipse($brush, $Cx - 16, $Cy - 16, 32, 32)
    $g.DrawEllipse($pen, $Cx - 30, $Cy - 30, 60, 60)
}

$titleRect = New-Object System.Drawing.RectangleF(0, 35, $width, 42)
$g.DrawString("动画管理活动图", $titleFont, $brush, $titleRect, $sf)

$cx = 650

Draw-Start $cx 115
Draw-Arrow $cx 135 $cx 185
Draw-Action 485 185 330 76 "接收动画触发来源`n角色、敌人或场景模块"
Draw-Arrow $cx 261 $cx 318
Draw-Action 485 318 330 76 "读取当前状态数据`n速度、生命值、攻击、技能等"
Draw-Arrow $cx 394 $cx 452
Draw-Diamond $cx 520 300 136 "判断动画类型"

Draw-Label 245 485 "角色动作"
Draw-PolylineArrow @(500,520,260,520,260,650)
Draw-Action 115 650 290 86 "PlayerAnimation`n同步 Animator 参数"
Draw-Arrow 260 736 260 800
Draw-Action 115 800 290 86 "播放待机、奔跑、`n跳跃、攻击等动画"

Draw-Label 570 588 "受击/死亡"
Draw-Arrow $cx 588 $cx 650
Draw-Action 505 650 290 86 "触发受击或死亡动画`n清理冲突状态标记"
Draw-Arrow $cx 736 $cx 800
Draw-Action 505 800 290 86 "HurtAnimation 处理结束`n恢复可控制状态"

Draw-Label 900 485 "场景过渡"
Draw-PolylineArrow @(800,520,1040,520,1040,650)
Draw-Action 895 650 290 86 "FadeCanvas 监听事件`n接收淡入淡出请求"
Draw-Arrow 1040 736 1040 800
Draw-Action 895 800 290 86 "DOTween 执行黑幕`n颜色渐变动画"

$joinY = 990
$g.FillRectangle($brush, 205, $joinY, 890, 12)
Draw-Arrow 260 886 260 $joinY
Draw-Arrow $cx 886 $cx $joinY
Draw-Arrow 1040 886 1040 $joinY
Draw-Arrow $cx ($joinY + 12) $cx 1070

Draw-Diamond $cx 1140 300 136 "动画是否结束"
Draw-Label 780 1105 "否"
Draw-PolylineArrow @(800,1140,1125,1140,1125,980,1040,980)
Draw-Label 525 1210 "是"
Draw-Arrow $cx 1208 $cx 1270
Draw-Action 485 1270 330 84 "执行动画结束逻辑`n重置 Animator 参数"
Draw-Arrow $cx 1354 $cx 1415
Draw-Action 485 1415 330 84 "更新角色、敌人或界面状态`n返回正常流程"
Draw-Arrow $cx 1499 $cx 1560
Draw-End $cx 1600

$captionRect = New-Object System.Drawing.RectangleF(0, 1678, $width, 42)
$g.DrawString("图  动画管理活动图", $captionFont, $brush, $captionRect, $sf)

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
$captionFont.Dispose()

Write-Output $OutFile
