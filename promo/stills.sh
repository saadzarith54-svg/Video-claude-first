#!/bin/bash
# usage: stills.sh outname t1,t2,...   -> renders 540x960 stills and tiles them (6 per row)
S=/tmp/claude-0/-home-user-Video-claude-first/f41a95c1-7e8c-5335-ad53-34d4f3d7f41e/scratchpad
cd /home/user/Video-claude-first/promo; rm -rf $S/still
NODE_PATH=$(npm root -g) timeout 400 node render.cjs $S/still 540 960 30 "$2" 2>&1 | grep -v "GL Driver"
cd $S/still; ins=""; fl=""; n=0
for t in ${2//,/ }; do f=$(printf "t_%.2f.png" $t); ins="$ins -i $f"; fl="$fl[$n:v]scale=216:-1,drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:text='$t':x=4:y=4:fontsize=16:fontcolor=red:box=1[v$n];"; n=$((n+1)); done
st=""; for i in $(seq 0 $((n-1))); do st="$st[v$i]"; done
cols=6; [ $n -lt 6 ] && cols=$n; rows=$(( (n+cols-1)/cols ))
lay=""; for i in $(seq 0 $((n-1))); do c=$((i%cols)); r=$((i/cols)); lay="$lay|$((c*216))_$((r*384))"; done
ffmpeg -v error -y $ins -filter_complex "$fl${st}xstack=inputs=$n:layout=${lay:1}:fill=black" $S/$1.png
