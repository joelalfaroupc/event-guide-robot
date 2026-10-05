param(
    [string]$PackageRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
)

$ErrorActionPreference = "Stop"

$mapDir = Join-Path $PackageRoot "maps"
$worldDir = Join-Path $PackageRoot "worlds"
$modelsDir = Join-Path $PackageRoot "models"
New-Item -ItemType Directory -Force -Path $mapDir, $worldDir, $modelsDir | Out-Null

$resolution = 0.05
$originX = -7.0
$originY = -7.0
$width = 280
$height = 280
$wallHeight = 2.2
$wallThickness = 0.14
$markerSize = 0.34
$markerHeight = $markerSize / 2.0

function New-Rect($name, $x, $y, $sx, $sy, $h, $kind) {
    [pscustomobject]@{
        Name = $name
        X = [double]$x
        Y = [double]$y
        SX = [double]$sx
        SY = [double]$sy
        H = [double]$h
        Kind = $kind
    }
}

$walls = @(
    New-Rect "outer_north" 0.0 5.4 12.0 $wallThickness $wallHeight "wall"
    New-Rect "outer_south" 0.0 -5.4 12.0 $wallThickness $wallHeight "wall"
    New-Rect "outer_west" -6.0 0.0 $wallThickness 10.8 $wallHeight "wall"
    New-Rect "outer_east" 6.0 0.0 $wallThickness 10.8 $wallHeight "wall"

    # Clean 3x3 fair-plan grid with asymmetric connectivity:
    # - top-left + top-center are one larger hall (no vertical wall there);
    # - bottom-center + bottom-right are one larger hall;
    # - top-right is a one-entry room, reachable only from the right-center room.
    # Coordinates use two vertical grid lines (x=-2.2, x=2.0) and two
    # horizontal grid lines (y=-1.8, y=1.8), with deliberate door gaps.

    # Vertical divider x=-2.2. It separates left rooms from the central column,
    # but is absent in the top row to create a larger north hall.
    New-Rect "left_divider_bottom_lower" -2.2 -4.70 $wallThickness 1.40 $wallHeight "wall"
    New-Rect "left_divider_bottom_upper" -2.2 -2.40 $wallThickness 1.20 $wallHeight "wall"
    New-Rect "left_divider_middle_lower" -2.2 -1.20 $wallThickness 1.20 $wallHeight "wall"
    New-Rect "left_divider_middle_upper" -2.2 1.35 $wallThickness 0.90 $wallHeight "wall"

    # Vertical divider x=2.0. It is absent in the bottom row to merge
    # bottom-center and bottom-right, and solid in the top row so the north-east
    # room only connects through the right-center room.
    New-Rect "right_divider_middle_lower" 2.0 -1.20 $wallThickness 1.20 $wallHeight "wall"
    New-Rect "right_divider_middle_upper" 2.0 1.20 $wallThickness 1.20 $wallHeight "wall"
    New-Rect "right_divider_top_solid" 2.0 3.60 $wallThickness 3.60 $wallHeight "wall"

    # Horizontal divider y=-1.8. Left room has no direct north/south door; the
    # large bottom hall is entered from the central room through an offset door.
    New-Rect "south_divider_left_solid" -4.10 -1.8 3.80 $wallThickness $wallHeight "wall"
    New-Rect "south_divider_center_left" -1.50 -1.8 1.40 $wallThickness $wallHeight "wall"
    New-Rect "south_divider_center_right" 3.40 -1.8 5.20 $wallThickness $wallHeight "wall"

    # Horizontal divider y=1.8. The north hall has an offset door from the
    # central room; the north-east room has its own single door from the right.
    New-Rect "north_divider_left" -4.20 1.8 3.60 $wallThickness $wallHeight "wall"
    New-Rect "north_divider_center_left" -0.55 1.8 1.70 $wallThickness $wallHeight "wall"
    New-Rect "north_divider_center_right" 1.45 1.8 1.10 $wallThickness $wallHeight "wall"
    New-Rect "north_divider_right_left" 2.90 1.8 1.80 $wallThickness $wallHeight "wall"
    New-Rect "north_divider_right_right" 5.45 1.8 1.10 $wallThickness $wallHeight "wall"
)

$obstacles = @()

$allCollisionRects = @($walls + $obstacles)

