Add-Type -AssemblyName System.Drawing

$ErrorActionPreference = "Stop"

$RootDir = "D:\codex_workspace\legend-of-warriors-master"
$OutFile = Join-Path $RootDir "数据管理UML类图_黑白论文版.png"

$width = 1600
$height = 1280
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

$titleFont = New-Object System.Drawing.Font("SimSun", 28, [System.Drawing.FontStyle]::Bold)
$classFont = New-Object System.Drawing.Font("SimSun", 19, [System.Drawing.FontStyle]::Bold)
$font = New-Object System.Drawing.Font("SimSun", 15, [System.Drawing.FontStyle]::Regular)
$smallFont = New-Object System.Drawing.Font("SimSun", 14, [System.Drawing.FontStyle]::Regular)
$captionFont = New-Object System.Drawing.Font("SimSun", 24, [System.Drawing.FontStyle]::Regular)

$sfCenter = New-Object System.Drawing.StringFormat
$sfCenter.Alignment = [System.Drawing.StringAlignment]::Center
$sfCenter.LineAlignment = [System.Drawing.StringAlignment]::Center
$sfCenter.FormatFlags = [System.Drawing.StringFormatFlags]::LineLimit

$sfLeft = New-Object System.Drawing.StringFormat
$sfLeft.Alignment = [System.Drawing.StringAlignment]::Near
$sfLeft.LineAlignment = [System.Drawing.StringAlignment]::Near
$sfLeft.FormatFlags = [System.Drawing.StringFormatFlags]::LineLimit

function Draw-Class {
    param(
        [int]$X, [int]$Y, [int]$W, [int]$H,
        [string]$Name,
        [string[]]$Attrs,
        [string[]]$Methods,
        [bool]$Interface = $false
    )
    $rect = New-Object System.Drawing.Rectangle($X, $Y, $W, $H)
    $g.FillRectangle($whiteBrush, $rect)
    $g.DrawRectangle($pen, $rect)

    $headerH = if ($Interface) { 72 } else { 50 }
    $attrH = [Math]::Max(62, [int](($H - $headerH) * 0.48))
    $g.DrawLine($thinPen, $X, $Y + $headerH, $X + $W, $Y + $headerH)
    $g.DrawLine($thinPen, $X, $Y + $headerH + $attrH, $X + $W, $Y + $headerH + $attrH)

    if ($Interface) {
        $stereoY = $Y + 8
        $nameY = $Y + 32
        $stereoRect = New-Object System.Drawing.RectangleF($X, $stereoY, $W, 24)
        $nameRect = New-Object System.Drawing.RectangleF($X, $nameY, $W, 34)
        $g.DrawString("<<interface>>", $smallFont, $brush, $stereoRect, $sfCenter)
        $g.DrawString($Name, $classFont, $brush, $nameRect, $sfCenter)
    } else {
        $nameRect = New-Object System.Drawing.RectangleF($X, $Y, $W, $headerH)
        $g.DrawString($Name, $classFont, $brush, $nameRect, $sfCenter)
    }

    $attrText = [string]::Join("`n", $Attrs)
    $methodText = [string]::Join("`n", $Methods)
    $attrX = $X + 14
    $attrY = $Y + $headerH + 10
    $attrW = $W - 24
    $attrH2 = $attrH - 16
    $methodX = $X + 14
    $methodY = $Y + $headerH + $attrH + 10
    $methodW = $W - 24
    $methodH = $H - $headerH - $attrH - 16
    $attrRect = New-Object System.Drawing.RectangleF($attrX, $attrY, $attrW, $attrH2)
    $methodRect = New-Object System.Drawing.RectangleF($methodX, $methodY, $methodW, $methodH)
    $g.DrawString($attrText, $font, $brush, $attrRect, $sfLeft)
    $g.DrawString($methodText, $font, $brush, $methodRect, $sfLeft)
}

function Draw-Label {
    param([int]$X, [int]$Y, [string]$Text, [int]$W = 160)
    $rect = New-Object System.Drawing.RectangleF($X, $Y, $W, 26)
    $g.DrawString($Text, $smallFont, $brush, $rect, $sfCenter)
}

function Draw-ArrowHead {
    param([int]$X1, [int]$Y1, [int]$X2, [int]$Y2, [bool]$Open = $false)
    $angle = [Math]::Atan2($Y2 - $Y1, $X2 - $X1)
    $len = 18
    $spread = 0.52
    $p1 = New-Object System.Drawing.Point(
        [int]($X2 - $len * [Math]::Cos($angle - $spread)),
        [int]($Y2 - $len * [Math]::Sin($angle - $spread))
    )
    $p2 = New-Object System.Drawing.Point(
        [int]($X2 - $len * [Math]::Cos($angle + $spread)),
        [int]($Y2 - $len * [Math]::Sin($angle + $spread))
    )
    $p3 = New-Object System.Drawing.Point($X2, $Y2)
    if ($Open) {
        $g.FillPolygon($whiteBrush, @($p1, $p2, $p3))
        $g.DrawPolygon($thinPen, @($p1, $p2, $p3))
    } else {
        $g.FillPolygon($brush, @($p1, $p2, $p3))
    }
}

function Draw-LineArrow {
    param([int]$X1, [int]$Y1, [int]$X2, [int]$Y2, [System.Drawing.Pen]$UsePen = $thinPen, [bool]$Open = $false)
    $g.DrawLine($UsePen, $X1, $Y1, $X2, $Y2)
    Draw-ArrowHead $X1 $Y1 $X2 $Y2 $Open
}

