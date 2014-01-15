#! /bin/bash

#determine if summoner is male of female
#extract most played champions from lolking record

#id number of summoner on lolking na
#have run on 39000000...40650000
#for idnumber in {37000000..39000000}
for idnumber in `ls`
do
#idnumber=`printf "%08d" $idnumber`
#wget "www.lolking.net/summoner/na/$idnumber" 
gender=0
melname=""
femname=""
ranked=""
m1=""; m2=""; m3=""; m4=""; m5=""
f1=""; f2=""; f3=""; f4=""; f5=""
o1=""; o2=""; o3=""; o4=""; o5=""

#get summoner name and make uppercase
sumname=`grep "Full ratings, statistics and LolKing score" $idnumber | cut -d ' ' -f 10 | sed -e 's/\,//' | tr '[a-z]' '[A-Z]'`

#does summoner name contain a male or female name? If not, the name var stays empty.
#prints more than once if it matches more than once, but that only affects the name list, not the sql table.
melname=$(awk -v name=$sumname '{
if (name ~ $1)
print name;
}' vital_files/mnames4500.txt)

femname=$(awk -v name=$sumname '{
if (name ~ $1)
print name;
}' vital_files/fnames4500.txt)

#check if playing ranked
ranked=`grep "Most Played Champions" $idnumber`

if [[ -n $ranked ]]; then
	champarray=(0,0,0,0,0)
        i=0
	#get 5 most played champions
	for item in $( sed -n '/"most_played_champion_chart"/,/Score/ p' $idnumber | grep name  | cut -d : -f 2 | sed -e 's/\"//' -e 's/\"//' -e 's/\,//' -e 's/ //' ); do
        #remove apostrophes from champions
	champarray[$i]=$( echo $item | sed s/"'"//g )
        if [ champarray[$i] == "Lee" ]; then
        echo $idnumber "Lee" >> "output.txt"
        fi
        if [ champarray[$i] == "Kog'Maw" ]; then
        echo $idnumber "Kog'Maw" >> "output.txt"
        fi   
        let "i++"
        done
        #if name is gendered, write to appropriate list and write champions to variables
	if [[ -n "$femname" ]]
        then echo $femname >> "rankedfemnamelist.txt"
        f1=${champarray[0]}
        f2=${champarray[1]}
        f3=${champarray[2]}
        f4=${champarray[3]}
        f5=${champarray[4]}
        gender="f"
        elif [ -n "$melname"  -a  "$gender" != "f" ]
	then echo $melname >> "rankedmelnamelist.txt"
	m1=${champarray[0]}
        m2=${champarray[1]}
        m3=${champarray[2]}
        m4=${champarray[3]}
        m5=${champarray[4]}
	else
	o1=${champarray[0]}
       	o2=${champarray[1]}
       	o3=${champarray[2]}
       	o4=${champarray[3]}
       	o5=${champarray[4]}
	fi
else
	#if name is gendered, write to appropriate list
        if [[ -n "$melname" ]]
        then echo $melname >> "unrankedmelnamelist.txt"
       	fi
        if [[ -n "$femname" ]]
        then echo $femname >> "unrankedfemnamelist.txt"
       	fi	
fi

#if any numbers have resulted from this pass, put them into the sql database
#don't want to open SQL a million times, so write a file of update commands
#don't care how many update commands there are
if [[ -n "$o1" ]]; then
echo "update champion set o_1=o_1+1 where name='"${champarray[0]}"';"   >> tablefiller.sql
fi
if [[ -n "$o2" ]]; then
echo "update champion set o_2=o_2+1 where name='"${champarray[1]}"';"   >> tablefiller.sql
fi
if [[ -n "$o3" ]]; then
echo "update champion set o_3=o_3+1 where name='"${champarray[2]}"';"   >> tablefiller.sql
fi
if [[ -n "$o4" ]]; then
echo "update champion set o_4=o_4+1 where name='"${champarray[3]}"';"   >> tablefiller.sql
fi
if [[ -n "$o5" ]]; then
echo "update champion set o_5=o_5+1 where name='"${champarray[4]}"';"   >> tablefiller.sql
fi
if [[ -n "$m1" ]]; then
echo "update champion set m_1=m_1+1 where name='"${champarray[0]}"';"   >> tablefiller.sql
fi
if [[ -n "$m2" ]]; then
echo "update champion set m_2=m_2+1 where name='"${champarray[1]}"';"   >> tablefiller.sql
fi
if [[ -n "$m3" ]]; then
echo "update champion set m_3=m_3+1 where name='"${champarray[2]}"';"   >> tablefiller.sql
fi
if [[ -n "$m4" ]]; then
echo "update champion set m_4=m_4+1 where name='"${champarray[3]}"';"   >> tablefiller.sql
fi
if [[ -n "$m5" ]]; then
echo "update champion set m_5=m_5+1 where name='"${champarray[4]}"';"   >> tablefiller.sql
fi
if [[ -n "$f1" ]]; then
echo "update champion set f_1=f_1+1 where name='"${champarray[0]}"';"   >> tablefiller.sql
fi
if [[ -n "$f2" ]]; then
echo "update champion set f_2=f_2+1 where name='"${champarray[1]}"';"   >> tablefiller.sql
fi
if [[ -n "$f3" ]]; then
echo "update champion set f_3=f_3+1 where name='"${champarray[2]}"';"   >> tablefiller.sql
fi
if [[ -n "$f4" ]]; then
echo "update champion set f_4=f_4+1 where name='"${champarray[3]}"';"   >> tablefiller.sql
fi
if [[ -n "$f5" ]]; then
echo "update champion set f_5=f_5+1 where name='"${champarray[4]}"';"   >> tablefiller.sql
fi

done
