# Desenha cafe.bmp: o 1.º quadro da animação "cafe" (chávena sem vapor), que a
# cortina nativa do arranque mostra antes de o WebView2 estar pronto.
# A geometria é a MESMA do <svg id="cafe"> do splash.html (viewBox 400x400,
# mostrado a 280x280 px): se mudar uma, mude a outra e volte a correr isto.
param([string]$Destino = (Join-Path $env:USERPROFILE '.glzr\zebar\omarchy-catppuccin\arranque\cafe.bmp'))
Add-Type -AssemblyName System.Drawing
$tam = 280; $escala = $tam / 400.0
$bmp = New-Object Drawing.Bitmap $tam, $tam, ([Drawing.Imaging.PixelFormat]::Format24bppRgb)
$g = [Drawing.Graphics]::FromImage($bmp)
$g.SmoothingMode = [Drawing.Drawing2D.SmoothingMode]::AntiAlias
$g.PixelOffsetMode = [Drawing.Drawing2D.PixelOffsetMode]::HighQuality
$g.Clear([Drawing.Color]::Black)
$g.ScaleTransform($escala, $escala)
function Cor($hex) { [Drawing.ColorTranslator]::FromHtml($hex) }
function Elipse($cx, $cy, $rx, $ry) { New-Object Drawing.RectangleF ($cx - $rx), ($cy - $ry), (2 * $rx), (2 * $ry) }

# pires
$g.FillEllipse((New-Object Drawing.SolidBrush (Cor '#45475a')), (Elipse 200 322 150 20))
# asa
$g.DrawEllipse((New-Object Drawing.Pen (Cor '#f5e0dc'), 16), (Elipse 305 212 42 38))
# corpo: M92 150 L308 150 L298 240 C292 295 252 318 200 318 C148 318 108 295 102 240 Z
$corpo = New-Object Drawing.Drawing2D.GraphicsPath
$corpo.AddLine(92, 150, 308, 150)
$corpo.AddLine(308, 150, 298, 240)
$corpo.AddBezier(298, 240, 292, 295, 252, 318, 200, 318)
$corpo.AddBezier(200, 318, 148, 318, 108, 295, 102, 240)
$corpo.CloseFigure()
$g.FillPath((New-Object Drawing.SolidBrush (Cor '#f5e0dc')), $corpo)
# café + borda
$g.FillEllipse((New-Object Drawing.SolidBrush (Cor '#6f4e37')), (Elipse 200 150 108 16))
$g.DrawEllipse((New-Object Drawing.Pen (Cor '#f5e0dc'), 6), (Elipse 200 150 108 16))

$g.Dispose()
$bmp.Save($Destino, [Drawing.Imaging.ImageFormat]::Bmp)
$bmp.Dispose()
"cafe.bmp: $Destino ($tam x $tam)"