function Draw-PolylineArrow {
    param([int[]]$Coords, [System.Drawing.Pen]$UsePen = $thinPen, [bool]$Open = $false)
    for ($i = 0; $i -lt $Coords.Count - 2; $i += 2) {
        $g.DrawLine($UsePen, $Coords[$i], $Coords[$i + 1], $Coords[$i + 2], $Coords[$i + 3])
    }
    $n = $Coords.Count
    Draw-ArrowHead $Coords[$n - 4] $Coords[$n - 3] $Coords[$n - 2] $Coords[$n - 1] $Open
}

function Draw-DiamondAggregation {
    param([int]$Cx, [int]$Cy)
    $topY = $Cy - 10
    $rightX = $Cx + 16
    $bottomY = $Cy + 10
    $leftX = $Cx - 16
    $pts = @(
        (New-Object System.Drawing.Point($Cx, $topY)),
        (New-Object System.Drawing.Point($rightX, $Cy)),
        (New-Object System.Drawing.Point($Cx, $bottomY)),
        (New-Object System.Drawing.Point($leftX, $Cy))
    )
    $g.FillPolygon($whiteBrush, $pts)
    $g.DrawPolygon($thinPen, $pts)
}

$titleRect = New-Object System.Drawing.RectangleF(0, 30, $width, 45)
$g.DrawString("数据管理 UML 类图", $titleFont, $brush, $titleRect, $sfCenter)

Draw-Class 80 120 400 320 "DataManager" @(
    "+ instance : DataManager",
    "- saveableList : List<ISaveable>",
    "- saveData : Data",
    "- jsonFolder : string",
    "+ saveDataEvent",
    "+ loadDataEvent"
) @(
    "+ RegisterSaveData()",
    "+ UnRegisterSaveData()",
    "+ Save()",
    "+ Load()",
    "- ReadSavedData()"
)

Draw-Class 610 120 380 285 "Data" @(
    "+ sceneToSave : string",
    "+ characterPosDict",
    "  Dictionary<string, SerializeVector3>",
    "+ floatSavedData",
    "  Dictionary<string, float>"
) @(
    "+ SaveGameScene()",
    "+ GetSavedScene() : GameSceneSO"
)

Draw-Class 1130 120 370 245 "SerializeVector3" @(
    "+ x : float",
    "+ y : float",
    "+ z : float"
) @(
    "+ SerializeVector3(Vector3)",
    "+ ToVector3() : Vector3"
)

Draw-Class 610 520 380 315 "ISaveable" @(
    ""
) @(
    "+ GetDataID() : DataDefination",
    "+ RegisterSaveData()",
    "+ UnRegisterSaveData()",
    "+ GetSaveData(data)",
    "+ LoadData(data)"
) $true

Draw-Class 80 650 400 245 "DataDefination" @(
    "+ persistentType : PersistentType",
    "+ ID : string"
) @(
    "- OnValidate()",
    "  生成可持久化对象标识"
)

Draw-Class 1130 520 370 230 "GameSceneSO" @(
    "+ sceneType : SceneType",
    "+ sceneReference : AssetReference"
) @(
    "用于记录当前场景配置"
)

Draw-Class 360 950 330 210 "Character" @(
    "+ maxHealth : float",
    "+ currentHealth : float"
) @(
    "+ GetSaveData(data)",
    "+ LoadData(data)"
)

Draw-Class 900 950 330 210 "SceneLoader" @(
    "- currentLoadedScene : GameSceneSO",
    "- positionToGo : Vector3"
) @(
    "+ GetSaveData(data)",
    "+ LoadData(data)"
)

# Relationships.
Draw-LineArrow 480 245 610 245 $thinPen $false
Draw-Label 493 215 "维护/读写" 115
Draw-DiamondAggregation 500 245

Draw-LineArrow 990 245 1130 245 $thinPen $false
Draw-Label 1005 215 "坐标转换" 115
Draw-DiamondAggregation 1010 245

Draw-PolylineArrow @(280,440,280,545,610,545) $thinPen $false
Draw-Label 305 505 "注册对象列表" 150
Draw-DiamondAggregation 300 545

Draw-PolylineArrow @(800,405,800,520) $thinPen $false
Draw-Label 820 455 "保存/恢复接口" 150

Draw-PolylineArrow @(990,635,1130,635) $thinPen $false
Draw-Label 1008 605 "场景数据" 120

Draw-PolylineArrow @(610,680,480,760) $thinPen $false
Draw-Label 485 688 "对象ID" 110

Draw-PolylineArrow @(525,950,685,835) $dashPen $true
Draw-Label 545 875 "实现" 90

Draw-PolylineArrow @(1065,950,875,835) $dashPen $true
Draw-Label 950 875 "实现" 90

Draw-PolylineArrow @(525,950,350,895) $thinPen $false
Draw-Label 365 900 "使用ID" 95

Draw-PolylineArrow @(1065,950,990,790,1130,685) $thinPen $false
Draw-Label 1030 820 "保存场景" 110

$captionRect = New-Object System.Drawing.RectangleF(0, 1215, $width, 42)
$g.DrawString("图  数据管理 UML 类图", $captionFont, $brush, $captionRect, $sfCenter)

$bmp.Save($OutFile, [System.Drawing.Imaging.ImageFormat]::Png)

$g.Dispose()
$bmp.Dispose()
$pen.Dispose()
$thinPen.Dispose()
$dashPen.Dispose()
$brush.Dispose()
$whiteBrush.Dispose()
$titleFont.Dispose()
$classFont.Dispose()
$font.Dispose()
$smallFont.Dispose()
$captionFont.Dispose()

Write-Output $OutFile
