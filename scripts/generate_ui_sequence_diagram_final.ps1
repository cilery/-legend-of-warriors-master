Add-Type -AssemblyName System.Drawing

$ErrorActionPreference = "Stop"

$RootDir = "D:\codex_workspace\legend-of-warriors-master"
$OutFile = Join-Path $RootDir "UI界面交互UML顺序图_最终无交叉版.png"

$width = 1300
$height = 1540
$bmp = New-Object System.Drawing.Bitmap($width, $height)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$g.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit
$g.Clear([System.Drawing.Color]::White)

$black = [System.Drawing.Color]::Black
$pen = New-Object System.Drawing.Pen($black, 3)
$thinPen = New-Object System.Drawing.Pen($black, 2)
$dashPen = New-Object System.Drawing.Pen($black, 2)
$dashPen.DashStyle = [System.Drawing.Drawing2D.DashStyle]::Dash
$brush = New-Object System.Drawing.SolidBrush($black)
$lightBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(246,246,246))

$titleFont = New-Object System.Drawing.Font("SimSun", 30, [System.Drawing.FontStyle]::Bold)
$headerFont = New-Object System.Drawing.Font("SimSun", 18, [System.Drawing.FontStyle]::Bold)
$smallFont = New-Object System.Drawing.Font("SimSun", 16, [System.Drawing.FontStyle]::Regular)
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
    Draw-Text $labelX ($Y - 45) $labelW 42 $Text $smallFont
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
    Draw-Text ($Cx + 100) ($Y - 6) 230 58 $Text $smallFont
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

$playerX = 110
$uiX = 405
$compX = 725
$eventX = 1040
$headerY = 110
$lifeTop = 195
$lifeBottom = 1415

Draw-Actor $playerX 100
Draw-Header $uiX $headerY 210 72 "UI 管理器`n(UIManager)"
Draw-Header $compX $headerY 220 72 "UI 组件`n(状态栏/面板)"
Draw-Header $eventX $headerY 210 72 "事件总线`n(EventSO)"

foreach ($x in @($playerX,$uiX,$compX,$eventX)) {
    Draw-LifeLine $x $lifeTop $lifeBottom
}

Draw-Activation $uiX 235 1095
Draw-Activation $compX 395 840
Draw-Activation $eventX 255 955

Draw-Message $uiX $eventX 255 "1. 注册事件监听"
Draw-Message $eventX $uiX 345 "2. 生命值变化事件"
Draw-Message $uiX $compX 425 "3. 计算生命值比例`n刷新血条"
Draw-Message $compX $uiX 500 "4. 返回刷新结果" $true
Draw-SelfMessage $uiX 570 "5. Update 读取`n技能冷却状态"
Draw-Message $uiX $compX 655 "6. 刷新技能图标"

Draw-AltFrame 65 720 1085 315 "alt"
Draw-Text 145 758 230 28 "[暂停操作]" $headerFont
Draw-Message $playerX $uiX 820 "7a. 按下 Esc 或点击设置"
Draw-SelfMessage $uiX 900 "8a. 判断暂停面板状态"
Draw-Message $uiX $compX 1000 "9a. 显示/隐藏暂停面板`n并同步游戏暂停"

Draw-AltFrame 65 1080 1085 280 "alt"
Draw-Text 145 1118 260 28 "[读档或返回主菜单]" $headerFont
Draw-Message $eventX $uiX 1180 "7b. loadData/backToMenu 事件"
Draw-Message $uiX $compX 1245 "8b. 关闭暂停面板`n隐藏结束面板"

Draw-Text 145 1302 220 28 "[角色死亡]" $headerFont
Draw-Message $eventX $uiX 1345 "7c. gameOverEvent 事件"
Draw-Message $uiX $compX 1410 "8c. 显示 Game Over 面板"

$captionRect = New-Object System.Drawing.RectangleF(0, 1480, $width, 42)
$g.DrawString("图  UI 界面交互 UML 顺序图", $captionFont, $brush, $captionRect, $sfCenter)

$bmp.Save($OutFile, [System.Drawing.Imaging.ImageFormat]::Png)

$g.Dispose()
$bmp.Dispose()
$pen.Dispose()
$thinPen.Dispose()
$dashPen.Dispose()
$brush.Dispose()
$lightBrush.Dispose()
$titleFont.Dispose()
$headerFont.Dispose()
$smallFont.Dispose()
$captionFont.Dispose()

Write-Output $OutFile
