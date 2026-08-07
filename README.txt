Sync with RPi 1b+ folder:
~atlas_ws/src/

Rpi status commands:
1.temperature:
sudo vcgencmd measure_temp
2.CPU realtime usage:
htop
3.voltage:
sudo vcgencmd get_throttled
-->return throttled=0x0 => good
-->return 0x50000 or 0x50005 =>Under-voltage