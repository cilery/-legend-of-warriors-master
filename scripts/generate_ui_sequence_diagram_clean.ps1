Add-Type -AssemblyName System.Drawing

$ErrorActionPreference = "Stop"

$RootDir = "D:\codex_workspace\legend-of-warriors-master"
$OutFile = Join-Path $RootDir "UI界面交互UML顺序图_无交叉优化版.png"

$width = 1500
$height = 1500
$bmp = New-Object System.Drawing.Bitmap($width, $height)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$g.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit
$g.Clear([System.Drawing.Color]::White)

$black = [System.Drawing.Color]::Black
$white = [System.Drawing.Color]::White
$pen = New-Object System.Drawing.Pen($black, 3)
$thinPen = New-Object System.Drawing.Pen($black, 2)
$dashPen = New-Object System.Drawing.Pen($black, 2)
$dashPen.DashStyle = [System.Drawing.Drawing2D.DashStyle]::Dash
$brush = New-Object System.Drawing.SolidBrush($black)
$whiteBrush = New-Object System.Drawing.SolidBrush($white)
$lightBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(246,246,246))

$titleFont = New-Object System.Drawing.Font("SimSun", 30, [System.Drawing.FontStyle]::Bold)
$headerFont = New-Object System.Drawing.Font("SimSun", 17, [System.Drawing.FontStyle]::Bold)
$font = New-Object System.Drawing.Font("SimSun", 17, [System.Drawing.FontStyle]::Regular)
$smallFont = New-Object System.Drawing.Font("SimSun", 15, [System.Drawing.FontStyle]::Regular)
$captionFont = New-Object System.Drawing.Font("SimSun", 24, [System.Drawing.FontStyle]::Regular)

$sfCenter = New-Object System.Drawing.StringFormat
$sfCenter.Alignment = [System.Drawing.StringAlignment]::Center
$sfCenter.LineAlignment = [System.Drawing.StringAlignment]::Center
$sfCenter.FormatFlags = [System.Drawing.StringFormatFlags]::LineLimit

function Draw-Text {
    param([int]$X, [int]$Y, [int]$W, [int]$H, [string]$Text, [System.Drawing.Font]$UseFont = $smallFont)
    $rect = New-Object System.Drawing.RectangleF($X, $Y, $W, $H)
    $g.DrawString($Text, $UseFont, $brush, $rect, $sfCenter)
}

function Draw-Header {
    param([int]$Cx, [int]$Y, [int]$W, [int]$H, [string]$Text)
    $x = $Cx - [int]($W / 2)
    $rect = New-Object System.Drawing.Rectangle($x, $Y, $W, $H)
    $textRect = New-Object System.Drawing.RectangleF($x, $Y, $W, $H)
    $g.FillRectangle($lightBrush, $rect)
    $g.DrawRectangle($pen, $rect)
    $g.DrawString($Text, $headerFont, $brush, $textRect, $sfCenter)
}

function Draw-Actor {
    param([int]$Cx, [int]$Y)
    $g.DrawEllipse($pen, $Cx - 13, $Y, 26, 26)
    $g.DrawLine($pen, $Cx, $Y + 26, $Cx, $Y + 66)
    $g.DrawLine($pen, $Cx - 28, $Y + 40, $Cx + 28, $Y + 40)
    $g.DrawLine($pen, $Cx, $Y + 66, $Cx - 24, $Y + 102)
    $g.DrawLine($pen, $Cx, $Y + 66, $Cx + 24, $Y + 102)
    Draw-Text ($Cx - 48) ($Y + 110) 96 28 "玩家" $headerFont
}

function Draw-LifeLine {
    param([int]$Cx, [int]$Y1, [int]$Y2)
    $g.DrawLine($dashPen, $Cx, $Y1, $Cx, $Y2)
}