function Write-PgmMap($path, $rects) {
    $pixels = New-Object byte[] ($width * $height)
    for ($i = 0; $i -lt $pixels.Length; $i++) {
        $pixels[$i] = 254
    }

    foreach ($rect in $rects) {
        $minX = [Math]::Floor((($rect.X - $rect.SX / 2.0) - $originX) / $resolution)
        $maxX = [Math]::Ceiling((($rect.X + $rect.SX / 2.0) - $originX) / $resolution)
        $minY = [Math]::Floor((($rect.Y - $rect.SY / 2.0) - $originY) / $resolution)
        $maxY = [Math]::Ceiling((($rect.Y + $rect.SY / 2.0) - $originY) / $resolution)
        $minX = [Math]::Max(0, [int]$minX)
        $maxX = [Math]::Min($width - 1, [int]$maxX)
        $minY = [Math]::Max(0, [int]$minY)
        $maxY = [Math]::Min($height - 1, [int]$maxY)

        for ($my = $minY; $my -le $maxY; $my++) {
            $row = ($height - 1 - $my) * $width
            for ($mx = $minX; $mx -le $maxX; $mx++) {
                $pixels[$row + $mx] = 0
            }
        }
    }

    $header = "P5`n$width $height`n255`n"
    $headerBytes = [System.Text.Encoding]::ASCII.GetBytes($header)
    $bytes = New-Object byte[] ($headerBytes.Length + $pixels.Length)
    [Array]::Copy($headerBytes, 0, $bytes, 0, $headerBytes.Length)
    [Array]::Copy($pixels, 0, $bytes, $headerBytes.Length, $pixels.Length)
    [System.IO.File]::WriteAllBytes($path, $bytes)
}

function Format-Double($value) {
    return ([double]$value).ToString("0.###", [Globalization.CultureInfo]::InvariantCulture)
}

function New-BoxXml($rect) {
    $z = $rect.H / 2.0
    $color = if ($rect.Kind -eq "booth") { "0.62 0.62 0.58 1" } else { "0.82 0.82 0.78 1" }
@"
      <link name='$( $rect.Name )'>
        <pose>$(Format-Double $rect.X) $(Format-Double $rect.Y) $(Format-Double $z) 0 0 0</pose>
        <collision name='collision'>
          <geometry>
            <box><size>$(Format-Double $rect.SX) $(Format-Double $rect.SY) $(Format-Double $rect.H)</size></box>
          </geometry>
        </collision>
        <visual name='visual'>
          <geometry>
            <box><size>$(Format-Double $rect.SX) $(Format-Double $rect.SY) $(Format-Double $rect.H)</size></box>
          </geometry>
          <material>
            <ambient>$color</ambient>
            <diffuse>$color</diffuse>
          </material>
        </visual>
      </link>
"@
}

$markerPlacements = @(
    [pscustomobject]@{ Id = 11; X = -1.25; Y = 5.30; Yaw = 0.0; Name = "Qualcomm AI Hub" }
    [pscustomobject]@{ Id = 12; X = -5.90; Y = 3.55; Yaw = 1.57079632679; Name = "Samsung Galaxy Experience" }
    [pscustomobject]@{ Id = 21; X = -5.90; Y = -0.60; Yaw = 1.57079632679; Name = "Telefonica Open Gateway" }
    [pscustomobject]@{ Id = 22; X = -3.35; Y = 1.70; Yaw = 0.0; Name = "Nokia Networks Lab" }
    [pscustomobject]@{ Id = 31; X = 0.05; Y = -5.30; Yaw = 0.0; Name = "Ericsson 5G Arena" }
    [pscustomobject]@{ Id = 32; X = 5.90; Y = -3.55; Yaw = 1.57079632679; Name = "GSMA Innovation City" }
    [pscustomobject]@{ Id = 41; X = 5.90; Y = 3.00; Yaw = 1.57079632679; Name = "Meta XR Showcase" }
    [pscustomobject]@{ Id = 42; X = 4.15; Y = 5.30; Yaw = 0.0; Name = "NVIDIA Edge AI" }
)

$arucoBytes = @{
    11 = @(17, 167)
    12 = @(14, 183)
    21 = @(176, 43)
    22 = @(204, 213)
    31 = @(87, 178)
    32 = @(158, 207)
    41 = @(42, 40)
    42 = @(50, 140)
}

Add-Type -AssemblyName System.Drawing

function New-ArucoPng($id, $path) {
    $tempPath = "$path.tmp"
    if (Test-Path $tempPath) {
        Remove-Item -LiteralPath $tempPath -Force
    }
    if (Test-Path $path) {
        return
    }

    $bytes = $arucoBytes[[int]$id]
    $bits = @()
    foreach ($b in $bytes) {
        for ($shift = 7; $shift -ge 0; $shift--) {
            $bits += (($b -shr $shift) -band 1)
        }
    }

    $cells = 6
    $cellPx = 100
    $size = $cells * $cellPx
    $bmp = New-Object System.Drawing.Bitmap $size, $size
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.Clear([System.Drawing.Color]::Black)
    for ($row = 0; $row -lt 4; $row++) {
        for ($col = 0; $col -lt 4; $col++) {
            $bit = $bits[$row * 4 + $col]
            if ($bit -eq 1) {
                $brush = [System.Drawing.Brushes]::White
            } else {
                $brush = [System.Drawing.Brushes]::Black
            }
            $g.FillRectangle($brush, ($col + 1) * $cellPx, ($row + 1) * $cellPx, $cellPx, $cellPx)
        }
    }
    $bmp.Save($tempPath, [System.Drawing.Imaging.ImageFormat]::Png)
    Move-Item -LiteralPath $tempPath -Destination $path -Force
    $g.Dispose()
    $bmp.Dispose()
}

