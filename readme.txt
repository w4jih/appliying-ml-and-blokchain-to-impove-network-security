get nsl-kdd.csv 
then run convert2.py
run the topo.py
then run extarct or extract_Dos with python3 extarct.py s2-eth1 
run hping3 command in mininet CLI h1 hping3 --flood -S -p 80 h2
then run predict_Dos2.py "you will get labled data normal and malicous"