raspivid -w 1280 -h 720 -fps 24 -rot 180  -t 30000 -o $1.h264
MP4Box -fps 24 -add $1.h264 $1.mp4
scp  -oPort=31392 $1.mp4 ProjectCuracao@www2.wardner.com:~