Write-PgmMap (Join-Path $mapDir "event_fair_map.pgm") $allCollisionRects

$mapYaml = @"
image: event_fair_map.pgm
resolution: 0.050000
origin: [-7.000000, -7.000000, 0.000000]
negate: 0
occupied_thresh: 0.65
free_thresh: 0.196
"@
Set-Content -Path (Join-Path $mapDir "event_fair_map.yaml") -Value $mapYaml -Encoding ASCII

$wallXml = ($allCollisionRects | ForEach-Object { New-BoxXml $_ }) -join "`n"
$markerIncludes = ($markerPlacements | ForEach-Object {
@"
    <include>
      <uri>model://aruco_marker_$($_.Id)</uri>
      <name>aruco_marker_$($_.Id)</name>
      <pose>$(Format-Double $_.X) $(Format-Double $_.Y) $(Format-Double $markerHeight) 0 0 $(Format-Double $_.Yaw)</pose>
    </include>
"@
}) -join "`n"

$worldXml = @"
<?xml version='1.0'?>
<sdf version='1.6'>
  <world name='event_fair_world'>
    <physics type='ode'>
      <real_time_update_rate>1000</real_time_update_rate>
      <max_step_size>0.001</max_step_size>
    </physics>

    <include>
      <uri>model://sun</uri>
    </include>

    <include>
      <uri>model://ground_plane</uri>
    </include>

    <model name='event_fair_building'>
      <static>true</static>
$wallXml
    </model>

$markerIncludes
  </world>
</sdf>
"@
Set-Content -Path (Join-Path $worldDir "event_fair.world") -Value $worldXml -Encoding ASCII

foreach ($marker in $markerPlacements) {
    $modelDir = Join-Path $modelsDir "aruco_marker_$($marker.Id)"
    $textureDir = Join-Path $modelDir "materials\textures"
    $scriptDir = Join-Path $modelDir "materials\scripts"
    New-Item -ItemType Directory -Force -Path $textureDir, $scriptDir | Out-Null

    New-ArucoPng $marker.Id (Join-Path $textureDir "aruco_$($marker.Id).png")

    $modelConfig = @"
<?xml version='1.0'?>
<model>
  <name>aruco_marker_$($marker.Id)</name>
  <version>1.0</version>
  <sdf version='1.6'>model.sdf</sdf>
  <author>
    <name>Event Guide Robot</name>
  </author>
  <description>OpenCV DICT_4X4_50 ArUco marker $($marker.Id) for the simulated event fair.</description>
</model>
"@
    Set-Content -Path (Join-Path $modelDir "model.config") -Value $modelConfig -Encoding ASCII

    $material = @"
material Aruco/Marker$($marker.Id)
{
  technique
  {
    pass
    {
      ambient 1 1 1 1
      diffuse 1 1 1 1
      texture_unit
      {
        texture aruco_$($marker.Id).png
        filtering none
      }
    }
  }
}
"@
    Set-Content -Path (Join-Path $scriptDir "aruco_$($marker.Id).material") -Value $material -Encoding ASCII

    $modelSdf = @"
<?xml version='1.0'?>
<sdf version='1.6'>
  <model name='aruco_marker_$($marker.Id)'>
    <static>true</static>
    <link name='marker_link'>
      <visual name='marker_visual'>
        <geometry>
          <box>
            <size>$(Format-Double $markerSize) 0.02 $(Format-Double $markerSize)</size>
          </box>
        </geometry>
        <material>
          <script>
            <uri>model://aruco_marker_$($marker.Id)/materials/scripts</uri>
            <uri>model://aruco_marker_$($marker.Id)/materials/textures</uri>
            <name>Aruco/Marker$($marker.Id)</name>
          </script>
        </material>
      </visual>
    </link>
  </model>
</sdf>
"@
    Set-Content -Path (Join-Path $modelDir "model.sdf") -Value $modelSdf -Encoding ASCII
}

Write-Host "Generated event fair map, Gazebo world, and ArUco marker models in $PackageRoot"
