# Win11 声音显示静音、点了没反应 —— 一键修复

## 用法

1. 把本文件夹里的 `fix-audio.bat` 和 `fix-audio.ps1` 两个文件拷到有问题的电脑上，放在**同一个文件夹**里。
2. 双击 `fix-audio.bat`，弹出“是否允许更改”时点 **是**。
3. 等它跑完，听到“叮”的提示音就说明好了。

## 脚本做了什么

| 步骤 | 内容 |
| --- | --- |
| 1 | 把 Windows Audio / Windows Audio Endpoint Builder 服务设为自动并重启（喇叭点了没反应，九成是这个服务卡死或被禁用） |
| 2 | 重新启用被禁用的声卡 / 播放设备 |
| 3 | 重新扫描硬件 |
| 4 | 取消所有播放设备的静音，音量低于 5% 的调到 50% |
| 5 | 如果一个播放设备都没有，询问是否卸载声卡后让 Windows 自动重装驱动 |

## 不想下载文件？手动一行命令

右键开始按钮 → **终端(管理员)**，粘贴回车：

```powershell
Set-Service AudioEndpointBuilder -StartupType Automatic; Set-Service Audiosrv -StartupType Automatic; Restart-Service AudioEndpointBuilder -Force; Start-Service Audiosrv
```

## 还是不行

- 到电脑品牌官网下载对应型号的音频驱动安装；
- 设置 → Windows 更新 → 高级选项 → 可选更新，安装音频驱动；
- 设置 → 系统 → 声音 → 疑难解答。
