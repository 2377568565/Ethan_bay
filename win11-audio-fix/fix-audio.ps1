# Win11 声音静音 / 点了没反应 一键修复脚本
# 用法: 双击同目录下的 "fix-audio.bat"（会自动请求管理员权限）

$ErrorActionPreference = 'Continue'
try { [Console]::OutputEncoding = [Text.Encoding]::UTF8 } catch {}

function Write-Step($msg) { Write-Host "`n==> $msg" -ForegroundColor Cyan }
function Write-Ok($msg)   { Write-Host "    [OK] $msg" -ForegroundColor Green }
function Write-Bad($msg)  { Write-Host "    [!]  $msg" -ForegroundColor Yellow }

$principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Bad '需要管理员权限：请双击 "fix-audio.bat"，或右键 PowerShell -> 以管理员身份运行。'
    exit 1
}

# ---------------------------------------------------------------------------
# Core Audio 接口：用来取消静音、调整音量
# ---------------------------------------------------------------------------
if (-not ('AudioFix.Fixer' -as [type])) {
    Add-Type -TypeDefinition @'
using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;

namespace AudioFix {
    [ComImport, Guid("5CDF2C82-841E-4546-9722-0CF74078229A"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    public interface IAudioEndpointVolume {
        [PreserveSig] int RegisterControlChangeNotify(IntPtr pNotify);
        [PreserveSig] int UnregisterControlChangeNotify(IntPtr pNotify);
        [PreserveSig] int GetChannelCount(out uint count);
        [PreserveSig] int SetMasterVolumeLevel(float levelDB, IntPtr ctx);
        [PreserveSig] int SetMasterVolumeLevelScalar(float level, IntPtr ctx);
        [PreserveSig] int GetMasterVolumeLevel(out float levelDB);
        [PreserveSig] int GetMasterVolumeLevelScalar(out float level);
        [PreserveSig] int SetChannelVolumeLevel(uint channel, float levelDB, IntPtr ctx);
        [PreserveSig] int SetChannelVolumeLevelScalar(uint channel, float level, IntPtr ctx);
        [PreserveSig] int GetChannelVolumeLevel(uint channel, out float levelDB);
        [PreserveSig] int GetChannelVolumeLevelScalar(uint channel, out float level);
        [PreserveSig] int SetMute([MarshalAs(UnmanagedType.Bool)] bool mute, IntPtr ctx);
        [PreserveSig] int GetMute([MarshalAs(UnmanagedType.Bool)] out bool mute);
    }

    [ComImport, Guid("D666063F-1587-4E43-81F1-B948E807363F"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    public interface IMMDevice {
        [PreserveSig] int Activate(ref Guid iid, int clsCtx, IntPtr activationParams, [MarshalAs(UnmanagedType.IUnknown)] out object ppInterface);
        [PreserveSig] int OpenPropertyStore(int access, out IntPtr ppProperties);
        [PreserveSig] int GetId([MarshalAs(UnmanagedType.LPWStr)] out string id);
        [PreserveSig] int GetState(out int state);
    }

    [ComImport, Guid("0BD7A1BE-7A1A-44DB-8397-CC5392387B5E"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    public interface IMMDeviceCollection {
        [PreserveSig] int GetCount(out uint count);
        [PreserveSig] int Item(uint index, out IMMDevice device);
    }

    [ComImport, Guid("A95664D2-9614-4F35-A746-DE8DB63617E6"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    public interface IMMDeviceEnumerator {
        [PreserveSig] int EnumAudioEndpoints(int dataFlow, int stateMask, out IMMDeviceCollection devices);
        [PreserveSig] int GetDefaultAudioEndpoint(int dataFlow, int role, out IMMDevice endpoint);
    }

    [ComImport, Guid("BCDE0395-E52F-467C-8E3D-C4579291692E")]
    public class MMDeviceEnumerator {}

    public class EndpointInfo {
        public string Id;
        public bool IsDefault;
        public bool WasMuted;
        public float VolumeBefore;
        public float VolumeAfter;
        public string Error;
    }

    public static class Fixer {
        const int eRender = 0;
        const int eMultimedia = 1;
        const int DEVICE_STATE_ACTIVE = 1;
        const int CLSCTX_ALL = 23;

        public static string GetDefaultId() {
            var en = (IMMDeviceEnumerator)new MMDeviceEnumerator();
            IMMDevice dev;
            if (en.GetDefaultAudioEndpoint(eRender, eMultimedia, out dev) != 0 || dev == null) return null;
            string id;
            dev.GetId(out id);
            return id;
        }

        // 取消所有“已启用”的播放设备的静音；音量低于 minVolume 时调到 setVolume
        public static EndpointInfo[] UnmuteAll(float minVolume, float setVolume) {
            var result = new List<EndpointInfo>();
            var en = (IMMDeviceEnumerator)new MMDeviceEnumerator();
            string defId = GetDefaultId();
            IMMDeviceCollection col;
            Marshal.ThrowExceptionForHR(en.EnumAudioEndpoints(eRender, DEVICE_STATE_ACTIVE, out col));
            uint count;
            col.GetCount(out count);
            Guid iid = typeof(IAudioEndpointVolume).GUID;
            for (uint i = 0; i < count; i++) {
                var info = new EndpointInfo();
                try {
                    IMMDevice dev;
                    Marshal.ThrowExceptionForHR(col.Item(i, out dev));
                    dev.GetId(out info.Id);
                    info.IsDefault = (info.Id == defId);
                    object o;
                    Marshal.ThrowExceptionForHR(dev.Activate(ref iid, CLSCTX_ALL, IntPtr.Zero, out o));
                    var vol = (IAudioEndpointVolume)o;
                    bool muted;
                    vol.GetMute(out muted);
                    info.WasMuted = muted;
                    float v;
                    vol.GetMasterVolumeLevelScalar(out v);
                    info.VolumeBefore = v;
                    Marshal.ThrowExceptionForHR(vol.SetMute(false, IntPtr.Zero));
                    if (v < minVolume) Marshal.ThrowExceptionForHR(vol.SetMasterVolumeLevelScalar(setVolume, IntPtr.Zero));
                    vol.GetMasterVolumeLevelScalar(out v);
                    info.VolumeAfter = v;
                } catch (Exception ex) {
                    info.Error = ex.Message;
                }
                result.Add(info);
            }
            return result.ToArray();
        }
    }
}
'@
}

function Get-EndpointNames {
    # MMDevice Id 形如 {0.0.0.00000000}.{guid}，对应 PnP 实例 SWD\MMDEVAPI\{0.0.0.00000000}.{guid}
    $map = @{}
    Get-PnpDevice -Class AudioEndpoint -ErrorAction SilentlyContinue | ForEach-Object {
        $id = ($_.InstanceId -replace '^SWD\\MMDEVAPI\\', '').ToLower()
        $map[$id] = $_.FriendlyName
    }
    return $map
}

function Invoke-Unmute {
    $names = Get-EndpointNames
    try {
        $eps = [AudioFix.Fixer]::UnmuteAll(0.05, 0.5)
    } catch {
        Write-Bad "无法访问音频设备：$($_.Exception.Message)"
        return 0
    }
    foreach ($e in $eps) {
        $name = $names[("$($e.Id)").ToLower()]
        if (-not $name) { $name = $e.Id }
        $tag = if ($e.IsDefault) { '(默认)' } else { '' }
        if ($e.Error) {
            Write-Bad "$name$tag 处理失败：$($e.Error)"
        } else {
            $before = [math]::Round($e.VolumeBefore * 100)
            $after  = [math]::Round($e.VolumeAfter * 100)
            $mute   = if ($e.WasMuted) { '已取消静音' } else { '未静音' }
            Write-Ok "$name$tag  $mute，音量 $before% -> $after%"
        }
    }
    return @($eps).Count
}

# ---------------------------------------------------------------------------
Write-Step '1/5 修复 Windows 音频服务（最常见原因：服务卡死/被禁用，点喇叭就没反应）'
foreach ($svc in 'AudioEndpointBuilder', 'Audiosrv') {
    try {
        Set-Service -Name $svc -StartupType Automatic -ErrorAction Stop
    } catch {
        sc.exe config $svc start= auto | Out-Null
    }
}
try {
    # 重启 AudioEndpointBuilder 会连带停止 Audiosrv，之后再把两个都拉起来
    Restart-Service -Name AudioEndpointBuilder -Force -ErrorAction Stop
} catch {
    Write-Bad "重启 AudioEndpointBuilder 失败：$($_.Exception.Message)"
}
foreach ($svc in 'AudioEndpointBuilder', 'Audiosrv') {
    try { Start-Service -Name $svc -ErrorAction Stop } catch {}
    $s = Get-Service -Name $svc -ErrorAction SilentlyContinue
    if ($s -and $s.Status -eq 'Running') { Write-Ok "$($s.DisplayName) 正在运行" }
    else { Write-Bad "$svc 没有运行起来（状态：$($s.Status)）" }
}

# ---------------------------------------------------------------------------
Write-Step '2/5 启用被禁用 / 出错的声卡和播放设备'
$devs = Get-PnpDevice -PresentOnly -ErrorAction SilentlyContinue |
    Where-Object { ($_.Class -eq 'MEDIA') -or ($_.Class -eq 'AudioEndpoint') }
$found = $false
foreach ($d in $devs) {
    if ($d.ConfigManagerErrorCode -eq 22) {
        # 22 = CM_PROB_DISABLED：设备被手动禁用了
        $found = $true
        try {
            Enable-PnpDevice -InstanceId $d.InstanceId -Confirm:$false -ErrorAction Stop
            Write-Ok "已重新启用：$($d.FriendlyName)"
        } catch {
            Write-Bad "无法启用 $($d.FriendlyName)：$($_.Exception.Message)"
        }
    } elseif ($d.Class -eq 'MEDIA' -and $d.Status -ne 'OK') {
        $found = $true
        Write-Bad "声卡异常：$($d.FriendlyName)（错误代码 $($d.ConfigManagerErrorCode)），稍后可尝试重装驱动"
    }
}
if (-not $found) { Write-Ok '没有发现被禁用或出错的音频设备' }

# ---------------------------------------------------------------------------
Write-Step '3/5 重新扫描硬件'
pnputil.exe /scan-devices | Out-Null
Start-Sleep -Seconds 3
Write-Ok '扫描完成'

# ---------------------------------------------------------------------------
Write-Step '4/5 取消静音并恢复音量'
$count = Invoke-Unmute

# ---------------------------------------------------------------------------
if ($count -eq 0) {
    Write-Step '5/5 没有找到可用的播放设备 —— 很可能是声卡驱动坏了'
    Write-Host '    可以让脚本卸载声卡设备再重新扫描，Windows 会自动重新安装驱动（不会删除驱动文件）。'
    $ans = Read-Host '    是否尝试重装声卡驱动？输入 y 回车确认，直接回车跳过'
    if ($ans -match '^[yY]') {
        $media = Get-PnpDevice -Class MEDIA -PresentOnly -ErrorAction SilentlyContinue
        foreach ($d in $media) {
            pnputil.exe /remove-device "$($d.InstanceId)" | Out-Null
            Write-Ok "已卸载：$($d.FriendlyName)"
        }
        pnputil.exe /scan-devices | Out-Null
        Write-Host '    等待驱动重新安装...'
        Start-Sleep -Seconds 10
        Restart-Service -Name AudioEndpointBuilder -Force -ErrorAction SilentlyContinue
        Start-Service -Name Audiosrv -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 3
        $count = Invoke-Unmute
    }
} else {
    Write-Step '5/5 播放测试音'
}

if ($count -gt 0) {
    try {
        $wav = Join-Path $env:WINDIR 'Media\Windows Notify System Generic.wav'
        if (Test-Path $wav) { (New-Object Media.SoundPlayer $wav).PlaySync() }
        else { [System.Media.SystemSounds]::Asterisk.Play() }
    } catch {}
    Write-Host "`n修复完成！如果刚才听到了提示音，就说明声音已经恢复。" -ForegroundColor Green
    Write-Host '如果右下角喇叭图标还显示静音，注销或重启一次电脑即可刷新。'
} else {
    Write-Host "`n仍然没有可用的播放设备。请按下面的顺序检查：" -ForegroundColor Yellow
    Write-Host '  1. 耳机/音箱是否插好；外接显示器的话，喇叭可能走的是 HDMI'
    Write-Host '  2. 到电脑品牌官网（联想/戴尔/惠普/华硕等）下载并安装对应型号的“音频驱动”'
    Write-Host '  3. 设置 -> Windows 更新 -> 高级选项 -> 可选更新 里安装音频相关驱动'
    Write-Host '  4. 设置 -> 系统 -> 声音 -> 疑难解答'
}
