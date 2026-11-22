param(
    [string]$InputPath = "static/nut-walnut-favicon.png",
    [string]$OutputPath = "static/nut-walnut-favicon.png",
    [int]$Size = 256
)

Add-Type -AssemblyName System.Drawing

$resolvedInput = (Resolve-Path -LiteralPath $InputPath).Path
$absoluteOutput = [System.IO.Path]::GetFullPath($OutputPath)
$temporaryOutput = "$absoluteOutput.tmp.png"

$source = [System.Drawing.Bitmap]::new($resolvedInput)
$masked = [System.Drawing.Bitmap]::new($source.Width, $source.Height, [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)

$left = $source.Width
$top = $source.Height
$right = 0
$bottom = 0

for ($y = 0; $y -lt $source.Height; $y++) {
    for ($x = 0; $x -lt $source.Width; $x++) {
        $pixel = $source.GetPixel($x, $y)
        $channelRange = [Math]::Max($pixel.R, [Math]::Max($pixel.G, $pixel.B)) - [Math]::Min($pixel.R, [Math]::Min($pixel.G, $pixel.B))
        $warmth = [Math]::Max(0, $pixel.R - $pixel.B)
        $foreground = [Math]::Max($channelRange, $warmth)
        $alpha = [Math]::Min(255, [Math]::Max(0, [int](($foreground - 10) * 5.5)))

        if ($alpha -gt 0) {
            $masked.SetPixel($x, $y, [System.Drawing.Color]::FromArgb($alpha, $pixel.R, $pixel.G, $pixel.B))
        }
        if ($alpha -gt 40) {
            $left = [Math]::Min($left, $x)
            $top = [Math]::Min($top, $y)
            $right = [Math]::Max($right, $x)
            $bottom = [Math]::Max($bottom, $y)
        }
    }
}

$width = $right - $left + 1
$height = $bottom - $top + 1
$side = [Math]::Min([Math]::Max($width, $height) * 1.14, [Math]::Min($source.Width, $source.Height))
$centerX = ($left + $right) / 2
$centerY = ($top + $bottom) / 2
$cropX = [Math]::Max(0, [Math]::Min($source.Width - $side, [int]($centerX - ($side / 2))))
$cropY = [Math]::Max(0, [Math]::Min($source.Height - $side, [int]($centerY - ($side / 2))))

$favicon = [System.Drawing.Bitmap]::new($Size, $Size, [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
$graphics = [System.Drawing.Graphics]::FromImage($favicon)
$graphics.Clear([System.Drawing.Color]::Transparent)
$graphics.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
$graphics.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality
$graphics.DrawImage($masked, [System.Drawing.Rectangle]::new(0, 0, $Size, $Size), $cropX, $cropY, $side, $side, [System.Drawing.GraphicsUnit]::Pixel)
$graphics.Dispose()
$masked.Dispose()
$source.Dispose()

$favicon.Save($temporaryOutput, [System.Drawing.Imaging.ImageFormat]::Png)
$favicon.Dispose()
Move-Item -LiteralPath $temporaryOutput -Destination $absoluteOutput -Force
