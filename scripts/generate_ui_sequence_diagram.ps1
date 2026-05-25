Add-Type -AssemblyName System.Drawing

$ErrorActionPreference = "Stop"

$RootDir = "D:\codex_workspace\legend-of-warriors-master"
$OutFile = Join-Path $RootDir "UI界面交互UML顺序图_黑白论文版.png"

$width = 1600
$height = 1580
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
$grayPen = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(110,110,110), 2)
$brush = New-Object System.Drawing.SolidBrush($black)
$whiteBrush = New-Object System.Drawing.SolidBrush($white)
$lightBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(245,245,245))

$titleFont = New-Object System.Drawing.Font("SimSun", 30, [System.Drawing.FontStyle]::Bold)
$font = New-Object System.Drawing.Font("SimSun", 19, [System.Drawing.FontStyle]::Regular)
$smallFont = New-Object System.Drawing.Font("SimSun", 16, [System.Drawing.FontStyle]::Regular)
$boldSmallFont = New-Object System.Drawing.Font("SimSun", 16, [System.Drawing.FontStyle]::Bold)
$captionFont = New-Object System.Drawing.Font("SimSun", 24, [System.Drawing.FontStyle]::Regular)

$sfCenter = New-Object System.Drawing.StringFormat
$sfCenter.Alignment = [System.Drawing.StringAlignment]::Center
$sfCenter.LineAlignment = [System.Drawing.StringAlignment]::Center
$sfCenter.FormatFlags = [System.Drawing.StringFormatFlags]::LineLimit

$sfLeft = New-Object System.Drawing.StringFormat
$sfLeft.Alignment = [System.Drawing.StringAlignment]::Near
$sfLeft.LineAlignment = [System.Drawing.StringAlignment]::Near
$sfLeft.FormatFlags = [System.Drawing.StringFormatFlags]::LineLimit

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
    $g.DrawString($Text, $boldSmallFont, $brush, $textRect, $sfCenter)
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
    $labelX = [Math]::Min($X1, $X2) + 8
    $labelW = [Math]::Abs($X2 - $X1) - 16
    Draw-Text $labelX ($Y - 44) $labelW 42 $Text $smallFont
}

function Draw-SelfMessage {
    param([int]$Cx, [int]$Y, [string]$Text)
    $x1 = $Cx + 10
    $x2 = $Cx + 90
    $g.DrawLine($pen, $x1, $Y, $x2, $Y)
    $g.DrawLine($pen, $x2, $Y, $x2, $Y + 44)
    $g.DrawLine($pen, $x2, $Y + 44, $x1, $Y + 44)
    Draw-ArrowHead $x2 ($Y + 44) $x1 ($Y + 44)
    Draw-Text ($Cx + 96) ($Y - 8) 220 58 $Text $smallFont
}

function Draw-Actor {
    param([int]$Cx, [int]$Y)
    $g.DrawEllipse($pen, $Cx - 13, $Y, 26, 26)
    $g.DrawLine($pen, $Cx, $Y + 26, $Cx, $Y + 68)
    $g.DrawLine($pen, $Cx - 28, $Y + 40, $Cx + 28, $Y + 40)
    $g.DrawLine($pen, $Cx, $Y + 68, $Cx - 24, $Y + 104)
    $g.DrawLine($pen, $Cx, $Y + 68, $Cx + 24, $Y + 104)
    Draw-Text ($Cx - 50) ($Y + 112) 100 28 "玩家" $boldSmallFont
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
    Draw-Text ($X + 5) ($Y + 2) 52 24 $Title $smallFont
}

$titleRect = New-Object System.Drawing.RectangleF(0, 30, $width, 45)
$g.DrawString("UI 界面交互 UML 顺序图", $titleFont, $brush, $titleRect, $sfCenter)

$playerX = 90
$uiX = 355
$statX = 610
$skillX = 845
$pauseX = 1085
$gameOverX = 1300
$eventX = 1500
$headerY = 105
$lifeTop = 190
$lifeBottom = 1490

Draw-Actor $playerX 95
Draw-Header $uiX $headerY 190 70 "UI 管理器`n(UIManager)"
Draw-Header $statX $headerY 190 70 "状态栏`n(PlayerStatBar)"
Draw-Header $skillX $headerY 190 70 "技能图标`n(Skill Image)"
Draw-Header $pauseX $headerY 190 70 "暂停面板`n(PausePanel)"
Draw-Header $gameOverX $headerY 190 70 "结束面板`n(GameOverPanel)"
Draw-Header $eventX $headerY 150 70 "事件总线`n(EventSO)"

foreach ($x in @($playerX,$uiX,$statX,$skillX,$pauseX,$gameOverX,$eventX)) {
    Draw-LifeLine $x $lifeTop $lifeBottom
}

Draw-Activation $uiX 230 1170
Draw-Activation $statX 335 130
Draw-Activation $skillX 505 90
Draw-Activation $pauseX 720 110
Draw-Activation $gameOverX 1060 95
Draw-Activation $eventX 250 970

Draw-Message $uiX $eventX 250 "1. 注册事件监听`n(生命值/读档/结束/返回)"
Draw-Message $eventX $uiX 330 "2. healthEvent 触发`n(角色生命值变化)"
Draw-Message $uiX $statX 405 "3. 计算生命值百分比`n并刷新血条"
Draw-Message $statX $uiX 470 "4. 返回刷新结果" $true
Draw-SelfMessage $uiX 530 "5. Update 中读取`n技能冷却状态"
Draw-Message $uiX $skillX 630 "6. 修改 fillAmount`n刷新技能图标"

Draw-AltFrame 45 700 1260 250 "alt"
Draw-Text 135 735 220 28 "[暂停操作]" $boldSmallFont
Draw-Message $playerX $uiX 800 "7a. 按下 Esc 或点击设置"
Draw-SelfMessage $uiX 860 "8a. 判断暂停面板`n是否显示"
Draw-Message $uiX $pauseX 930 "9a. 显示/隐藏暂停面板`n同步 Time.timeScale"

Draw-AltFrame 45 990 1455 380 "alt"
Draw-Text 130 1025 250 28 "[场景切换或读档]" $boldSmallFont
Draw-Message $eventX $uiX 1085 "7b. loadData/backToMenu`n事件触发"
Draw-Message $uiX $pauseX 1150 "8b. 关闭暂停面板`n恢复游戏时间"
Draw-Message $uiX $gameOverX 1215 "9b. 隐藏 Game Over 面板"

Draw-Text 130 1285 250 28 "[角色死亡]" $boldSmallFont
Draw-Message $eventX $uiX 1345 "7c. gameOverEvent 触发"
Draw-Message $uiX $gameOverX 1410 "8c. 显示 Game Over 面板`n选中重新开始按钮"

$captionRect = New-Object System.Drawing.RectangleF(0, 1520, $width, 42)
$g.DrawString("图  UI 界面交互 UML 顺序图", $captionFont, $brush, $captionRect, $sfCenter)

$bmp.Save($OutFile, [System.Drawing.Imaging.ImageFormat]::Png)

$g.Dispose()
$bmp.Dispose()
$pen.Dispose()
$thinPen.Dispose()
$dashPen.Dispose()
$grayPen.Dispose()
$brush.Dispose()
$whiteBrush.Dispose()
$lightBrush.Dispose()
$titleFont.Dispose()
$font.Dispose()
$smallFont.Dispose()
$boldSmallFont.Dispose()
$captionFont.Dispose()

Write-Output $OutFile
