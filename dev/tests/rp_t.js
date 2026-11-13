const {rpList,rpCal}=require("./rparse.js");
const row=`Roster
Legend
DUTY
FLIGHT TIME: 8H 45M
12 Nov 26, Thu
12:50 Z
12:50 LT
STN
CHECK IN
13:35 Z
13:35 LT
STN
FR2812
9HQAG
LPA
18:00 Z
18:00 LT
18:35 Z
18:35 LT
LPA
FR2811
9HQAG
STN
22:55 Z
22:55 LT
23:25 Z
23:25 LT
STN
CHECK OUT
More Actions...
DUTY
FLIGHT TIME: 5H 40M
13 Nov 26, Fri
15:25 Z
15:25 LT
STN
CHECK IN
16:10 Z
16:10 LT
STN
FR1882
EIEKL
LIS
19:00 Z
19:00 LT
19:25 Z
19:25 LT
LIS
FR1883
EIEKL
STN
22:15 Z
22:15 LT
22:45 Z
22:45 LT
STN
CHECK OUT
More Actions...`;
const col=`DUTY FLIGHT TIME: 8H 45M
12 Nov 26, Thu
12:50 Z
12:50 LT
13:35 Z
13:35 LT
18:35 Z
18:35 LT
23:25 Z
23:25 LT
STN
STN
LPA
STN
FR2812 9HQAG
FR2811 9HQAG
CHECK IN
LPA
18:00 Z
18:00 LT
STN
22:55 Z
22:55 LT
CHECK OUT`;
console.log(JSON.stringify(rpList(row),null,0));
console.log(JSON.stringify(rpList(col),null,0));
const cal=`Calendar Legend
November 2026 Flight time: 63h 1m
Mon Tue Wed Thu Fri Sat Sun
1
OFF
2 3 4 5 6 7 8
VTO HSBY HSBY HSBY 2 OFF OFF
9 10 11 12 13 14 15
OFF 2 HSBY 2 2 2 OFF
16 17 18 19 20 21 22
OFF OFF HSBY TRNG 4 HSBY 2
23 24 25 26 27 28 29
OFF OFF OFF 4 HSBY 4 2
30
L
December 2026
Mon Tue Wed Thu Fri Sat Sun
1 2 3 4 5 6
OFF OFF OFF L L L
7 8 9 10 11 12 13
L L OFF OFF OFF DUTY DUTY`;
console.log(rpCal(cal).map(e=>e.date.slice(5)+":"+e.kind+(e.n?e.n:"")).join(" "));
const cell=`November 2026
1 OFF 2 VTO 3 HSBY 4 HSBY 5 HSBY 6 2 7 OFF 8 OFF 9 OFF 10 2 11 HSBY 12 2`;
console.log(rpCal(cell).map(e=>e.date.slice(5)+":"+e.kind).join(" "));
