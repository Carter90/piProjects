sed -i '1s/.*/T/' $state
sed -i '1s/.*/F/' $state

sed -i '2s/.*/T/' /home/carter/Dropbox/CISCSClasses/fun/relay/state.txt

sh -c "state=/home/carter/Dropbox/CISCSClasses/fun/relay/state.txt; [ `sed '1q;d' $state` = "T" ] && sed -i '1s/.*/F/' $state || sed -i '1s/.*/T/' $state"
