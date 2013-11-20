TOPICS='ads
analytics
audio
credits
crypto
display
easing
facebook
gameNetwork
global
graphics
index.markdown
io
json
lfs
licensing
math
media
native
network
os
package
physics
socket
sprite
sqlite3
store
storyboard
string
system
table
timer
transition
widget'

for T in $TOPICS
do
	echo "$T: \c"
	fgrep -c "${T}." raw-api-definitions-daily
done
