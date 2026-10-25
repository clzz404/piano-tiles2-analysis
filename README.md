# 钢琴块 2：体力、金币与钻石数据调查

本记录基于 `com.cmplay.tiles2_newest` 版本 `3.1.1.1220`（versionCode `30101221`）的已安装 APK、Android 16 设备和应用数据备份。目标设备未 root，应用不可调试。以下结果只在该版本、该设备上验证。

## 实测结果

| 项目 | 初始值 | 修改后 | 重新启动应用后 |
|---|---:|---:|---:|
| 体力 | 15 | 9999 | 9999 |
| 金币 | 266 | 9999 | 9999 |
| 钻石 | 12 | 9999 | 9999 |

游戏等级在整个验证过程保持 6 级。未测试跨设备登录或长期服务器同步后的状态。

## 数据在哪里

- **体力：** 应用私有目录 `shared_prefs/Cocos2dxPrefsFile.xml` 中的整数 `CurHP`。修改备份中的该字段并恢复后，界面直接显示新值。
- **金币：** 私有目录 `files/proofgold` 曾包含与金币相同的明文数字，但单独把它从 266 改成 9999 后，文件保持 9999、界面仍显示 266。它不是界面余额的权威输入。偏好设置中有不透明的 `Gold` 封装值，另有不透明的 `files/piano_tiles2.db`；本调查未证明金币主值落在哪一个文件或远端字段。
- **钻石：** `files/diamondlog.txt` 记录了余额与 `DiamondHandler` 的远端返回；日志不是余额源。当前可读备份里未找到明文钻石余额字段。
- **规则配置：** `life.csv` 定义体力上限和恢复间隔，`gold.csv` 等 CSV 定义奖励规则；这些表不是当前余额。

## 可用的游戏内部更新入口

APK 声明了导出的广播接收器 `com.cmplay.webview.broadcast.GameBroadcast`，action 为 `com.cmplay.webview.broadcast.gamebroadcast`。它读取两个 extra：

- `send_prize_boolean=true`
- `send_prize_number`：JSON 字符串，包含整数 `type` 与 `num`

DEX 中 `GameBroadcast.sendGamePrize` 将这两个数字交给 `NativeUtil.halloweenCallback(int,int)`。ARM64 原生分支显示 `type=2` 进入金币更新路径，`type=1` 进入钻石更新路径。小额验证分别得到金币 `266→267`、钻石 `12→13`；补加差额后均到 9999，并在应用重启后保留。可用 [tools/send_reward.py](tools/send_reward.py) 在自己的已授权设备上复现广播调用。脚本默认只接受正数，运行前应先确认当前余额以计算差额。

```powershell
python tools/send_reward.py --type gold --amount 1 --serial <设备序列号>
python tools/send_reward.py --type diamond --amount 1 --serial <设备序列号>
```

## 备份恢复注意点

Android 备份格式的 tar 流不能随意用 GNU tar 重新打包。本次第一次重打包加入了 GNU 长文件名记录，Android 恢复日志报 `Unknown tar entity type: 76`；恢复程序在报错前已清空应用数据。原始备份随后成功恢复。最终体力修改采用原位补丁：保留 tar 记录顺序和其他成员字节，只更新 `CurHP` 所在数据块、该成员长度和 tar 头校验和。操作前必须保留可恢复的原始备份，并在恢复后核对等级与其他余额。

原始备份、账号标识、设备序列号、APK、私有数据库、完整日志和 REA 证据包均未纳入本仓库。