function Draw-Activation {
    param([int]$Cx, [int]$Y, [int]$H)
    $x = $Cx - 10
    $rect = New-Object System.Drawing.Rectangle($x, $Y, 20, $H)
    $g.FillRectangle($lightBrush, $rect)
    $g.DrawRectangle($thinPen, $rect)
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

function Draw-Message {
    param([int]$X1, [int]$X2, [int]$Y, [string]$Text, [bool]$Dashed = $false)
    $usePen = if ($Dashed) { $dashPen } else { $pen }
    $g.DrawLine($usePen, $X1, $Y, $X2, $Y)
    Draw-ArrowHead $X1 $Y $X2 $Y
    $labelX = [Math]::Min($X1, $X2) + 10
    $labelW = [Math]::Abs($X2 - $X1) - 20
    Draw-Text $labelX ($Y - 44) $labelW 40 $Text $smallFont
}

function Draw-SelfMessage {
    param([int]$Cx, [int]$Y, [string]$Text)
    $x1 = $Cx + 10
    $x2 = $Cx + 95
    $y2 = $Y + 44
    $g.DrawLine($pen, $x1, $Y, $x2, $Y)
    $g.DrawLine($pen, $x2, $Y, $x2, $y2)
    $g.DrawLine($pen, $x2, $y2, $x1, $y2)
    Draw-ArrowHead $x2 $y2 $x1 $y2
    Draw-Text ($Cx + 100) ($Y - 6) 220 58 $Text $smallFont
}

function Draw-AltFrame {
    param([int]$X, [int]$Y, [int]$W, [int]$H, [string]$Title)
    $rect = New-Object System.Drawing.Rectangle($X, $Y, $W, $H)
    $g.DrawRectangle($thinPen, $rect)
    $tagX2 = $X + 72
    $tagX3 = $X + 56
    $tagY2 = $Y + 30
    $tagPts = @(
        (New-Object System.Drawing.Point($X, $Y)),
        (New-Object System.Drawing.Point($tagX2, $Y)),
        (New-Object System.Drawing.Point($tagX3, $tagY2)),
        (New-Object System.Drawing.Point($X, $tagY2))
    )
    $g.FillPolygon($lightBrush, $tagPts)
    $g.DrawPolygon($thinPen, $tagPts)
    Draw-Text ($X + 4) ($Y + 2) 54 24 $Title $smallFont
}

$titleRect = New-Object System.Drawing.RectangleF(0, 30, $width, 45)
$g.DrawString("UI 界面交互 UML 顺序图", $titleFont, $brush, $titleRect, $sfCenter)

$playerX = 95
$uiX = 355
$eventX = 620
$statX = 875
$panelX = 1140
$timeX = 1370
$headerY = 105
$lifeTop = 190
$lifeBottom = 1390

Draw-Actor $playerX 95
Draw-Header $uiX $headerY 190 70 "UI 管理器`n(UIManager)"
Draw-Header $eventX $headerY 180 70 "事件总线`n(EventSO)"
Draw-Header $statX $headerY 190 70 "状态显示`n(Stat/Skill)"
Draw-Header $panelX $headerY 190 70 "界面面板`n(Panels)"
Draw-Header $timeX $headerY 170 70 "游戏时间`n(Time)"

foreach ($x in @($playerX,$uiX,$eventX,$statX,$panelX,$timeX)) {
    Draw-LifeLine $x $lifeTop $lifeBottom
}

Draw-Activation $uiX 230 1045
Draw-Activation $eventX 260 760
Draw-Activation $statX 405 230
Draw-Activation $panelX 780 460
Draw-Activation $timeX 855 110

Draw-Message $uiX $eventX 260 "1. 注册事件监听`nhealth/load/gameOver/backToMenu"
Draw-Message $eventX $uiX 350 "2. 生命值变化事件触发"
Draw-Message $uiX $statX 430 "3. 计算生命值比例并刷新血条"
Draw-Message $statX $uiX 500 "4. 返回刷新结果" $true
Draw-SelfMessage $uiX 575 "5. Update 读取`n技能冷却状态"
Draw-Message $uiX $statX 660 "6. 刷新技能图标填充比例"

Draw-AltFrame 55 735 1400 250 "alt"
Draw-Text 145 770 220 28 "[暂停操作]" $headerFont
Draw-Message $playerX $uiX 830 "7a. 按下 Esc 或点击设置按钮"
Draw-SelfMessage $uiX 900 "8a. 判断暂停面板显示状态"
Draw-Message $uiX $panelX 965 "9a. 显示或隐藏暂停面板"
Draw-Message $uiX $timeX 1030 "10a. 设置 Time.timeScale"

Draw-AltFrame 55 1070 1400 270 "alt"
Draw-Text 145 1105 250 28 "[读档/返回主菜单]" $headerFont
Draw-Message $eventX $uiX 1160 "7b. loadData/backToMenu 事件触发"
Draw-Message $uiX $panelX 1225 "8b. 关闭暂停面板并隐藏结束面板"

Draw-Text 145 1280 220 28 "[角色死亡]" $headerFont
Draw-Message $eventX $uiX 1335 "7c. gameOverEvent 事件触发"
Draw-Message $uiX $panelX 1400 "8c. 显示 Game Over 面板"

$captionRect = New-Object System.Drawing.RectangleF(0, 1442, $width, 42)
$g.DrawString("图  UI 界面交互 UML 顺序图", $captionFont, $brush, $captionRect, $sfCenter)

$bmp.Save($OutFile, [System.Drawing.Imaging.ImageFormat]::Png)

$g.Dispose()
$bmp.Dispose()
$pen.Dispose()
$thinPen.Dispose()
$dashPen.Dispose()
$brush.Dispose()
$whiteBrush.Dispose()
$lightBrush.Dispose()
$titleFont.Dispose()
$headerFont.Dispose()
$font.Dispose()
$smallFont.Dispose()
$captionFont.Dispose()

Write-Output $OutFile
